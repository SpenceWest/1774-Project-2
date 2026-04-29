from Settings import Settings


class Battery:
    def __init__(
        self,
        name: str,
        bus_name: str,
        mode: str,
        dispatch_mw: float,
        max_charge_mw: float = 0.0,
        max_discharge_mw: float = 0.0,
        soc: float = 0.5,
        q_setpoint: float = 0.0
    ):
        """
        Battery equipment model.
        Treated as a bus-connected bidirectional PQ injection/absorption device.

        Parameters
        ----------
        name : str
            Equipment name
        bus_name : str
            Connected bus name
        mode : str
            'charge', 'discharge', or 'idle'
        dispatch_mw : float
            Requested active power magnitude in MW
        max_charge_mw : float
            Maximum charging power in MW
        max_discharge_mw : float
            Maximum discharging power in MW
        soc : float
            State of charge placeholder, 0.0 to 1.0
        q_setpoint : float
            Reactive power setting in MVAR
        """
        valid_modes = {"charge", "discharge", "idle"}
        if mode not in valid_modes:
            raise ValueError(
                f"Invalid battery mode '{mode}'. Must be one of {valid_modes}."
            )

        self.name = name
        self.bus_name = bus_name
        self.mode = mode
        self.dispatch_mw = dispatch_mw
        self.max_charge_mw = max_charge_mw
        self.max_discharge_mw = max_discharge_mw
        self.soc = soc
        self.q_setpoint = q_setpoint

    def calc_p(self):
        """
        Active power in per unit.

        discharge -> positive injection
        charge    -> negative injection
        idle      -> zero
        """
        if self.mode == "discharge":
            if self.max_discharge_mw > 0.0:
                p_mw = min(self.dispatch_mw, self.max_discharge_mw)
            else:
                p_mw = self.dispatch_mw
            return p_mw / Settings.sbase

        if self.mode == "charge":
            if self.max_charge_mw > 0.0:
                p_mw = min(self.dispatch_mw, self.max_charge_mw)
            else:
                p_mw = self.dispatch_mw
            return -p_mw / Settings.sbase

        return 0.0

    def calc_q(self):
        """
        Reactive power in per unit.
        Simplest model: fixed q_setpoint when active, zero when idle.
        """
        if self.mode == "idle":
            return 0.0
        return self.q_setpoint / Settings.sbase


if __name__ == "__main__":
    batt1 = Battery(
        name="B1",
        bus_name="Bus 2",
        mode="discharge",
        dispatch_mw=50.0,
        max_discharge_mw=80.0,
        soc=0.6,
        q_setpoint=5.0
    )

    print(batt1.name, batt1.bus_name, batt1.mode)
    print("P (pu):", batt1.calc_p())
    print("Q (pu):", batt1.calc_q())
