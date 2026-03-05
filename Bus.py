class Bus:
    bus_index_counter = 0  # Start of the counter
    valid_bus_types = {"Slack", "PQ", "PV"} #DIffrent bus types

    def __init__(self, name:str, nominal_kv:float, bus_type: str):
        if bus_type not in Bus.valid_bus_types:   #Bus type checker
            raise ValueError(f"Invalid bus type '{bus_type}'")

        self.name = name
        self.nominal_kv = nominal_kv
        self.bus_index = Bus.bus_index_counter  # Assign current counter value
        self.vpu = 1.0
        self.delta =0.0
        self.bus_type = bus_type

        Bus.bus_index_counter += 1  # Increment for next bus

if __name__ == "__main__":
    bus1 = Bus("Bus 1", 20.0, "Slack")
    bus2 = Bus("Bus 2", 230.0,"PQ")
    bus3 = Bus("Bus 3", 115.0, "PV")

    print(bus1.name, bus1.nominal_kv, bus1.bus_index, bus1.bus_type)
    print(bus2.name, bus2.nominal_kv, bus2.bus_index, bus2.bus_type)
    print(bus3.name, bus3.nominal_kv, bus3.bus_index, bus3.bus_type)
