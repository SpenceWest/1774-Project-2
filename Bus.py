from Settings import Settings


class Bus:
    bus_index_counter = 0
    valid_bus_types = {"Slack", "PQ", "PV"}

    def __init__(self, name: str, nominal_kv: float, bus_type: str):
        if bus_type not in Bus.valid_bus_types:
            raise ValueError(f"Invalid bus type '{bus_type}'")

        self.name = name
        self.nominal_kv = nominal_kv
        self.bus_index = Bus.bus_index_counter
        self.vpu = 1.0
        self.delta = 0.0
        self.bus_type = bus_type

        # Existing equipment
        self.generators = []
        self.loads = []

        # New equipment models
        self.pv_systems = []
        self.batteries = []

        Bus.bus_index_counter += 1

    def add_generator(self, gen):
        """Attach a generator to this bus."""
        self.generators.append(gen)

    def add_load(self, load):
        """Attach a load to this bus."""
        self.loads.append(load)

    def add_pv_system(self, pv):
        """Attach a PV system to this bus."""
        self.pv_systems.append(pv)

    def add_battery(self, battery):
        """Attach a battery to this bus."""
        self.batteries.append(battery)

    def get_specified_pq(self):
        """
        Calculate the specified real and reactive power for this bus.

        P_spec = P_gen + P_pv + P_batt - P_load
        Q_spec = Q_gen + Q_pv + Q_batt - Q_load

        In the current implementation, generator reactive power is not explicitly
        modeled here, so Q_gen = 0.0.
        """
        p_gen = sum(g.calc_p() for g in self.generators)
        q_gen = 0.0

        p_load = sum(l.calc_p() for l in self.loads)
        q_load = sum(l.calc_q() for l in self.loads)

        p_pv = sum(pv.calc_p() for pv in self.pv_systems)
        q_pv = sum(pv.calc_q() for pv in self.pv_systems)

        p_batt = sum(b.calc_p() for b in self.batteries)
        q_batt = sum(b.calc_q() for b in self.batteries)

        p_spec = p_gen + p_pv + p_batt - p_load
        q_spec = q_gen + q_pv + q_batt - q_load

        return p_spec, q_spec


if __name__ == "__main__":
    bus1 = Bus("Bus 1", 20.0, "Slack")
    bus2 = Bus("Bus 2", 230.0, "PQ")
    bus3 = Bus("Bus 3", 115.0, "PV")

    print(bus1.name, bus1.nominal_kv, bus1.bus_index, bus1.bus_type)
    print(bus2.name, bus2.nominal_kv, bus2.bus_index, bus2.bus_type)
    print(bus3.name, bus3.nominal_kv, bus3.bus_index, bus3.bus_type)
