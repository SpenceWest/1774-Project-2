from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QColor

from PropertiesDialog import PropertiesDialog
from BusVisual import BusVisual
from GeneratorVisual import GeneratorVisual
from LoadVisual import LoadVisual
from TransmissionLineVisual import TransmissionLineVisual
from TransformerVisual import TransformerVisual


class SchematicScene(QGraphicsScene):
    def __init__(self, circuit, parent=None):
        super().__init__(parent)

        # Reference to the circuit data model
        self.circuit = circuit

        # Maps bus name → BusVisual so Generator/Load can find their bus
        self.bus_visuals = {}

        # Canvas size — how big the drawing area is
        self.setSceneRect(0, 0, 2000, 2000)

        # Grid spacing in pixels
        self.grid_size = 30

    # ------------------------------------------------------------------ #
    #  Grid drawing
    # ------------------------------------------------------------------ #

    def drawBackground(self, painter, rect):
        """Draws the background color then the line grid."""
        # Fill background first
        painter.fillRect(rect, QColor(245, 245, 245))

        # Light gray grid lines
        grid_pen = QPen(QColor(210, 210, 210))
        grid_pen.setWidthF(0.5)
        painter.setPen(grid_pen)

        # Find the first grid line inside the visible rect
        left   = int(rect.left())   - (int(rect.left())   % self.grid_size)
        top    = int(rect.top())    - (int(rect.top())    % self.grid_size)
        right  = int(rect.right())
        bottom = int(rect.bottom())

        # Draw vertical lines
        x = left
        while x <= right:
            painter.drawLine(x, top, x, bottom)
            x += self.grid_size

        # Draw horizontal lines
        y = top
        while y <= bottom:
            painter.drawLine(left, y, right, y)
            y += self.grid_size

    # ------------------------------------------------------------------ #
    #  Drag and drop
    # ------------------------------------------------------------------ #

    def dragEnterEvent(self, event):
        """Accept the drag if it carries a component type string."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Keep accepting while the user moves over the canvas."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Open PropertiesDialog then place the component on the canvas."""
        if not event.mimeData().hasText():
            event.ignore()
            return

        component_type = event.mimeData().text()

        # Snap drop position to grid
        raw = event.scenePos()
        x   = round(raw.x() / self.grid_size) * self.grid_size
        y   = round(raw.y() / self.grid_size) * self.grid_size

        event.acceptProposedAction()

        # Use QTimer so the drop event fully finishes before dialog opens
        # This fixes Windows focus issues
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(50, lambda: self._open_dialog(component_type, x, y))

    def _open_dialog(self, component_type: str, x: float, y: float):
        """Opens PropertiesDialog after the drop event has finished."""
        parent_widget = self.views()[0] if self.views() else None
        dlg = PropertiesDialog(component_type, self.circuit,
                               parent=parent_widget)
        dlg.raise_()
        dlg.activateWindow()

        if dlg.exec() != PropertiesDialog.DialogCode.Accepted:
            return

        vals = dlg.get_values()
        self._add_to_circuit(component_type, vals, x, y)

    # ------------------------------------------------------------------ #
    #  Add component to circuit + place visual on canvas
    # ------------------------------------------------------------------ #

    def _add_to_circuit(self, component_type: str, vals: dict,
                        x: float, y: float):
        """Create the data object in Circuit and place its Visual on canvas."""

        if component_type == "Bus":
            self.circuit.add_bus(
                vals["name"],
                float(vals["nominal_kv"]),
                bus_type=vals["bus_type"]
            )
            # Create and place the BusVisual
            bus_obj    = self.circuit.buses[vals["name"]]
            bus_visual = BusVisual(bus_obj)
            self.addItem(bus_visual)
            bus_visual.setPos(x, y)

            # Store so Generator/Load can find it later
            self.bus_visuals[vals["name"]] = bus_visual

        elif component_type == "Generator":
            self.circuit.add_generator(
                vals["name"],
                vals["bus_name"],
                float(vals["voltage_setpoint"]),
                float(vals["mw_setpoint"]),
                x_subtransient=float(vals["x_subtransient"])
            )
            # Attach GeneratorVisual to its bus visual
            bus_visual = self.bus_visuals.get(vals["bus_name"])
            if bus_visual:
                gen_obj    = self.circuit.generators[vals["name"]]
                gen_visual = GeneratorVisual(gen_obj, bus_visual)
                self.addItem(gen_visual)

        elif component_type == "Load":
            self.circuit.add_load_element(
                vals["name"],
                vals["bus_name"],
                float(vals["mw"]),
                float(vals["mvar"])
            )
            # Attach LoadVisual to its bus visual
            bus_visual = self.bus_visuals.get(vals["bus_name"])
            if bus_visual:
                load_obj    = self.circuit.loads[vals["name"]]
                load_visual = LoadVisual(load_obj, bus_visual)
                self.addItem(load_visual)

        elif component_type == "Transmission Line":
            self.circuit.add_transmission_line(
                vals["name"],
                vals["bus1_name"],
                vals["bus2_name"],
                float(vals["r"]),
                float(vals["x"]),
                float(vals["g"]),
                float(vals["b"])
            )
            # Connect the two bus visuals with a line
            bus1_visual = self.bus_visuals.get(vals["bus1_name"])
            bus2_visual = self.bus_visuals.get(vals["bus2_name"])
            if bus1_visual and bus2_visual:
                line_obj    = self.circuit.transmission_lines[vals["name"]]
                line_visual = TransmissionLineVisual(line_obj,
                                                     bus1_visual, bus2_visual)
                self.addItem(line_visual)
                # Register after addItem so scenePos() is valid
                bus1_visual.connected_lines.append(line_visual)
                bus2_visual.connected_lines.append(line_visual)

        elif component_type == "Transformer":
            self.circuit.add_transformer(
                vals["name"],
                vals["bus1_name"],
                vals["bus2_name"],
                float(vals["r"]),
                float(vals["x"])
            )
            # Connect the two bus visuals with a transformer symbol
            bus1_visual = self.bus_visuals.get(vals["bus1_name"])
            bus2_visual = self.bus_visuals.get(vals["bus2_name"])
            if bus1_visual and bus2_visual:
                transformer_obj    = self.circuit.transformers[vals["name"]]
                transformer_visual = TransformerVisual(transformer_obj,
                                                       bus1_visual, bus2_visual)
                self.addItem(transformer_visual)
                # Register after addItem so scenePos() is valid
                bus1_visual.connected_lines.append(transformer_visual)
                bus2_visual.connected_lines.append(transformer_visual)

class SchematicView(QGraphicsView):
    def __init__(self, scene: SchematicScene, parent=None):
        super().__init__(scene, parent)

        # Enable drop events on the view
        self.setAcceptDrops(True)

        # No scroll bar jumping when items are added near the edge
        self.setDragMode(QGraphicsView.DragMode.NoDrag)


# ------------------------------------------------------------------ #
#  Quick test — run this file directly to see the canvas
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from circuit import Circuit

    app = QApplication(sys.argv)

    circuit = Circuit("Test")
    scene   = SchematicScene(circuit)
    view    = SchematicView(scene)
    view.setWindowTitle("Schematic Canvas Test")
    view.resize(900, 600)
    view.show()

    sys.exit(app.exec())