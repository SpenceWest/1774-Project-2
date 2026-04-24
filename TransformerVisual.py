from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QPen, QColor, QFont

from Transformer import Transformer
from BusVisual import BusVisual


class TransformerVisual(QGraphicsItem):
    def __init__(self, transformer: Transformer,
                 bus1_visual: BusVisual, bus2_visual: BusVisual):
        super().__init__()
        self.transformer = transformer
        self.bus1_visual = bus1_visual
        self.bus2_visual = bus2_visual

        # Register with both buses so we redraw when either moves
        self.bus1_visual.connected_lines.append(self)
        self.bus2_visual.connected_lines.append(self)

    def boundingRect(self):
        p1 = self.bus1_visual.scenePos()
        p2 = self.bus2_visual.scenePos()
        return QRectF(p1, p2).normalized()

    def paint(self, painter, option, widget):
        p1 = self.bus1_visual.scenePos()
        p2 = self.bus2_visual.scenePos()

        # Midpoint of the line
        mid_x = (p1.x() + p2.x()) / 2
        mid_y = (p1.y() + p2.y()) / 2

        pen = QPen(QColor(30, 30, 30))
        pen.setWidth(2)
        painter.setPen(pen)

        # Line from bus1 to first circle
        painter.drawLine(p1.x(), p1.y(), int(mid_x) - 12, int(mid_y))

        # Two circles in the middle — transformer symbol
        painter.drawEllipse(int(mid_x) - 22, int(mid_y) - 10, 20, 20)
        painter.drawEllipse(int(mid_x) - 2,  int(mid_y) - 10, 20, 20)

        # Line from second circle to bus2
        painter.drawLine(int(mid_x) + 18, int(mid_y), int(p2.x()), int(p2.y()))

        # Name label above midpoint
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QPen(QColor(150, 0, 0)))
        painter.drawText(int(mid_x) - 10, int(mid_y) - 15,
                         self.transformer.name)

    def update_position(self):
        """Called by buses when they move — forces a redraw."""
        self.prepareGeometryChange()
        self.update()
