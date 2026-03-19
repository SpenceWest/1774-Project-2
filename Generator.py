class Generator:
    def __init__(self, name: str, bus1_name: str, voltage_setpoint: float, mw_setpoint: float):
        self.name = name
        self.bus1_name = bus1_name
        self.voltage_setpoint = voltage_setpoint
        self.mw_setpoint = mw_setpoint
        self.p = None  # Per unit real power injection

    def calc_p(self, base_mva: float = 100.0):
        """
        Calculate and return the per-unit real power injection 
        based on the system base MVA.
        """
        self.p = self.mw_setpoint / base_mva
        return self.p

if __name__ == "__main__":
    # Test case based on the PDF example
    gen1 = Generator("G1", "Bus-1", 1.04, 100.0)
    print(f"{gen1.name} connected to {gen1.bus1_name} injects {gen1.calc_p()} p.u. Real Power")
