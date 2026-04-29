from Bus import Bus
from TransmissionLine import TransmissionLine
from Generator import Generator
from Load import Load
from Transformer import Transformer
from PVSystem import PVSystem
from Battery import Battery
from Settings import Settings
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

        # New Project 3 equipment collections
        self.pv_systems = {}
        self.batteries = {}

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
        else:
            print(f"Warning: Bus '{bus_name}' not found. Load '{name}' not attached to a bus.")

    def add_generator(self, name: str, bus1_name: str, voltage_setpoint: float, mw_setpoint: float, x_subtransient: float = 0.0):
        if name in self.generators:
            raise ValueError(f"Generator with name '{name}' already exists.")

        new_generator = Generator(name, bus1_name, voltage_setpoint, mw_setpoint, x_subtransient=x_subtransient)
        self.generators[name] = new_generator

        if bus1_name in self.buses:
            self.buses[bus1_name].add_generator(new_generator)
            if self.buses[bus1_name].bus_type in ["PV", "Slack"]:
                self.buses[bus1_name].vpu = voltage_setpoint
        else:
            print(f"Warning: Bus '{bus1_name}' not found. Generator '{name}' not attached to a bus.")

    def add_transformer(self, name: str, bus1_name: str, bus2_name: str, r: float, x: float):
        if name in self.transformers:
            raise ValueError(f"Transformer with name '{name}' already exists.")

        new_transformer = Transformer(name, bus1_name, bus2_name, r, x)
        self.transformers[name] = new_transformer

    def add_pv_system(self, name: str, bus_name: str, rated_mw: float, irradiance: float, q_setpoint: float = 0.0, power_factor: float = None):
        if name in self.pv_systems:
            raise ValueError(f"PV system with name '{name}' already exists.")

        new_pv = PVSystem(
            name=name,
            bus_name=bus_name,
            rated_mw=rated_mw,
            irradiance=irradiance,
            q_setpoint=q_setpoint,
            power_factor=power_factor
        )
        self.pv_systems[name] = new_pv

        if bus_name in self.buses:
            self.buses[bus_name].add_pv_system(new_pv)
        else:
            print(f"Warning: Bus '{bus_name}' not found. PV system '{name}' not attached to a bus.")

    def add_battery(self, name: str, bus_name: str, mode: str, dispatch_mw: float, max_charge_mw: float = 0.0, max_discharge_mw: float = 0.0, soc: float = 0.5, q_setpoint: float = 0.0):
        if name in self.batteries:
            raise ValueError(f"Battery with name '{name}' already exists.")

        new_battery = Battery(
            name=name,
            bus_name=bus_name,
            mode=mode,
            dispatch_mw=dispatch_mw,
            max_charge_mw=max_charge_mw,
            max_discharge_mw=max_discharge_mw,
            soc=soc,
            q_setpoint=q_setpoint
        )
        self.batteries[name] = new_battery

        if bus_name in self.buses:
            self.buses[bus_name].add_battery(new_battery)
        else:
            print(f"Warning: Bus '{bus_name}' not found. Battery '{name}' not attached to a bus.")

    def compute_power_mismatch(self):
        """
        Computes the mismatch vector f for the current system state.
        """
        if self.ybus is None:
            raise ValueError("Ybus has not been calculated yet. Call calc_ybus() first.")

        deltaQ_list = []
        deltaP_list = []

        for bus_name, bus in self.buses.items():
            if bus.bus_type == "Slack":
                continue

            p_spec, q_spec = bus.get_specified_pq()
            p_calc, q_calc = self.compute_power_injection(bus_name)

            delta_p = p_spec - p_calc
            deltaP_list.append(delta_p)

            if bus.bus_type == "PQ":
                delta_q = q_spec - q_calc
                deltaQ_list.append(delta_q)

        f = np.array(deltaP_list + deltaQ_list, dtype=float)
        return f

    def calc_ybus(self):
        """
        Build Ybus only from branch elements.
        PV systems and batteries are NOT stamped into Ybus.
        """
        N = len(self.buses.keys())
        y_matrix = pd.DataFrame(
            np.zeros((N, N)),
            dtype=complex,
            index=list(self.buses.keys()),
            columns=list(self.buses.keys())
        )

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

    def compute_power_injection(self, i_name: str):
        """
        Calculates actual network power injection at a bus using Ybus and current bus states.
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

            yij = self.ybus.loc[i_name, j_name]
            gij = yij.real
            bij = yij.imag

            delta_ij = delta_i - delta_j

            p_calc += vj * (gij * np.cos(delta_ij) + bij * np.sin(delta_ij))
            q_calc += vj * (gij * np.sin(delta_ij) - bij * np.cos(delta_ij))

        p_calc *= vi
        q_calc *= vi

        return p_calc, q_calc

    def print_bus_results(self):
        """
        Print bus voltage and specified/calculated power.
        This is useful for direct comparison with PowerWorld.
        """
        print("\n--- Bus Results ---")
        print(f"{'Bus':<10}{'Vpu':<12}{'Angle(deg)':<14}{'P_spec':<12}{'Q_spec':<12}{'P_calc':<12}{'Q_calc':<12}")
        for bus_name, bus in self.buses.items():
            p_spec, q_spec = bus.get_specified_pq()
            p_calc, q_calc = self.compute_power_injection(bus_name)
            print(f"{bus_name:<10}{bus.vpu:<12.6f}{bus.delta:<14.6f}{p_spec:<12.6f}{q_spec:<12.6f}{p_calc:<12.6f}{q_calc:<12.6f}")


if __name__ == "__main__":
    from PowerFlow import PowerFlow

    circuit1 = Circuit("Project 3 Test Circuit")

    # Existing buses
    circuit1.add_bus("Bus 1", 15.0, bus_type="Slack")
    circuit1.add_bus("Bus 2", 345.0, bus_type="PQ")
    circuit1.add_bus("Bus 3", 15.75, bus_type="PV")
    circuit1.add_bus("Bus 4", 345.0, bus_type="PQ")
    circuit1.add_bus("Bus 5", 345.0, bus_type="PQ")

    # Example new connection location
    circuit1.add_bus("Bus 6", 34.5, bus_type="PQ")

    # Initial voltages
    circuit1.buses["Bus 1"].vpu = 1.00
    circuit1.buses["Bus 2"].vpu = 1.00
    circuit1.buses["Bus 3"].vpu = 1.05
    circuit1.buses["Bus 4"].vpu = 1.00
    circuit1.buses["Bus 5"].vpu = 1.00
    circuit1.buses["Bus 6"].vpu = 1.00

    # Initial angles
    circuit1.buses["Bus 1"].delta = 0.0
    circuit1.buses["Bus 2"].delta = 0.0
    circuit1.buses["Bus 3"].delta = 0.0
    circuit1.buses["Bus 4"].delta = 0.0
    circuit1.buses["Bus 5"].delta = 0.0
    circuit1.buses["Bus 6"].delta = 0.0

    # Branches
    circuit1.add_transmission_line("Line 1", "Bus 4", "Bus 2", 0.009, 0.1, 0.0, 1.72)
    circuit1.add_transmission_line("Line 2", "Bus 5", "Bus 2", 0.0045, 0.05, 0.0, 0.88)
    circuit1.add_transmission_line("Line 3", "Bus 5", "Bus 4", 0.00225, 0.025, 0.0, 0.44)

    circuit1.add_transformer("T1", "Bus 1", "Bus 5", 0.0015, 0.02)
    circuit1.add_transformer("T2", "Bus 3", "Bus 4", 0.00075, 0.01)
    circuit1.add_transformer("T3", "Bus 5", "Bus 6", 0.0010, 0.015)

    # Existing source/load
    circuit1.add_generator("G1", "Bus 1", 1.00, 278.0)
    circuit1.add_generator("G2", "Bus 3", 1.05, 520.0)

    circuit1.add_load_element("Load 1", "Bus 2", 800.0, 280.0)
    circuit1.add_load_element("Load 2", "Bus 3", 80.0, 40.0)

    # New equipment models
    circuit1.add_pv_system(
        name="PV 1",
        bus_name="Bus 6",
        rated_mw=120.0,
        irradiance=0.75,
        q_setpoint=15.0
    )

    # Battery case 1: discharge
    circuit1.add_battery(
        name="Battery 1",
        bus_name="Bus 2",
        mode="discharge",
        dispatch_mw=50.0,
        max_discharge_mw=80.0,
        soc=0.60,
        q_setpoint=5.0
    )

    circuit1.calc_ybus()
    print("\n--- Ybus Matrix ---")
    print(circuit1.ybus)

    print("\n--- Initial Power Mismatch Vector ---")
    mismatch_vector = circuit1.compute_power_mismatch()
    print(mismatch_vector)

    powerflow = PowerFlow()
    powerflow.solve(circuit1)

    circuit1.print_bus_results()
