import numpy as np
import pandas as pd
import math
from circuit import Circuit


class Jacobian:
    """
    The full Jacobian is partitioned into four submatrices:

        J = | J1  J2 |     where:  J1 = dP/d_delta  (non-slack x non-slack)
            | J3  J4 |             J2 = dP/d|V|     (non-slack x PQ-only)
                                   J3 = dQ/d_delta  (PQ-only  x non-slack)
                                   J4 = dQ/d|V|     (PQ-only  x PQ-only)
    """

    def __init__(self, buses, ybus):
        self.buses = buses
        self.ybus = ybus


        self.p_buses = [b for b in self.buses.values() if b.bus_type != "Slack"]
        self.q_buses = [b for b in self.buses.values() if b.bus_type == "PQ"]



    def calc_jacobian(self):
        """
        Assembles and returns the full Jacobian matrix J by stacking the four
        submatrices computed by the private helper methods below.

            J = | J1  J2 |
                | J3  J4 |
        """
        J1 = self._calc_j1()
        J2 = self._calc_j2()
        J3 = self._calc_j3()
        J4 = self._calc_j4()

        # Stack horizontally first, then vertically
        top    = np.hstack((J1, J2))   # [ J1 | J2 ]
        bottom = np.hstack((J3, J4))   # [ J3 | J4 ]
        J      = np.vstack((top, bottom))
        return J



    #     J1: dP/d_delta
    def _calc_j1(self):
        """
        J1 submatrix — partial derivative of real power P with respect to
        voltage angle δ.

          Off-diagonal  (k ≠ n):
              J1_kn = V_k · Y_kn · V_n · sin(δ_k - δ_n - θ_kn)

          Diagonal  (k = n):
              J1_kk = -V_k · Σ_{n≠k} [ Y_kn · V_n · sin(δ_k - δ_n - θ_kn) ]

        Size: (N_non_slack) × (N_non_slack)
        """
        size = len(self.p_buses)
        J1 = np.zeros((size, size))

        for r, bus_k in enumerate(self.p_buses):   # row  → bus k
            for c, bus_n in enumerate(self.p_buses):   # col → bus n

                # Pull admittance Y_kn from the Ybus and convert to polar form
                y_kn  = self.ybus.loc[bus_k.name, bus_n.name]
                Y_mag = abs(y_kn)           # |Y_kn|
                theta = math.atan2(y_kn.imag, y_kn.real)  # θ_kn

                # Angle difference  δ_k - δ_n
                d_kn = np.deg2rad(bus_k.delta - bus_n.delta)

                if r != c:
                    # ── Off-diagonal ──────────────────────────────────────────
                    # J1_kn = V_k · Y_kn · V_n · sin(δ_k - δ_n - θ_kn)
                    J1[r, c] = (bus_k.vpu
                                * Y_mag
                                * bus_n.vpu
                                * math.sin(d_kn - theta))
                else:
                    # ── Diagonal ─────────────────────────────────────────────
                    # J1_kk = -V_k · Σ_{n≠k} [ Y_kn · V_n · sin(δ_k-δ_n-θ_kn) ]
                    # We sum over ALL buses in the system (not just p_buses)
                    # because the Ybus includes connections to every bus.
                    total = 0.0
                    for other_name, other_bus in self.buses.items():
                        if other_name == bus_k.name:
                            continue  # skip n = k term
                        y_kn_full = self.ybus.loc[bus_k.name, other_name]
                        Ym = abs(y_kn_full)
                        th = math.atan2(y_kn_full.imag, y_kn_full.real)
                        d  = np.deg2rad(bus_k.delta - other_bus.delta)
                        total += Ym * other_bus.vpu * math.sin(d - th)

                    J1[r, c] = -bus_k.vpu * total

        return J1

    # ── J2: dP/d|V| ───────────────────────────────────────────────────────────
    def _calc_j2(self):
        """
        J2 submatrix — partial derivative of real power P with respect to
        voltage magnitude |V|.

          Off-diagonal  (k ≠ n):
              J2_kn = V_k · Y_kn · cos(δ_k - δ_n - θ_kn)

          Diagonal  (k = n):
              J2_kk = V_k · Y_kk · cos(θ_kk)
                      + Σ_{n=1}^{N} [ Y_kn · V_n · cos(δ_k - δ_n - θ_kn) ]
              Note: the self-term (n=k) IS included in the summation here.

        Size: (N_non_slack) × (N_PQ)
        """
        rows = len(self.p_buses)
        cols = len(self.q_buses)
        J2 = np.zeros((rows, cols))

        for r, bus_k in enumerate(self.p_buses):    # row → bus k
            for c, bus_n in enumerate(self.q_buses):  # col → bus n (PQ only)

                y_kn  = self.ybus.loc[bus_k.name, bus_n.name]
                Y_mag = abs(y_kn)
                theta = math.atan2(y_kn.imag, y_kn.real)
                d_kn  = np.deg2rad(bus_k.delta - bus_n.delta)

                if bus_k.name != bus_n.name:
                    # ── Off-diagonal ──────────────────────────────────────────
                    # J2_kn = V_k · Y_kn · cos(δ_k - δ_n - θ_kn)
                    J2[r, c] = bus_k.vpu * Y_mag * math.cos(d_kn - theta)
                else:
                    # ── Diagonal ─────────────────────────────────────────────
                    # J2_kk = V_k·Y_kk·cos(θ_kk)
                    #         + Σ_{n=1}^{N} Y_kn·V_n·cos(δ_k-δ_n-θ_kn)
                    #
                    # First term: self-admittance contribution
                    y_kk   = self.ybus.loc[bus_k.name, bus_k.name]
                    Y_kk   = abs(y_kk)
                    th_kk  = math.atan2(y_kk.imag, y_kk.real)
                    first  = bus_k.vpu * Y_kk * math.cos(th_kk)

                    # Second term: sum over ALL buses (including n=k this time)
                    total = 0.0
                    for other_name, other_bus in self.buses.items():
                        y_kn_full = self.ybus.loc[bus_k.name, other_name]
                        Ym = abs(y_kn_full)
                        th = math.atan2(y_kn_full.imag, y_kn_full.real)
                        d  = np.deg2rad(bus_k.delta - other_bus.delta)
                        total += Ym * other_bus.vpu * math.cos(d - th)

                    J2[r, c] = first + total

        return J2

    # ── J3: dQ/d_delta ────────────────────────────────────────────────────────
    def _calc_j3(self):
        """
        J3 submatrix — partial derivative of reactive power Q with respect to
        voltage angle δ.

          Off-diagonal  (k ≠ n):
              J3_kn = -V_k · Y_kn · V_n · cos(δ_k - δ_n - θ_kn)

          Diagonal  (k = n):
              J3_kk = V_k · Σ_{n≠k} [ Y_kn · V_n · cos(δ_k - δ_n - θ_kn) ]

        Size: (N_PQ) × (N_non_slack)
        """
        rows = len(self.q_buses)
        cols = len(self.p_buses)
        J3 = np.zeros((rows, cols))

        for r, bus_k in enumerate(self.q_buses):    # row → bus k (PQ only)
            for c, bus_n in enumerate(self.p_buses):  # col → bus n

                y_kn  = self.ybus.loc[bus_k.name, bus_n.name]
                Y_mag = abs(y_kn)
                theta = math.atan2(y_kn.imag, y_kn.real)
                d_kn  = np.deg2rad(bus_k.delta - bus_n.delta)

                if bus_k.name != bus_n.name:
                    # ── Off-diagonal ──────────────────────────────────────────
                    # J3_kn = -V_k · Y_kn · V_n · cos(δ_k - δ_n - θ_kn)
                    J3[r, c] = (-bus_k.vpu
                                * Y_mag
                                * bus_n.vpu
                                * math.cos(d_kn - theta))
                else:
                    # ── Diagonal ─────────────────────────────────────────────
                    # J3_kk = V_k · Σ_{n≠k} [ Y_kn·V_n·cos(δ_k-δ_n-θ_kn) ]
                    total = 0.0
                    for other_name, other_bus in self.buses.items():
                        if other_name == bus_k.name:
                            continue  # skip n = k
                        y_kn_full = self.ybus.loc[bus_k.name, other_name]
                        Ym = abs(y_kn_full)
                        th = math.atan2(y_kn_full.imag, y_kn_full.real)
                        d  = np.deg2rad(bus_k.delta - other_bus.delta)
                        total += Ym * other_bus.vpu * math.cos(d - th)

                    J3[r, c] = bus_k.vpu * total

        return J3

    # ── J4: dQ/d|V| ───────────────────────────────────────────────────────────
    def _calc_j4(self):
        """
        J4 submatrix — partial derivative of reactive power Q with respect to
        voltage magnitude |V|.

          Off-diagonal  (k ≠ n):
              J4_kn = V_k · Y_kn · sin(δ_k - δ_n - θ_kn)

          Diagonal  (k = n):
              J4_kk = -V_k · Y_kk · sin(θ_kk)
                      + Σ_{n=1}^{N} [ Y_kn · V_n · sin(δ_k - δ_n - θ_kn) ]
              Note: the self-term (n=k) IS included in the summation here.

        Size: (N_PQ) × (N_PQ)
        """
        size = len(self.q_buses)
        J4 = np.zeros((size, size))

        for r, bus_k in enumerate(self.q_buses):    # row → bus k (PQ only)
            for c, bus_n in enumerate(self.q_buses):  # col → bus n (PQ only)

                y_kn  = self.ybus.loc[bus_k.name, bus_n.name]
                Y_mag = abs(y_kn)
                theta = math.atan2(y_kn.imag, y_kn.real)
                d_kn  = np.deg2rad(bus_k.delta - bus_n.delta)

                if r != c:
                    # ── Off-diagonal ──────────────────────────────────────────
                    # J4_kn = V_k · Y_kn · sin(δ_k - δ_n - θ_kn)
                    J4[r, c] = bus_k.vpu * Y_mag * math.sin(d_kn - theta)
                else:
                    # ── Diagonal ─────────────────────────────────────────────
                    # J4_kk = -V_k·Y_kk·sin(θ_kk)
                    #         + Σ_{n=1}^{N} Y_kn·V_n·sin(δ_k-δ_n-θ_kn)
                    #
                    # First term: self-admittance contribution (negative)
                    y_kk   = self.ybus.loc[bus_k.name, bus_k.name]
                    Y_kk   = abs(y_kk)
                    th_kk  = math.atan2(y_kk.imag, y_kk.real)
                    first  = -bus_k.vpu * Y_kk * math.sin(th_kk)

                    # Second term: sum over ALL buses (including n=k)
                    total = 0.0
                    for other_name, other_bus in self.buses.items():
                        y_kn_full = self.ybus.loc[bus_k.name, other_name]
                        Ym = abs(y_kn_full)
                        th = math.atan2(y_kn_full.imag, y_kn_full.real)
                        d  = np.deg2rad(bus_k.delta - other_bus.delta)
                        total += Ym * other_bus.vpu * math.sin(d - th)

                    J4[r, c] = first + total
                    #J4[r, c] = bus_k.bus_index

        return J4


