from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QPen, QColor, QFont

from TransmissionLine import TransmissionLine
from BusVisual import BusVisual


class TransmissionLineVisual(QGraphicsItem):
    def __init__(self, transmission_line: TransmissionLine,
                 bus1_visual: BusVisual, bus2_visual: BusVisual):
        super().__init__()
        self.transmission_line = transmission_line
        self.bus1_visual       = bus1_visual
        self.bus2_visual       = bus2_visual

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

        # Draw the line
        pen = QPen(QColor(30, 30, 30))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(p1, p2)

        # Name label in the middle
        mid_x = (p1.x() + p2.x()) / 2
        mid_y = (p1.y() + p2.y()) / 2
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QPen(QColor(0, 0, 150)))
        painter.drawText(int(mid_x), int(mid_y), self.transmission_line.name)

    def update_position(self):
        """Called by buses when they move — forces a redraw."""
        self.prepareGeometryChange()
        self.update()