import numpy as np
import pandas as pd
from Jacobian import Jacobian
from circuit import Circuit
from PowerFlow import PowerFlow
from Bus import Bus
class Solution:

    def solution(self, circuit: Circuit, mode: str = 'powerflow', fault_bus: str = None, v_prefault: float = 1.0) -> dict:

        mode = mode.strip().lower()

        if mode == 'powerflow':
            return self._run_powerflow(circuit)

        elif mode == 'fault':
            if fault_bus is None:
                raise ValueError("fault_bus must be specified when mode='fault'.")
            return self._run_fault(circuit, fault_bus, v_prefault)

        else:
            raise ValueError(f"Unknown mode '{mode}'. Choose 'powerflow' or 'fault'.")

    # ================================================================== #
    #  MODE 1 – Power Flow                                                #
    # ================================================================== #

    def _run_powerflow(self, circuit: Circuit) -> dict:
        """Newton-Raphson PowerFlow solver."""
        if circuit.ybus is None:
            circuit.calc_ybus()

        pf = PowerFlow()
        converged = pf.solve(circuit)

        results = {
            'mode': 'powerflow',
            'converged': converged,
            'bus_results': {}
        }

        for name, bus in circuit.buses.items():
            p_calc, q_calc = circuit.compute_power_injection(name)
            results['bus_results'][name] = {
                'vpu': round(bus.vpu, 6),
                'delta': round(bus.delta, 4),
                'p_calc_pu': round(p_calc, 6),
                'q_calc_pu': round(q_calc, 6),
            }

        self._print_powerflow_results(results)
        return results

    # ================================================================== #
    #  MODE 2 – Symmetrical Fault Study                                   #
    # ================================================================== #

    def _run_fault(self, circuit: Circuit, fault_bus_name: str, v_prefault: float) -> dict:
        """
        Steps
        1. Build the *faulted* Ybus by adding each generator's subtransient
           admittance Y'' = 1/(j X'') as a shunt from its terminal bus to
           the reference (ground).
        2. Invert to obtain Zbus.
        3. Compute subtransient fault current:
               I_F'' = V_F / Z_nn
        4. Compute post-fault bus voltages:
               E_k   = (1 – Z_kn / Z_nn) * V_F
        """

        bus_names = list(circuit.buses.keys())

        if fault_bus_name not in circuit.buses:
            raise ValueError(f"Fault bus '{fault_bus_name}' not found in circuit.")

        # ── Step 1: Build faulted Ybus ─────────────────────────────────
        # Start from a fresh network Ybus (lines + transformers only)
        circuit.calc_ybus()
        y_fault = circuit.ybus.copy()  # DataFrame, complex

        gens_with_xpp = []
        for gen_name, gen in circuit.generators.items():
            if gen.x_subtransient == 0.0:
                print(f"  [WARNING] Generator '{gen_name}' has X''=0; "
                      "skipping its shunt contribution.")
                continue
            y_shunt = gen.calc_y_subtransient()
            bus = gen.bus_name
            y_fault.loc[bus, bus] += y_shunt  # add shunt to diagonal only
            gens_with_xpp.append((gen_name, bus, gen.x_subtransient, y_shunt))

        print("\n─── Faulted Ybus (with generator X'' shunts) ───")
        print(y_fault)

        # ── Step 2: Zbus = Ybus_faulted ⁻¹ ───────────────────────────
        y_array = y_fault.values.astype(complex)
        z_array = np.linalg.inv(y_array)
        zbus = pd.DataFrame(z_array, index=bus_names, columns=bus_names)

        print("\n─── Zbus ───")
        print(zbus)

        # ── Step 3: Fault current at fault bus n ──────────────────────
        z_nn = zbus.loc[fault_bus_name, fault_bus_name]
        i_fault = v_prefault / z_nn  # I_F'' = V_F / Z_nn  (complex pu)

        # ── Step 4: Post-fault bus voltages ───────────────────────────
        bus_voltages = {}
        for k_name in bus_names:
            z_kn = zbus.loc[k_name, fault_bus_name]
            e_k = (1.0 - z_kn / z_nn) * v_prefault
            bus_voltages[k_name] = e_k

        # ── Collect and print results ──────────────────────────────────
        results = {
            'mode': 'fault',
            'fault_bus': fault_bus_name,
            'v_prefault_pu': v_prefault,
            'z_nn': z_nn,
            'i_fault_pu': i_fault,
            'bus_voltages': bus_voltages,
            'zbus': zbus,
        }

        self._print_fault_results(results)
        return results

    @staticmethod
    def _print_powerflow_results(results: dict):
        print("\n" + "=" * 55)
        print("  POWER FLOW SOLUTION")
        print("=" * 55)
        conv = "YES" if results['converged'] else "NO"
        print(f"  Converged : {conv}\n")
        print(f"  {'Bus':<12} {'|V| (pu)':>10} {'δ (deg)':>10} "
              f"{'P_calc (pu)':>13} {'Q_calc (pu)':>13}")
        print("  " + "-" * 53)
        for name, r in results['bus_results'].items():
            print(f"  {name:<12} {r['vpu']:>10.5f} {r['delta']:>10.4f} "
                  f"{r['p_calc_pu']:>13.5f} {r['q_calc_pu']:>13.5f}")
        print("=" * 55)

    @staticmethod
    def _print_fault_results(results: dict):
        print("\n" + "=" * 55)
        print("  SYMMETRICAL FAULT STUDY RESULTS")
        print("=" * 55)
        print(f"  Fault bus      : {results['fault_bus']}")
        print(f"  Pre-fault V_F  : {results['v_prefault_pu']} pu")
        print(f"  Z_nn           : {results['z_nn']:.5f} pu")
        print(f"  I_fault''      : {results['i_fault_pu']:.5f} pu")
        print(f"  |I_fault''|    : {abs(results['i_fault_pu']):.5f} pu\n")
        print(f"  {'Bus':<14} {'E_k (pu, complex)':>28}  {'|E_k|':>8}")
        print("  " + "-" * 53)
        for bus, ek in results['bus_voltages'].items():
            print(f"  {bus:<14} {str(ek):>28}  {abs(ek):>8.5f}")
        print("=" * 55)