def cmath_phase(z: complex) -> float:
    """Return the phase angle (radians) of a complex number z."""
    return math.atan2(z.imag, z.real)

if __name__ == "__main__":
    circuit1 = Circuit("Test Circuit")

    # Modified: Adding bus_type to add_bus based on Milestone 6 Needs
    circuit1.add_bus("Bus 1", 15.0, bus_type="Slack")
    circuit1.add_bus("Bus 2", 345.0, bus_type="PQ")
    circuit1.add_bus("Bus 3", 15.75, bus_type="PV")
    circuit1.add_bus("Bus 4", 345.0, bus_type="PQ")
    circuit1.add_bus("Bus 5", 345.0, bus_type="PQ")

    # Add bus vpu  of ex powerworld
    circuit1.buses["Bus 1"].vpu = 1
    circuit1.buses["Bus 2"].vpu = 1
    circuit1.buses["Bus 3"].vpu = 1.05
    circuit1.buses["Bus 4"].vpu = 1
    circuit1.buses["Bus 5"].vpu = 1

    # Add bus delta  of ex powerworld
    circuit1.buses["Bus 1"].delta = 0
    circuit1.buses["Bus 2"].delta = 0
    circuit1.buses["Bus 3"].delta = 0
    circuit1.buses["Bus 4"].delta = 0
    circuit1.buses["Bus 5"].delta = 0

    # Add line components of ex powerworld
    circuit1.add_transmission_line("Line 1", "Bus 4", "Bus 2", 0.009, 0.1, 0.0, 1.72)
    circuit1.add_transmission_line("Line 2", "Bus 5", "Bus 2", 0.0045, 0.05, 0.0, 0.88)
    circuit1.add_transmission_line("Line 3", "Bus 5", "Bus 4", 0.00225, 0.025, 0.0, 0.44)

    # Add transformers components of ex powerworld
    circuit1.add_transformer("T1", "Bus 1", "Bus 5", 0.0015, 0.02)
    circuit1.add_transformer("T2", "Bus 3", "Bus 4", 0.00075, 0.01)

    # Add line generator of ex powerworld
    circuit1.add_generator("G1", "Bus 1", 1.00, 278.0)
    circuit1.add_generator("G2", "Bus 3", 1.05, 520.0)

    # Add line load of ex powerworld
    circuit1.add_load_element("Load 1", "Bus 2", 800.0, 280.0)
    circuit1.add_load_element("Load 2", "Bus 3", 80.0, 40.0)

    # 1. First calculate Ybus
    circuit1.calc_ybus()
    print("\n--- Ybus Matrix ---")
    print(circuit1.ybus)

    # 2. Test Milestone 6 Methods
    print("\n--- Milestone 6: Power Mismatch Vector ---")
    mismatch_vector = circuit1.compute_power_mismatch()
    print("Mismatch Vector f:")
    print(mismatch_vector)

    jacobian1 = Jacobian(circuit1.buses, circuit1.ybus)
    jacobian1_matrix = jacobian1.calc_jacobian()

    row_labels = (
            [f"dP / {b.name}" for b in jacobian1.p_buses] +
            [f"dQ / {b.name}" for b in jacobian1.q_buses]
    )
    col_labels = (
            [f"d_delta {b.name}" for b in jacobian1.p_buses] +
            [f"d|V| {b.name}" for b in jacobian1.q_buses]
    )
    df_J = pd.DataFrame(jacobian1_matrix, index=row_labels, columns=col_labels)

    pd.set_option("display.float_format", "{:8.4f}".format)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)  # ← no limit on columns

    print(df_J)