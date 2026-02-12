class Bus:
    bus_index_counter = 1  # Start of the counter

    def __init__(self, name, nominal_kv):
        self.name = name
        self.nominal_kv = nominal_kv
        self.bus_index = Bus.bus_index_counter  # Assign current counter value

        Bus.bus_index_counter += 1  # Increment for next bus

if __name__ == "__main__":
    bus1 = Bus("Bus 1", 20.0)
    bus2 = Bus("Bus 2", 230.0)
    bus3 = Bus("Bus 3", 115.0)

    print(bus1.name, bus1.nominal_kv, bus1.bus_index)
    print(bus2.name, bus2.nominal_kv, bus2.bus_index)
    print(bus3.name, bus3.nominal_kv, bus3.bus_index)
