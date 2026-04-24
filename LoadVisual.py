from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import QRectF, QPoint
from PyQt6.QtGui import QPen, QColor, QFont, QPolygon

from Load import Load
from BusVisual import BusVisual


class LoadVisual(QGraphicsItem):
    def __init__(self, load: Load, bus1_visual: BusVisual):
        super().__init__()
        self.load        = load
        self.bus1_visual = bus1_visual

        # Attach to bus so it moves with it
        self.setParentItem(bus1_visual)

        # Offset so it sits below the bus bar
        self.setPos(50, 15)

    def boundingRect(self):
        return QRectF(-5, -5, 30, 45)

    def paint(self, painter, option, widget):
        pen = QPen(QColor(30, 30, 30))
        pen.setWidth(2)
        painter.setPen(pen)

        # Small vertical line connecting to bus bar above
        painter.drawLine(10, 0, 10, 10)

        # Triangle pointing downward — standard load symbol
        points = [
            QPoint(0,  10),
            QPoint(20, 10),
            QPoint(10, 30),
        ]
        painter.drawPolygon(QPolygon(points))

        # Load name above
        painter.setFont(QFont("Arial", 7))
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.drawText(-5, -2, self.load.name)
