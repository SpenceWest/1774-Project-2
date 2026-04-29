from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QComboBox,
                             QDialogButtonBox, QLabel, QMessageBox, QVBoxLayout)
from PyQt6.QtCore import Qt


class PropertiesDialog(QDialog):
    def __init__(self, component_type: str, circuit, parent=None):
        super().__init__(parent)
        self.component_type = component_type
        self.circuit        = circuit
        self.values         = {}  # filled on OK

        self.setWindowTitle(f"New {component_type}")
        self.setMinimumWidth(300)

        # Outer layout
        outer = QVBoxLayout(self)

        # Form layout holds all the fields
        self.form = QFormLayout()
        outer.addLayout(self.form)

        # Build the right fields for this component
        self._build_fields()

        # OK / Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)

    # ------------------------------------------------------------------ #
    #  Field builders
    # ------------------------------------------------------------------ #

    def _build_fields(self):
        """Add the right fields depending on component type."""
        if self.component_type == "Bus":
            self._field("name",       "Name",          "Bus 1")
            self._field("nominal_kv", "Nominal kV",    "345.0")
            self._combo("bus_type",   "Bus Type",      ["PQ", "PV", "Slack"])

        elif self.component_type == "Generator":
            self._check_buses_exist()
            self._field("name",            "Name",                  "G1")
            self._bus_combo("bus_name",    "Bus")
            self._field("voltage_setpoint","Voltage Setpoint (pu)", "1.0")
            self._field("mw_setpoint",     "MW Setpoint",           "100.0")
            self._field("x_subtransient",  "X'' (pu)",              "0.0")

        elif self.component_type == "Load":
            self._check_buses_exist()
            self._field("name", "Name", "Load 1")
            self._bus_combo("bus_name", "Bus")
            self._field("mw",   "MW",   "100.0")
            self._field("mvar", "MVAR", "50.0")

        elif self.component_type == "Transmission Line":
            self._check_buses_exist()
            self._field("name", "Name", "Line 1")
            self._bus_combo("bus1_name", "From Bus")
            self._bus_combo("bus2_name", "To Bus")
            self._field("r", "R (pu)", "0.01")
            self._field("x", "X (pu)", "0.10")
            self._field("g", "G (pu)", "0.0")
            self._field("b", "B (pu)", "0.0")

        elif self.component_type == "Transformer":
            self._check_buses_exist()
            self._field("name", "Name", "T1")
            self._bus_combo("bus1_name", "From Bus")
            self._bus_combo("bus2_name", "To Bus")
            self._field("r", "R (pu)", "0.0")
            self._field("x", "X (pu)", "0.10")

    def _field(self, key: str, label: str, default: str):
        """Add a text input row."""
        edit = QLineEdit(default)
        self.form.addRow(label + ":", edit)
        self.values[key] = edit          # store reference for reading later

    def _combo(self, key: str, label: str, options: list):
        """Add a dropdown row."""
        combo = QComboBox()
        combo.addItems(options)
        self.form.addRow(label + ":", combo)
        self.values[key] = combo

    def _bus_combo(self, key: str, label: str):
        """Dropdown populated with buses already in the circuit."""
        combo = QComboBox()
        combo.addItems(list(self.circuit.buses.keys()))
        self.form.addRow(label + ":", combo)
        self.values[key] = combo

    def _check_buses_exist(self):
        """Warn immediately if no buses have been placed yet."""
        if not self.circuit.buses:
            QMessageBox.warning(self, "No Buses",
                                "Place at least two buses before adding "
                                "a line or transformer.")
            # Delay the rejection until after __init__ finishes
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, self.reject)

    # ------------------------------------------------------------------ #
    #  OK handler — read all fields into a plain dict
    # ------------------------------------------------------------------ #

    def _on_ok(self):
        """Collect values and close with Accepted."""
        result = {}
        for key, widget in self.values.items():
            if isinstance(widget, QLineEdit):
                result[key] = widget.text().strip()
            elif isinstance(widget, QComboBox):
                result[key] = widget.currentText()

        # Basic validation — no empty fields allowed
        for key, val in result.items():
            if val == "":
                QMessageBox.warning(self, "Missing Field",
                                    f"'{key}' cannot be empty.")
                return

        self.values = result   # replace widget refs with plain strings
        self.accept()

    # ------------------------------------------------------------------ #
    #  Convenience — call this after exec() to get the filled values
    # ------------------------------------------------------------------ #

    def get_values(self) -> dict:
        return self.values


# ------------------------------------------------------------------ #
#  Quick test
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from circuit import Circuit

    app = QApplication(sys.argv)

    # Test with a Bus dialog
    c = Circuit("Test")
    dlg = PropertiesDialog("Bus", c)
    if dlg.exec():
        print("Bus values:", dlg.get_values())

    # Test with a Transmission Line (no buses — should warn)
    dlg2 = PropertiesDialog("Transmission Line", c)
    if dlg2.exec():
        print("Line values:", dlg2.get_values())
