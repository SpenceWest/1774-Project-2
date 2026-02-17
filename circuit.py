from Bus import Bus
from TransmissionLine import TransmissionLine
from Generator import Generator
from Load import Load

class Circuit:
    def __init__(self, name:str):
        self.name = name
        self.buses = {}
        self.resistors = {}
        self.loads = {}
        self.generators = {}


    def add_bus(self, bus_name:str):

        new_bus = Bus(bus_name)
        self.buses[bus_name] = new_bus


    def add_transmission_line(self, name: str, bus1:str, bus2:str, r: float, x: float, g: float, b: float):


        new_resistor = TransmissionLine(name, bus1, bus2, r, x, g, b)
        self.resistors[name] = new_resistor


    def add_load_element(self, name: str,  bus1:str, mw: float, mvar : float):

        new_load = Load(name, bus1, p, q, r, x, )
        self.loads[name] = new_load
