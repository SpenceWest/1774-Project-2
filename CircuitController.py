from PyQt6.QtWidgets import (QDialog, QFormLayout, QComboBox, QLineEdit,
                             QDialogButtonBox, QVBoxLayout, QMessageBox)

from Solution import Solution
from circuit import Circuit


class FaultDialog(QDialog):
    """Small dialog to collect fault bus and pre-fault voltage."""

    def __init__(self, circuit: Circuit, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fault Study Settings")
        self.setMinimumWidth(280)

        outer = QVBoxLayout(self)
        form  = QFormLayout()
        outer.addLayout(form)

        # Bus dropdown
        self.bus_combo = QComboBox()
        self.bus_combo.addItems(list(circuit.buses.keys()))
        form.addRow("Fault Bus:", self.bus_combo)

        # Pre-fault voltage field
        self.v_edit = QLineEdit("1.0")
        form.addRow("Pre-fault V (pu):", self.v_edit)

        # OK / Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)

    def get_values(self):
        return {
            "fault_bus":  self.bus_combo.currentText(),
            "v_prefault": float(self.v_edit.text())
        }


class CircuitController:
    def __init__(self, circuit: Circuit, results_box, scene):
        self.circuit     = circuit
        self.results_box = results_box  # QTextEdit in MainWindow
        self.scene       = scene
        self.solver      = Solution()

    # ------------------------------------------------------------------ #
    #  Power Flow
    # ------------------------------------------------------------------ #

    def run_powerflow(self):
        """Build Ybus and run Newton-Raphson power flow."""

        # Basic check — need at least one bus
        if not self.circuit.buses:
            self._warn("No buses defined. Build a circuit first.")
            return

        # Check for a slack bus
        slack_buses = [b for b in self.circuit.buses.values()
                       if b.bus_type == "Slack"]
        if not slack_buses:
            self._warn("No Slack bus found. "
                       "At least one bus must be type 'Slack'.")
            return

        try:
            self.circuit.calc_ybus()
            results = self.solver.solution(self.circuit, mode="powerflow")
            self._display_powerflow(results)
        except Exception as e:
            self._warn(f"Power flow failed:\n{e}")

    # ------------------------------------------------------------------ #
    #  Fault Study
    # ------------------------------------------------------------------ #

    def run_fault(self, parent_widget=None):
        """Ask for fault settings then run symmetrical fault study."""

        if not self.circuit.buses:
            self._warn("No buses defined. Build a circuit first.")
            return

        # Open fault settings dialog
        dlg = FaultDialog(self.circuit, parent=parent_widget)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        vals = dlg.get_values()

        try:
            self.circuit.calc_ybus()
            results = self.solver.solution(
                self.circuit,
                mode="fault",
                fault_bus=vals["fault_bus"],
                v_prefault=vals["v_prefault"]
            )
            self._display_fault(results)
        except Exception as e:
            self._warn(f"Fault study failed:\n{e}")

    # ------------------------------------------------------------------ #
    #  Result formatters
    # ------------------------------------------------------------------ #

    def _display_powerflow(self, results: dict):
        """Format power flow results and write to the results panel."""
        lines = []
        conv  = "YES" if results["converged"] else "NO"

        lines.append("=== POWER FLOW ===")
        lines.append(f"Converged: {conv}\n")
        lines.append(f"{'Bus':<12} {'|V| (pu)':>10} {'δ (deg)':>10} "
                     f"{'P (pu)':>10} {'Q (pu)':>10}")
        lines.append("-" * 55)

        for name, r in results["bus_results"].items():
            lines.append(
                f"{name:<12} {r['vpu']:>10.5f} {r['delta']:>10.4f} "
                f"{r['p_calc_pu']:>10.5f} {r['q_calc_pu']:>10.5f}"
            )

        self.results_box.setPlainText("\n".join(lines))

    def _display_fault(self, results: dict):
        """Format fault study results and write to the results panel."""
        lines = []

        lines.append("=== FAULT STUDY ===")
        lines.append(f"Fault bus    : {results['fault_bus']}")
        lines.append(f"Pre-fault V  : {results['v_prefault_pu']} pu")
        lines.append(f"Z_nn         : {results['z_nn']:.5f} pu")
        lines.append(f"I_fault''    : {results['i_fault_pu']:.5f} pu")
        lines.append(f"|I_fault''|  : {abs(results['i_fault_pu']):.5f} pu\n")
        lines.append(f"{'Bus':<14} {'|E_k| (pu)':>10}")
        lines.append("-" * 26)

        for bus, ek in results["bus_voltages"].items():
            lines.append(f"{bus:<14} {abs(ek):>10.5f}")

        self.results_box.setPlainText("\n".join(lines))

    def _warn(self, message: str):
        """Show a warning popup."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Warning")
        msg.setText(message)
        msg.exec()