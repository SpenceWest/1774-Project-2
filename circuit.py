from Bus import Bus
from TransmissionLine import TransmissionLine
from Generator import Generator
from Load import Load
from Transformer import Transformer
from Settings import Settings
import numpy as np
import pandas as pd
import math



class Circuit:
    def __init__(self, name: str, base_mva: float = 100.0):
        self.name = name
        self.base_mva = base_mva  # Added base MVA for per-unit calculations
        self.buses = {}
        self.transformers = {}
        self.transmission_lines = {}
        self.loads = {}
        self.generators = {}
        self.ybus = None

    def add_bus(self, bus_name: str, nominal_kv: float, bus_type: str = "PQ"):
        """Added bus_type to align with Milestone 6 requirements."""
        new_bus = Bus(bus_name, nominal_kv, bus_type)
        self.buses[bus_name] = new_bus

    def add_transmission_line(self, name: str, bus1_name: str, bus2_name: str, r: float, x: float, g: float, b: float):
        new_transmission_line = TransmissionLine(name, bus1_name, bus2_name, r, x, g, b)
        self.transmission_lines[name] = new_transmission_line

    def add_load_element(self, name: str, bus_name: str, mw: float, mvar: float):
        new_load = Load(name, bus_name, mw, mvar)
        self.loads[name] = new_load
        # Automatically attach the load to the respective Bus object
        if bus_name in self.buses:
            self.buses[bus_name].add_load(new_load)
        else:
            print(f"Warning: Bus '{bus_name}' not found. Load '{name}' not attached to a bus.")

    def add_generator(self, name: str, bus1_name: str, voltage_setpoint: float, mw_setpoint: float, x_subtransient: float = 0.0):
        if name in self.generators:
            raise ValueError(f"Generator with name '{name}' already exists.")

        new_generator = Generator(name, bus1_name, voltage_setpoint, mw_setpoint, x_subtransient=x_subtransient)
        self.generators[name] = new_generator
        # Automatically attach the generator to the respective Bus object
        if bus1_name in self.buses:
            self.buses[bus1_name].add_generator(new_generator)
            # Set the bus voltage to the generator's setpoint if it's a PV or Slack bus
            if self.buses[bus1_name].bus_type in ["PV", "Slack"]:
                self.buses[bus1_name].vpu = voltage_setpoint
        else:
            print(f"Warning: Bus '{bus1_name}' not found. Generator '{name}' not attached to a bus.")


    def add_transformer(self, name: str, bus1_name: str, bus2_name: str, r: float, x: float):
        if name in self.transformers:
            raise ValueError(f"Transformer with name '{name}' already exists.")

        new_transformer = Transformer(name, bus1_name, bus2_name, r, x)
        self.transformers[name] = new_transformer

    def compute_power_mismatch(self):
        """
        Computes the mismatch vector 'f' for the current system state.
        Iterates over all buses and applies formulas based on bus type.
        """
        if self.ybus is None:
            raise ValueError("Ybus has not been calculated yet. Call calc_ybus() first.")

        deltaQ_list = []
        deltaP_list = []

        for bus_name, bus in self.buses.items():
            # Slack bus: No mismatch calculation required
            if bus.bus_type == "Slack":
                continue

            # Get specified values (P_spec, Q_spec)
            p_spec, q_spec = bus.get_specified_pq()

            # Get calculated values (P_calc, Q_calc)
            p_calc, q_calc = self.compute_power_injection(bus_name)

            # Real Power Mismatch (delta_P)
            delta_p = p_spec - p_calc
            deltaP_list.append(delta_p)

            # Reactive Power Mismatch (delta_Q) - Only for PQ buses
            if bus.bus_type == "PQ":
                delta_q = q_spec - q_calc
                deltaQ_list.append(delta_q)

        # Return as a numpy array for numerical solver compatibility
        f = np.array(deltaP_list + deltaQ_list, dtype=float)
        return f

    def calc_ybus(self):
        N = len(self.buses.keys())
        y_matrix = pd.DataFrame(np.zeros((N, N)), dtype=complex, index=list(self.buses.keys()),
                                columns=list(self.buses.keys()))

        for key in self.transmission_lines.keys():
            y_prim = self.transmission_lines[key].calc_yprim()
            b1 = self.transmission_lines[key].bus1_name
            b2 = self.transmission_lines[key].bus2_name

            y_matrix.loc[b1, b1] += y_prim.loc[b1, b1]
            y_matrix.loc[b1, b2] += y_prim.loc[b1, b2]
            y_matrix.loc[b2, b1] += y_prim.loc[b2, b1]
            y_matrix.loc[b2, b2] += y_prim.loc[b2, b2]

        for key in self.transformers.keys():
            y_prim = self.transformers[key].calc_yprim()
            b1 = self.transformers[key].bus1_name
            b2 = self.transformers[key].bus2_name

            y_matrix.loc[b1, b1] += y_prim.loc[b1, b1]
            y_matrix.loc[b1, b2] += y_prim.loc[b1, b2]
            y_matrix.loc[b2, b1] += y_prim.loc[b2, b1]
            y_matrix.loc[b2, b2] += y_prim.loc[b2, b2]

        self.ybus = y_matrix

    # ==========================================
    # MILESTONE 6: POWER FLOW EQUATIONS
    # ==========================================
    def compute_power_injection(self, i_name: str):
        """
        Calculates the actual power injected into the network at a given bus.
        Uses the Ybus dataframe and current bus voltages/angles.
        """
        if self.ybus is None:
            raise ValueError("Ybus has not been calculated yet. Call calc_ybus() first.")

        bus = self.buses[i_name]
        p_calc = 0.0
        q_calc = 0.0

        vi = bus.vpu
        delta_i = np.deg2rad(bus.delta)

        for j_name, j_bus in self.buses.items():
            vj = j_bus.vpu
            delta_j = np.deg2rad(j_bus.delta)

            # Extract Ybus element using pandas loc
            yij = self.ybus.loc[i_name, j_name]
            gij = yij.real
            bij = yij.imag

            # Phase angle difference
            delta_ij = delta_i - delta_j

            # Eq (2): Real power injection
            p_calc += vj * (gij * np.cos(delta_ij) + bij * np.sin(delta_ij))

            # Eq (3): Reactive power injection
            q_calc += vj * (gij * np.sin(delta_ij) - bij * np.cos(delta_ij))

        p_calc *= vi
        q_calc *= vi

        return p_calc, q_calc


