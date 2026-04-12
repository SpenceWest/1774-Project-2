import numpy as np
import pandas as pd
from Jacobian import Jacobian
from circuit import Circuit

class PowerFlow:
    def solve(self, circuit, tol=0.001, max_iter=50):
        """
        circuit  : Circuit object with calc_ybus() already called.
        tol      : Convergence tolerance on max |mismatch| (default 0.001).
        max_iter : Maximum Newton-Raphson iterations (default 50).

        """
        buses = circuit.buses
        ybus  = circuit.ybus

        if ybus is None:
            raise ValueError("Ybus not built — call circuit.calc_ybus() first.")

        # Flat start
        # All angles → 0 rad; PQ bus voltages → 1.0 pu.
        # PV / Slack voltages keep their generator setpoints.
        for bus in buses.values():
            if bus.bus_type != "Slack":
                bus.delta = 0.0
            if bus.bus_type == "PQ":
                bus.vpu = 1.0
                bus.delta = 0.0


        # Ordered bus lists that match Jacobian row/column ordering
        p_buses = [b for b in buses.values() if b.bus_type != "Slack"]  # Δδ vars
        q_buses = [b for b in buses.values() if b.bus_type == "PQ"]     # ΔV vars

        converged = False

        for iteration in range(1, max_iter + 1):

            # Step 1: Power mismatch
            # f = [ΔP (non-slack), ΔQ (PQ-only)]  — built by Circuit
            f = circuit.compute_power_mismatch()

            # Convergence check
            max_mis = np.max(np.abs(f))
            print(f"  Iter {iteration:3d} | max mismatch = {max_mis:.6f}")

            if max_mis < tol:
                converged = True
                print(f"\nConverged in {iteration} iteration(s). "
                      f"Max mismatch = {max_mis:.2e}")

                for bus in circuit.buses.values():
                    print(bus.vpu, bus.delta)

                break

            # Jacobian
            jac = Jacobian(buses, ybus)
            J   = jac.calc_jacobian()

            #  Solve  J · Δx = f
            # numpy.linalg.solve is preferred over explicit inversion
            dx = np.linalg.solve(J, f)

            # Split Δx into angle corrections and voltage corrections
            n_p    = len(p_buses)
            d_delta = dx[:n_p]        # corrections to δ  (non-slack buses)
            d_v     = dx[n_p:]        # corrections to |V| (PQ buses only)

            # Update state variables
            # Slack bus: no update (voltage and angle are fixed references)
            # PV  bus:   update δ only
            # PQ  bus:   update both δ and |V|
            for i, bus in enumerate(p_buses):
                bus.delta += np.rad2deg(d_delta[i])         # all non-slack buses

            for i, bus in enumerate(q_buses):
                bus.vpu += d_v[i]               # PQ buses only

        else:
            # Loop completed without break → did not converge
            print(f"\nWARNING: Newton-Raphson did NOT converge "
                  f"after {max_iter} iterations.")

        return converged


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



    powerflow = PowerFlow()

    powerflow.solve(circuit1)