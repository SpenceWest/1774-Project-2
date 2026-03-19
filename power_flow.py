import numpy as np
import math

class PowerFlow:
    def __init__(self, buses, ybus, base_mva=100.0):
        self.buses = buses
        self.ybus = ybus
        self.base_mva = base_mva

    def compute_power_injection(self, bus, ybus, all_buses):
        """
        Milestone 6: Implement Real and Reactive Power Calculations.
        Calculates the actual power injected into the network at a given bus.
        
        Eq (2): P_i = |Vi| * sum(|Vj| * (Gij*cos(delta_ij) + Bij*sin(delta_ij)))
        Eq (3): Q_i = |Vi| * sum(|Vj| * (Gij*sin(delta_ij) - Bij*cos(delta_ij)))
        """
        i = bus.bus_index
        p_calc = 0.0
        q_calc = 0.0

        vi = bus.vpu
        delta_i = bus.delta

        for j_bus in all_buses:
            j = j_bus.bus_index
            vj = j_bus.vpu
            delta_j = j_bus.delta

            # Extract Real (G) and Imaginary (B) parts of the Ybus matrix element
            yij = ybus[i, j]
            gij = yij.real
            bij = yij.imag

            # Phase angle difference
            delta_ij = delta_i - delta_j

            # Calculate Real Power (P_calc) using Eq (2)
            p_calc += vi * vj * (gij * math.cos(delta_ij) + bij * math.sin(delta_ij))
            
            # Calculate Reactive Power (Q_calc) using Eq (3)
            q_calc += vi * vj * (gij * math.sin(delta_ij) - bij * math.cos(delta_ij))

        return p_calc, q_calc

    def compute_power_mismatch(self):
        """
        Milestone 6: Power Mismatch Calculation.
        Computes the difference between specified and calculated values for each bus.
        
        Eq (4): delta_P = P_spec - P_calc
        Eq (5): delta_Q = Q_spec - Q_calc
        
        Returns:
            numpy.ndarray: The mismatch vector 'f' used in numerical methods.
        """
        mismatches = []
        
        for bus in self.buses:
            # 1. Slack bus handling: No mismatch calculation required.
            if bus.bus_type == "Slack":
                continue 
            
            # 2. Get specified values (P_spec, Q_spec) from connected equipment
            p_spec, q_spec = bus.get_specified_pq(self.base_mva)
            
            # 3. Get calculated values (P_calc, Q_calc) based on current voltages
            p_calc, q_calc = self.compute_power_injection(bus, self.ybus, self.buses)
            
            # 4. Calculate Real Power Mismatch (Eq 4)
            delta_p = p_spec - p_calc
            
            # Both PQ and PV buses must include delta_P in the mismatch vector
            mismatches.append(delta_p)
            
            # 5. Bus type specific handling:
            #    - PQ buses must include both delta_P and delta_Q.
            #    - PV buses should exclude delta_Q (voltage magnitude is specified).
            if bus.bus_type == "PQ":
                # Calculate Reactive Power Mismatch (Eq 5)
                delta_q = q_spec - q_calc
                mismatches.append(delta_q) 
                
        # 6. Construct and return the mismatch vector 'f'
        f = np.array(mismatches)
        return f
