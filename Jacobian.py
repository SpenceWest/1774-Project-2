import numpy as np
import pandas as pd
import math

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
