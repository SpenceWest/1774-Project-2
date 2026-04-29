from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import QRectF, QPointF
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

    def _get_points(self):
        """Get bus positions in scene coordinates."""
        p1 = self.bus1_visual.pos()
        p2 = self.bus2_visual.pos()
        return p1, p2

    def boundingRect(self):
        p1, p2 = self._get_points()
        return QRectF(p1, p2).normalized().adjusted(-30, -30, 30, 30)

    def paint(self, painter, option, widget):
        p1, p2 = self._get_points()

        mid_x = (p1.x() + p2.x()) / 2
        mid_y = (p1.y() + p2.y()) / 2

        pen = QPen(QColor(30, 30, 30))
        pen.setWidth(2)
        painter.setPen(pen)

        # Line from bus1 to first circle
        painter.drawLine(p1, QPointF(mid_x - 12, mid_y))

        # Two circles in the middle — transformer symbol
        painter.drawEllipse(int(mid_x) - 22, int(mid_y) - 10, 20, 20)
        painter.drawEllipse(int(mid_x) - 2,  int(mid_y) - 10, 20, 20)

        # Line from second circle to bus2
        painter.drawLine(QPointF(mid_x + 18, mid_y), p2)

        # Name label above midpoint
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QPen(QColor(150, 0, 0)))
        painter.drawText(int(mid_x) - 10, int(mid_y) - 15,
                         self.transformer.name)

    def update_position(self):
        """Called by buses when they move — forces a redraw."""
        self.prepareGeometryChange()
        self.update()