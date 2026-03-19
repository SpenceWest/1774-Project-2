class Load:
    def __init__(self, name: str, bus1_name: str, mw: float, mvar: float):
        self.name = name
        self.bus_name = bus1_name
        self.mw = mw
        self.mvar = mvar
        self.p = None  # Per unit real power consumption
        self.q = None  # Per unit reactive power consumption

    def calc_p(self, base_mva: float = 100.0):
        """
        Calculate and return the per-unit real power consumption.
        """
        self.p = self.mw / base_mva
        return self.p

    def calc_q(self, base_mva: float = 100.0):
        """
        Calculate and return the per-unit reactive power consumption.
        """
        self.q = self.mvar / base_mva
        return self.q

if __name__ == "__main__":
    # Test case based on the PDF example
    load1 = Load("Load-1", "Bus-2", 50.0, 30.0)
    print(f"{load1.name} at {load1.bus_name} consumes {load1.calc_p()} p.u. P and {load1.calc_q()} p.u. Q")
