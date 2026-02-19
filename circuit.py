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


    def add_bus(self, bus_name:str):

        new_bus = Bus(bus_name)
        self.buses[bus_name] = new_bus


    def add_transmission_line(self, name: str, bus1:str, bus2:str, r: float, x: float, g: float, b: float):


        new_transmission_line = TransmissionLine(name, bus1, bus2, r, x, g, b)
        self.transmission_lines[name] = new_transmission_line


    def add_load_element(self, name: str,  bus1:str, mw: float, mvar : float):

        new_load = Load(name, bus1,  mw, mvar)
        self.loads[name] = new_load








    if __name__ == "__main__":
        circuit1 = Circuit("circuit1")


        print(circuit1.name)
        print(type(circuit1.name))



        print(circuit1.buses)
        print(type(circuit1.buses))


        print(circuit1.transformers)
        print(circuit1.generators)
        print(circuit1.transmission_line)