if __name__ == "__main__":
    circuit1 = Circuit("Test Circuit")

    # Modified: Adding bus_type to add_bus based on your latest update
    circuit1.add_bus("Bus 1", 15.0, bus_type="Slack")
    circuit1.add_bus("Bus 2", 345.0, bus_type="PQ")
    circuit1.add_bus("Bus 3", 15.75, bus_type="PV")
    circuit1.add_bus("Bus 4", 345.0, bus_type="PQ")
    circuit1.add_bus("Bus 5", 345.0, bus_type="PQ")

    # Add bus vpu
    circuit1.buses["Bus 1"].vpu = 1
    circuit1.buses["Bus 2"].vpu = 1
    circuit1.buses["Bus 3"].vpu = 1.05
    circuit1.buses["Bus 4"].vpu = 1
    circuit1.buses["Bus 5"].vpu = 1

    # Add bus delta
    circuit1.buses["Bus 1"].delta = 0
    circuit1.buses["Bus 2"].delta = 0
    circuit1.buses["Bus 3"].delta = 0
    circuit1.buses["Bus 4"].delta = 0
    circuit1.buses["Bus 5"].delta = 0

    # Add line components
    circuit1.add_transmission_line("Line 1", "Bus 4", "Bus 2", 0.009, 0.1, 0.0, 1.72)
    circuit1.add_transmission_line("Line 2", "Bus 5", "Bus 2", 0.0045, 0.05, 0.0, 0.88)
    circuit1.add_transmission_line("Line 3", "Bus 5", "Bus 4", 0.00225, 0.025, 0.0, 0.44)

    # Add transformers components
    circuit1.add_transformer("T1", "Bus 1", "Bus 5", 0.0015, 0.02)
    circuit1.add_transformer("T2", "Bus 3", "Bus 4", 0.00075, 0.01)

    # Add generators
    circuit1.add_generator("G1", "Bus 1", 1.00, 278.0)
    circuit1.add_generator("G2", "Bus 3", 1.05, 520.0)

    # Add loads
    circuit1.add_load_element("Load 1", "Bus 2", 800.0, 280.0)
    circuit1.add_load_element("Load 2", "Bus 3", 80.0, 40.0)

    # 1. First calculate Ybus
    circuit1.calc_ybus()
    
    # Optional: Print initial status
    print("\n--- Ybus Matrix ---")
    print(circuit1.ybus)

