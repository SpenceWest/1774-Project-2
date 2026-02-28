from Bus import Bus
from TransmissionLine import TransmissionLine
from Generator import Generator
from Load import Load
from Transformer import Transformer
import numpy as np
import pandas as pd

class Circuit:
    def __init__(self, name:str):
        self.name = name
        self.buses = {}
        self.transformers = {}
        self.transmission_lines = {}
        self.loads = {}
        self.generators = {}
        self.ybus = None



    def add_bus(self, bus_name:str, nominal_kv:float):

        new_bus = Bus(bus_name, nominal_kv)
        self.buses[bus_name] = new_bus


    def add_transmission_line(self, name: str, bus1_name:str, bus2_name:str, r: float, x: float, g: float, b: float):


        new_transmission_line = TransmissionLine(name, bus1_name, bus2_name, r, x, g, b)
        self.transmission_lines[name] = new_transmission_line


    def add_load_element(self, name: str,  bus_name:str, mw: float, mvar : float):

        new_load = Load(name, bus_name,  mw, mvar)
        self.loads[name] = new_load

    def add_generator(self, name: str, bus1_name: str, voltage_setpoint: float, mw_setpoint: float):
            if name in self.generators:
                raise ValueError(f"Generator with name '{name}' already exists.")
                
            new_generator = Generator(name, bus1_name, voltage_setpoint, mw_setpoint)
            self.generators[name] = new_generator
        
    def add_transformer(self, name: str, bus1_name: str, bus2_name: str, r: float, x: float):
        if name in self.transformers:
            raise ValueError(f"Transformer with name '{name}' already exists.")
            
        new_transformer = Transformer(name, bus1_name, bus2_name, r, x)
        self.transformers[name] = new_transformer


    def calc_ybus(self):
        N = len(self.buses.keys())



        y_matrix = pd.DataFrame(np.zeros((N, N)), dtype=complex, index= list(self.buses.keys()) , columns=list(self.buses.keys()))
        index_mapping = self.buses.copy()

        i =0
        for key in index_mapping.keys():
            index_mapping[key] = i
            i += 1

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

        print()





if __name__ == "__main__":


        circuit1 = Circuit("Test Circuit")


        print(circuit1.name)
        print(type(circuit1.name))


        circuit1.add_bus("Bus 1", 20)
        circuit1.add_bus("Bus 2", 230)

        circuit1.add_transmission_line("Line 1", "Bus 1", "Bus 2", 0.02, 0.25, 0.0, 0.04)

        circuit1.add_transformer("T1", "Bus 1", "Bus 2", 0.01, 0.10)

        circuit1.calc_ybus()


        """#Attribute Initialization

        print(circuit1.buses)
        print(type(circuit1.buses))

        print(circuit1.transformers)
        print(circuit1.generators)
        print(circuit1.transmission_lines)
        print(circuit1.loads)


        #Verify Buses
        circuit1.add_bus("Bus 1", 20)
        circuit1.add_bus("Bus 2", 230)


        print(list(circuit1.buses.keys()))
        print(circuit1.buses["Bus 1"].name, circuit1.buses["Bus 1"].nominal_kv)

        #Verify Transmission Line
        circuit1.add_transmission_line("Line 1", "Bus 1", "Bus 2", 0.02, 0.25, 0.0, 0.04)

        print(list(circuit1.transmission_lines.keys()))

        print(circuit1.transmission_lines["Line 1"].name,
              circuit1.transmission_lines["Line 1"].bus1_name,
              circuit1.transmission_lines["Line 1"].bus2_name,
              circuit1.transmission_lines["Line 1"].r,
              circuit1.transmission_lines["Line 1"].x,
              circuit1.transmission_lines["Line 1"].g,
              circuit1.transmission_lines["Line 1"].b)

        #Verify Loads
        circuit1.add_load_element("Line 1", "Bus 2", 50, 30)

        print(list(circuit1.loads.keys()))

        print(circuit1.loads["Line 1"].name,
              circuit1.loads["Line 1"].bus_name,
              circuit1.loads["Line 1"].mw,
              circuit1.loads["Line 1"].mvar,
              )



        circuit1.add_transformer("T1", "Bus 1", "Bus 2", 0.01, 0.10)

        # Expected output: ['T1']
        print(list(circuit1.transformers.keys()))

        print(circuit1.transformers["T1"].name,
              circuit1.transformers["T1"].bus1_name,
              circuit1.transformers["T1"].bus2_name,
              circuit1.transformers["T1"].r,
              circuit1.transformers["T1"].x)


        # ---------------------------------------------------------

        circuit1.add_generator("G1", "Bus 1", 1.04, 100.0)

        # Expected output: ['G1']
        print(list(circuit1.generators.keys()))

        print(circuit1.generators["G1"].name,
              circuit1.generators["G1"].bus1_name,
              circuit1.generators["G1"].voltage_setpoint,
              circuit1.generators["G1"].mw_setpoint)"""









