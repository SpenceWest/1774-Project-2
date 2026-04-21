from Settings import Settings

class Generator:
    def __init__(self, name: str, bus_name: str, voltage_setpoint: float, mw_setpoint: float, x_subtransient: float = 0.0):
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
        self.x_subtransient = x_subtransient

    def calc_p(self):

        return self.mw_setpoint / Settings.sbase

    def convert_x_subtransient(self, gen_mva: float, gen_kv: float):

        s_sys = Settings.sbase      # system MVA base
        self.x_subtransient = (
            self.x_subtransient
            * (s_sys / gen_mva)
            # voltage-ratio term: (gen_kv / sys_kv)^2 — equals 1 when bases match
        )

    def calc_y_subtransient(self) -> complex:

        if self.x_subtransient == 0.0:
            raise ValueError(
                f"Generator '{self.name}': x_subtransient is 0. "
                "Set it before calling calc_y_subtransient()."
            )

        return 1.0 / complex(0.0, self.x_subtransient)

