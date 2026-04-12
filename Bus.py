from Settings import Settings

class Bus:
    bus_index_counter = 0 # Start of the counter
    valid_bus_types = {"Slack", "PQ", "PV"} # Different bus types

    def __init__(self, name: str, nominal_kv: float, bus_type: str):
        if bus_type not in Bus.valid_bus_types:   # Bus type checker
            raise ValueError(f"Invalid bus type '{bus_type}'")

        self.name = name
        self.nominal_kv = nominal_kv
        self.bus_index = Bus.bus_index_counter  # Assign current counter value
        self.vpu = 1.0
        self.delta = 0.0
        self.bus_type = bus_type

        # Lists to hold devices connected to this specific bus
        self.generators = []
        self.loads = []

        Bus.bus_index_counter += 1  # Increment for next bus

    def add_generator(self, gen):
        """Attach a generator to this bus."""
        self.generators.append(gen)

    def add_load(self, load):
        """Attach a load to this bus."""
        self.loads.append(load)

    def get_specified_pq(self):
        """
        Calculate the specified real (P_spec) and reactive (Q_spec) power for the bus.
        Formulas:
        P_spec = P_gen - P_load
        Q_spec = Q_gen - Q_load
        """
        p_gen = sum(g.calc_p() for g in self.generators)
        # Generators usually control voltage (PV bus), thus Q_gen is unconstrained initially
        q_gen = 0.0

        p_load = sum(l.calc_p() for l in self.loads)
        q_load = sum(l.calc_q() for l in self.loads)

        p_spec = p_gen - p_load
        q_spec = q_gen - q_load

        return p_spec, q_spec

if __name__ == "__main__":
    bus1 = Bus("Bus 1", 20.0, "Slack")
    bus2 = Bus("Bus 2", 230.0, "PQ")
    bus3 = Bus("Bus 3", 115.0, "PV")

    print(bus1.name, bus1.nominal_kv, bus1.bus_index, bus1.bus_type)
    print(bus2.name, bus2.nominal_kv, bus2.bus_index, bus2.bus_type)
    print(bus3.name, bus3.nominal_kv, bus3.bus_index, bus3.bus_type)