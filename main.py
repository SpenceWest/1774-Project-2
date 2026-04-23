import numpy as np
import pandas as pd
from circuit import Circuit
from Solution import Solution
from Bus import Bus

def get_float(prompt):
    """Keep asking until the user types a valid number."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  Please enter a number.")


def get_choice(prompt, valid):
    """Keep asking until the user picks one of the valid options."""
    while True:
        choice = input(prompt).strip()
        if choice in valid:
            return choice
        print(f"  Invalid choice. Options: {valid}")


# ─────────────────────────────────────────────
#  SECTION MENUS
# ─────────────────────────────────────────────
def add_buses(circuit):
    """Prompt the user to add one or more buses."""
    print("\nAdd Buses ")
    while True:
        name = input("Bus name (or press enter to finish): ").strip()
        if not name:
            break

        kv = get_float("Nominal kV: ")
        b_type = get_choice(" Bus type [Slack / PV / PQ]: ",["Slack", "PV", "PQ"])

        circuit.add_bus(name, kv, b_type)

        # For PV / Slack buses let the user set the voltage setpoint now
        if b_type in ("Slack", "PV"):
            vpu = get_float("  Voltage setpoint (pu, e.g. 1.0): ")

            circuit.buses[name].vpu = vpu

        print(f"Bus '{name}' added.")


def add_transmission_lines(circuit):
    """Prompt the user to add transmission lines."""
    if not circuit.buses:
        print("  No buses defined yet — add buses first.")
        return

    print("\n── Add Transmission Lines ─────────────")
    print("  Available buses:", list(circuit.buses.keys()))

    while True:
        name = input("  Line name (or press enter to finish): ").strip()
        if not name:
            break

        bus1 = input("  From bus: ").strip()
        bus2 = input("  To bus:   ").strip()
        r = get_float("  R (pu): ")
        x = get_float("  X (pu): ")
        g = get_float("  G shunt (pu, usually 0): ")
        b = get_float("  B shunt (pu): ")

        circuit.add_transmission_line(name, bus1, bus2, r, x, g, b)
        print(f"Line '{name}' added.")


def add_transformers(circuit):
    """Prompt the user to add transformers."""
    if not circuit.buses:
        print("  No buses defined yet — add buses first.")
        return

    print("\n── Add Transformers ───────────────────")
    print("  Available buses:", list(circuit.buses.keys()))

    while True:
        name = input("  Transformer name (or press enter to finish): ").strip()
        if not name:
            break

        bus1 = input("  From bus: ").strip()
        bus2 = input("  To bus:   ").strip()
        r = get_float("  R (pu): ")
        x = get_float("  X (pu): ")

        circuit.add_transformer(name, bus1, bus2, r, x)
        print(f"Transformer '{name}' added.")


def add_generators(circuit):
    """Prompt the user to add generators."""
    if not circuit.buses:
        print("  No buses defined yet — add buses first.")
        return

    print("\n── Add Generators ─────────────────────")
    print("  Available buses:", list(circuit.buses.keys()))

    while True:
        name = input("  Generator name (or press enter to finish): ").strip()
        if not name:
            break

        bus = input("  Connected bus: ").strip()
        vset = get_float("  Voltage setpoint (pu): ")
        mw = get_float("  MW setpoint: ")
        xpp = get_float("  X'' subtransient (pu, enter 0 if unknown): ")

        circuit.add_generator(name, bus, vset, mw, x_subtransient=xpp)
        print(f"Generator '{name}' added.")


def add_loads(circuit):
    """Prompt the user to add loads."""
    if not circuit.buses:
        print("  No buses defined yet — add buses first.")
        return

    print("\n── Add Loads ──────────────────────────")
    print("  Available buses:", list(circuit.buses.keys()))

    while True:
        name = input("  Load name (or ENTER to finish): ").strip()
        if not name:
            break

        bus = input("  Connected bus: ").strip()
        mw = get_float("  MW consumption: ")
        mvar = get_float("  MVAR consumption: ")

        circuit.add_load_element(name, bus, mw, mvar)
        print(f"Load '{name}' added.")


def print_summary(circuit):
    """Print a quick summary of what has been added to the circuit."""
    print("\n── Circuit Summary ────────────────────")
    print(f"  Buses          : {list(circuit.buses.keys())}")
    print(f"  Trans. lines   : {list(circuit.transmission_lines.keys())}")
    print(f"  Transformers   : {list(circuit.transformers.keys())}")
    print(f"  Generators     : {list(circuit.generators.keys())}")
    print(f"  Loads          : {list(circuit.loads.keys())}")


def run_analysis(circuit):
    """Ask the user which analysis to run, then call Solution."""
    print("\n── Run Analysis ───────────────────────")
    mode = get_choice("  Choose mode [powerflow / fault]: ", ["powerflow", "fault"])

    solver = Solution()

    if mode == "powerflow":
        solver.solution(circuit, mode="powerflow")

    else:  # fault study
        print("  Available buses:", list(circuit.buses.keys()))
        fault_bus = input("  Fault bus name: ").strip()
        v_pre = get_float("  Pre-fault voltage (pu, usually 1.0): ")
        solver.solution(circuit, mode="fault",
        fault_bus=fault_bus, v_prefault=v_pre)


# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────
def main():
    print("=" * 45)
    print("   Power System Simulator")
    print("=" * 45)

    # Reset bus counter so indices start at 0 each run
    Bus.bus_index_counter = 0

    circuit_name = input("Circuit name: ").strip() or "My Circuit"
    circuit = Circuit(circuit_name)

    # Main menu loop
    MENU = """
  1. Add buses
  2. Add transmission lines
  3. Add transformers
  4. Add generators
  5. Add loads
  6. Run analysis
  0. Exit
"""
    actions = {
        "1": add_buses,
        "2": add_transmission_lines,
        "3": add_transformers,
        "4": add_generators,
        "5": add_loads,
    }

    while True:
        print(MENU)
        choice = input("Select option: ").strip()

        if choice in actions:
            actions[choice](circuit)  # call the matching function



        elif choice == "6":
            # Need at least one bus before solving
            if not circuit.buses:
                print("Add at least one bus before running analysis.")
            else:
                run_analysis(circuit)

        elif choice == "0":
            print("Done")
            break

        else:
            print("Unknown option, try again.")


if __name__ == "__main__":
    main()
