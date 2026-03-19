from Bus import Bus
from TransmissionLine import TransmissionLine
from Generator import Generator
from Load import Load
from Transformer import Transformer
from Jacobian import Jacobian # <--- IMPORT MILESTONE 7 CLASS
import numpy as np
import pandas as pd
import math

class Circuit:
    def __init__(self, name: str, base_mva: float = 100.0):
        self.name = name
        self.base_mva = base_mva
        self.buses = {}
        self.transformers = {}
        self.transmission_lines = {}
        self.loads = {}
        self.generators = {}
        self.ybus = None

    def add_bus(self, bus_name: str, nominal_kv: float, bus_type: str = "PQ"):
        new_bus = Bus(bus_name, nominal_kv, bus_type)
        self.buses[bus_name] = new_bus

    def add_transmission_line(self, name: str, bus1_name: str, bus2_name: str, r: float, x: float, g: float, b: float):
        new_transmission_line = TransmissionLine(name, bus1_name, bus2_name, r, x, g, b)
        self.transmission_lines[name] = new_transmission_line

    def add_load_element(self, name: str, bus_name: str, mw: float, mvar: float):
        new_load = Load(name, bus_name, mw, mvar)
        self.loads[name] = new_load
        if bus_name in self.buses:
            self.buses[bus_name].add_load(new_load)

    def add_generator(self, name: str, bus1_name: str, voltage_setpoint: float, mw_setpoint: float):
        if name in self.generators:
            raise ValueError(f"Generator with name '{name}' already exists.")
            
        new_generator = Generator(name, bus1_name, voltage_setpoint, mw_setpoint)
        self.generators[name] = new_generator
        if bus1_name in self.buses:
            self.buses[bus1_name].add_generator(new_generator)
            if self.buses[bus1_name].bus_type in ["PV", "Slack"]:
                self.buses[bus1_name].vpu = voltage_setpoint
        
    def add_transformer(self, name: str, bus1_name: str, bus2_name: str, r: float, x: float):
        if name in self.transformers:
            raise ValueError(f"Transformer with name '{name}' already exists.")
            
        new_transformer = Transformer(name, bus1_name, bus2_name, r, x)
        self.transformers[name] = new_transformer

    def calc_ybus(self):
        N = len(self.buses.keys())
        y_matrix = pd.DataFrame(np.zeros((N, N)), dtype=complex, index=list(self.buses.keys()), columns=list(self.buses.keys()))
        
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
    def compute_power_injection(self, bus_name: str):
        if self.ybus is None:
            raise ValueError("Ybus has not been calculated yet. Call calc_ybus() first.")

        bus = self.buses[bus_name]
        p_calc = 0.0
        q_calc = 0.0
        vi = bus.vpu
        delta_i = bus.delta

        for j_name, j_bus in self.buses.items():
            vj = j_bus.vpu
            delta_j = j_bus.delta
            yij = self.ybus.loc[bus_name, j_name]
            gij = yij.real
            bij = yij.imag
            delta_ij = delta_i - delta_j

            p_calc += vi * vj * (gij * math.cos(delta_ij) + bij * math.sin(delta_ij))
            q_calc += vi * vj * (gij * math.sin(delta_ij) - bij * math.cos(delta_ij))

        return p_calc, q_calc

    def compute_power_mismatch(self):
        if self.ybus is None:
            raise ValueError("Ybus has not been calculated yet. Call calc_ybus() first.")

        mismatches = []
        for bus_name, bus in self.buses.items():
            if bus.bus_type == "Slack":
                continue 
            
            p_spec, q_spec = bus.get_specified_pq(self.base_mva)
            p_calc, q_calc = self.compute_power_injection(bus_name)
            
            delta_p = p_spec - p_calc
            mismatches.append(delta_p)
            
            if bus.bus_type == "PQ":
                delta_q = q_spec - q_calc
                mismatches.append(delta_q) 
                
        f = np.array(mismatches)
        return f

    # ==========================================
    # MILESTONE 7: JACOBIAN MATRIX
    # ==========================================
    def get_jacobian_matrix(self):
        """
        Creates the Jacobian object and returns the full Jacobian matrix
        based on current system voltages and angles.
        """
        if self.ybus is None:
            raise ValueError("Ybus has not been calculated yet. Call calc_ybus() first.")
            
        jacobian_obj = Jacobian(self.buses, self.ybus)
        return jacobian_obj.calc_jacobian()

if __name__ == "__main__":
    circuit1 = Circuit("Test Circuit")

    circuit1.add_bus("Bus 1", 20.0, bus_type="Slack")
    circuit1.add_bus("Bus 2", 230.0, bus_type="PQ")
    circuit1.add_bus("Bus 3", 115.0, bus_type="PV")

    circuit1.add_transmission_line("Line 2", "Bus 2", "Bus 3", 0.02, 0.25, 0.0, 0.04)
    circuit1.add_transformer("T1", "Bus 1", "Bus 2", 0.01, 0.10)
    circuit1.add_generator("G1", "Bus 1", 1.04, 100.0)
    circuit1.add_load_element("Load 1", "Bus 2", 50.0, 30.0)

    # Calculate Ybus
    circuit1.calc_ybus()
    
    # Milestone 6 output
    print("--- Mismatch Vector f (Milestone 6) ---")
    print(circuit1.compute_power_mismatch())

    # Milestone 7 output
    print("\n--- Jacobian Matrix J (Milestone 7) ---")
    J = circuit1.get_jacobian_matrix()
    print(J)
