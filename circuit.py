from Bus import Bus
from TransmissionLine import TransmissionLine
from Generator import Generator
from Load import Load

class Circuit:
    def __init__(self, name:str):
        self.name = name
        self.buses = {}
        self.transformers = {}
        self.transmission_lines = {}
        self.loads = {}
        self.generators = {}


    def add_bus(self, bus_name:str, nominal_kv:float):

        new_bus = Bus(bus_name, nominal_kv)
        self.buses[bus_name] = new_bus


    def add_transmission_line(self, name: str, bus1_name:str, bus2_name:str, r: float, x: float, g: float, b: float):


        new_transmission_line = TransmissionLine(name, bus1_name, bus2_name, r, x, g, b)
        self.transmission_lines[name] = new_transmission_line


    def add_load_element(self, name: str,  bus_name:str, mw: float, mvar : float):

        new_load = Load(name, bus_name,  mw, mvar)
        self.loads[name] = new_load








if __name__ == "__main__":


        circuit1 = Circuit("Test Circuit")


        print(circuit1.name)
        print(type(circuit1.name))


        #Attribute Initialization

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












