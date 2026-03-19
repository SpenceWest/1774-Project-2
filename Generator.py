from Settings import Settings

class Generator:
    def __init__(self, name: str, bus_name: str, voltage_setpoint: float, mw_setpoint: float):
        """
        Initialize a Generator attached to a specific bus.

        :param name: Name of the generator (e.g., 'G1')
        :param bus_name: Name of the bus it is attached to (e.g., 'Bus 1')
        :param voltage_setpoint: The target voltage magnitude in per-unit (p.u.)
        :param mw_setpoint: The real power output setpoint in MW
        """
        self.name = name
        self.bus_name = bus_name
        self.voltage_setpoint = voltage_setpoint
        self.mw_setpoint = mw_setpoint

    def calc_p(self):
        """
        Calculates the per-unit real power generation.
        Generation is considered a POSITIVE power injection into the bus.
        """
        return self.mw_setpoint / Settings.sbase


