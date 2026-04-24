from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QPen, QColor, QFont

from Bus import Bus


class BusVisual(QGraphicsItem):
    def __init__(self, bus: Bus):
        super().__init__()
        self.bus = bus

        self.width  = 80
        self.height = 10

        # Lines and transformers register here so they redraw when bus moves
        self.connected_lines = []

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

    def boundingRect(self):
        # Extra padding above for the name label
        return QRectF(-5, -20, self.width + 10, self.height + 25)

    def paint(self, painter, option, widget):
        # Draw the bus bar as a thick horizontal line
        pen = QPen(QColor(30, 30, 30))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(0, self.height // 2,
                         self.width, self.height // 2)

        # Draw the bus name above
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.drawText(0, -5, self.bus.name)

    def itemChange(self, change, value):
        # When the bus moves, tell all connected lines to redraw
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            for line in self.connected_lines:
                line.update_position()
        return super().itemChange(change, value)