from Settings import Settings
import math


class PVSystem:
    def __init__(
        self,
        name: str,
        bus_name: str,
        rated_mw: float,
        irradiance: float,
        q_setpoint: float = 0.0,
        power_factor: float = None
    ):
        """
        PV equipment model.
        Treated as a bus-connected PQ injection device for steady-state power flow.

        Parameters
        ----------
        name : str
            Equipment name
        bus_name : str
            Connected bus name
        rated_mw : float
            Rated active power output in MW
        irradiance : float
            Simple scaling factor, usually 0.0 to 1.0
        q_setpoint : float
            Reactive power injection in MVAR if power_factor is not used
        power_factor : float
            Fixed power factor if used instead of q_setpoint
        """
        self.name = name
        self.bus_name = bus_name
        self.rated_mw = rated_mw
        self.irradiance = irradiance
        self.q_setpoint = q_setpoint
        self.power_factor = power_factor

    def calc_p(self):
        """
        Active power injection in per unit.
        Simplest model:
            P = rated_mw * irradiance
        """
        p_mw = self.rated_mw * self.irradiance
        return p_mw / Settings.sbase

    def calc_q(self):
        """
        Reactive power injection in per unit.

        If power_factor is given, compute Q from P and pf.
        Otherwise, directly use q_setpoint.
        """
        if self.power_factor is not None:
            if self.power_factor <= 0.0 or self.power_factor > 1.0:
                raise ValueError(
                    f"PVSystem '{self.name}': power_factor must be in (0, 1]."
                )

            p_mw = self.rated_mw * self.irradiance

            if self.power_factor == 1.0:
                q_mvar = 0.0
            else:
                theta = math.acos(self.power_factor)
                q_mvar = p_mw * math.tan(theta)

            return q_mvar / Settings.sbase

        return self.q_setpoint / Settings.sbase


if __name__ == "__main__":
    pv1 = PVSystem(
        name="PV1",
        bus_name="Bus 6",
        rated_mw=100.0,
        irradiance=0.8,
        q_setpoint=10.0
    )

    print(pv1.name, pv1.bus_name)
    print("P (pu):", pv1.calc_p())
    print("Q (pu):", pv1.calc_q())