if __name__ == "__main__":
    circuit1 = Circuit("Test Circuit")

    circuit1.add_bus("Bus 1", 15.0, bus_type="Slack")
    circuit1.add_bus("Bus 2", 345.0, bus_type="PQ")
    circuit1.add_bus("Bus 3", 15.75, bus_type="PV")
    circuit1.add_bus("Bus 4", 345.0, bus_type="PQ")
    circuit1.add_bus("Bus 5", 345.0, bus_type="PQ")

    circuit1.buses["Bus 1"].vpu = 1.0
    circuit1.buses["Bus 2"].vpu = 1.0
    circuit1.buses["Bus 3"].vpu = 1.05
    circuit1.buses["Bus 4"].vpu = 1.0
    circuit1.buses["Bus 5"].vpu = 1.0

    circuit1.buses["Bus 1"].delta = 0
    circuit1.buses["Bus 2"].delta = 0
    circuit1.buses["Bus 3"].delta = 0
    circuit1.buses["Bus 4"].delta = 0
    circuit1.buses["Bus 5"].delta = 0

    circuit1.add_transmission_line("Line 1", "Bus 4", "Bus 2", 0.009, 0.1, 0.0, 1.72)
    circuit1.add_transmission_line("Line 2", "Bus 5", "Bus 2", 0.0045, 0.05, 0.0, 0.88)
    circuit1.add_transmission_line("Line 3", "Bus 5", "Bus 4", 0.00225, 0.025, 0.0, 0.44)

    circuit1.add_transformer("T1", "Bus 1", "Bus 5", 0.0015, 0.02)
    circuit1.add_transformer("T2", "Bus 3", "Bus 4", 0.00075, 0.01)

    circuit1.add_generator("G1", "Bus 1", voltage_setpoint=1.00, mw_setpoint=278.0, x_subtransient=0.15)
    circuit1.add_generator("G2", "Bus 3", voltage_setpoint=1.05, mw_setpoint=520.0, x_subtransient=0.20)

    circuit1.add_load_element("Load 1", "Bus 2", 800.0, 280.0)
    circuit1.add_load_element("Load 2", "Bus 3", 80.0, 40.0)

    circuit1.calc_ybus()

    solver = Solution()

    # --- Power Flow ---
    print("\n===== Power Flow Mode =====")
    solver.solution(circuit1, mode='powerflow')

    # --- Fault Study (fault at Bus 1) ---
    #print("\n===== Fault Study Mode (fault at Bus 1) =====")
    #solver.solution(circuit1, mode='fault', fault_bus='Bus 3', v_prefault=1.0)




