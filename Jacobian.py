import numpy as np
import pandas as pd
import math
from circuit import Circuit


class Jacobian:
    def __init__(self, buses, ybus):
        self.buses = buses
        self.ybus = ybus
        
        # Determine variable mappings (Exclude Slack for all; Exclude PV for Q and V)
        self.p_buses = [b for b in self.buses.values() if b.bus_type != "Slack"]
        self.q_buses = [b for b in self.buses.values() if b.bus_type == "PQ"]

    def calc_jacobian(self):
        """
        Milestone 7: Constructs the full Jacobian matrix J by calculating
        submatrices J1, J2, J3, and J4.
        """
        J1 = self._calc_j1()
        J2 = self._calc_j2()
        J3 = self._calc_j3()
        J4 = self._calc_j4()

        # Combine the submatrices into the full Jacobian matrix
        # J = [ J1  J2 ]
        #     [ J3  J4 ]
        top_half = np.hstack((J1, J2))
        bottom_half = np.hstack((J3, J4))
        J = np.vstack((top_half, bottom_half))
        
        return J

    def _get_p_q_calc(self, i_bus_name):
        """Helper to compute P_calc and Q_calc for a specific bus."""
        p_calc = 0.0
        q_calc = 0.0
        bus_i = self.buses[i_bus_name]
        
        for j_bus_name, bus_j in self.buses.items():
            yij = self.ybus.loc[i_bus_name, j_bus_name]
            gij, bij = yij.real, yij.imag
            delta_ij = bus_i.delta - bus_j.delta
            
            p_calc += bus_i.vpu * bus_j.vpu * (gij * math.cos(delta_ij) + bij * math.sin(delta_ij))
            q_calc += bus_i.vpu * bus_j.vpu * (gij * math.sin(delta_ij) - bij * math.cos(delta_ij))
            
        return p_calc, q_calc

    def _calc_j1(self):
        """J1 = dP / dDelta (Size: N_non_slack x N_non_slack)"""
        size = len(self.p_buses)
        J1 = np.zeros((size, size))
        
        for r, bus_i in enumerate(self.p_buses):
            for c, bus_j in enumerate(self.p_buses):
                yij = self.ybus.loc[bus_i.name, bus_j.name]
                gij, bij = yij.real, yij.imag
                delta_ij = bus_i.delta - bus_j.delta
                
                if r != c: # Off-diagonal
                    J1[r, c] = bus_i.vpu * bus_j.vpu * (gij * math.sin(delta_ij) - bij * math.cos(delta_ij))
                else:      # Diagonal
                    p_calc, q_calc = self._get_p_q_calc(bus_i.name)
                    # Diagonal formula: -Q_i - B_ii * V_i^2
                    yii = self.ybus.loc[bus_i.name, bus_i.name]
                    J1[r, c] = -q_calc - yii.imag * (bus_i.vpu ** 2)
        return J1

    def _calc_j2(self):
        """J2 = dP / d|V| (Size: N_non_slack x N_PQ)"""
        rows = len(self.p_buses)
        cols = len(self.q_buses)
        J2 = np.zeros((rows, cols))
        
        for r, bus_i in enumerate(self.p_buses):
            for c, bus_j in enumerate(self.q_buses):
                yij = self.ybus.loc[bus_i.name, bus_j.name]
                gij, bij = yij.real, yij.imag
                delta_ij = bus_i.delta - bus_j.delta
                
                if bus_i.name != bus_j.name: # Off-diagonal
                    J2[r, c] = bus_i.vpu * (gij * math.cos(delta_ij) + bij * math.sin(delta_ij))
                else:                        # Diagonal
                    p_calc, q_calc = self._get_p_q_calc(bus_i.name)
                    yii = self.ybus.loc[bus_i.name, bus_i.name]
                    J2[r, c] = (p_calc / bus_i.vpu) + yii.real * bus_i.vpu
        return J2

    def _calc_j3(self):
        """J3 = dQ / dDelta (Size: N_PQ x N_non_slack)"""
        rows = len(self.q_buses)
        cols = len(self.p_buses)
        J3 = np.zeros((rows, cols))
        
        for r, bus_i in enumerate(self.q_buses):
            for c, bus_j in enumerate(self.p_buses):
                yij = self.ybus.loc[bus_i.name, bus_j.name]
                gij, bij = yij.real, yij.imag
                delta_ij = bus_i.delta - bus_j.delta
                
                if bus_i.name != bus_j.name: # Off-diagonal
                    J3[r, c] = -bus_i.vpu * bus_j.vpu * (gij * math.cos(delta_ij) + bij * math.sin(delta_ij))
                else:                        # Diagonal
                    p_calc, q_calc = self._get_p_q_calc(bus_i.name)
                    yii = self.ybus.loc[bus_i.name, bus_i.name]
                    J3[r, c] = p_calc - yii.real * (bus_i.vpu ** 2)
        return J3

    def _calc_j4(self):
        """J4 = dQ / d|V| (Size: N_PQ x N_PQ)"""
        size = len(self.q_buses)
        J4 = np.zeros((size, size))
        
        for r, bus_i in enumerate(self.q_buses):
            for c, bus_j in enumerate(self.q_buses):
                yij = self.ybus.loc[bus_i.name, bus_j.name]
                gij, bij = yij.real, yij.imag
                delta_ij = bus_i.delta - bus_j.delta
                
                if r != c: # Off-diagonal
                    J4[r, c] = bus_i.vpu * (gij * math.sin(delta_ij) - bij * math.cos(delta_ij))
                else:      # Diagonal
                    p_calc, q_calc = self._get_p_q_calc(bus_i.name)
                    yii = self.ybus.loc[bus_i.name, bus_i.name]
                    J4[r, c] = (q_calc / bus_i.vpu) - yii.imag * bus_i.vpu
        return J4


if __name__ == "__main__":
    circuit1 = Circuit("Test Circuit")

    # Modified: Adding bus_type to add_bus based on Milestone 6 Needs
    circuit1.add_bus("Bus 1", 15.0, bus_type="PQ")
    circuit1.add_bus("Bus 2", 345.0, bus_type="PQ")
    circuit1.add_bus("Bus 3", 15.75, bus_type="PV")
    circuit1.add_bus("Bus 4", 345.0, bus_type="PQ")
    circuit1.add_bus("Bus 5", 345.0, bus_type="Slack")

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

    jacobian1 = Jacobian( circuit1.buses, circuit1.ybus)
    jacobian1_matrix= jacobian1.calc_jacobian()

    print("\n--- Jacobian Matrix ---")
    print(jacobian1_matrix.shape)