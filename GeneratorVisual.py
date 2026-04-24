from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QPen, QColor, QFont

from Generator import Generator
from BusVisual import BusVisual


class GeneratorVisual(QGraphicsItem):
    def __init__(self, generator: Generator, bus1_visual: BusVisual):
        super().__init__()
        self.generator   = generator
        self.bus1_visual = bus1_visual

        # Attach to bus so it moves with it
        self.setParentItem(bus1_visual)

        # Offset so it sits below the bus bar
        self.setPos(30, 15)

    def boundingRect(self):
        return QRectF(-5, -5, 30, 45)

    def paint(self, painter, option, widget):
        # Circle symbol
        pen = QPen(QColor(30, 30, 30))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawEllipse(0, 10, 20, 20)

        # Small vertical line connecting to bus bar above
        painter.drawLine(10, 0, 10, 10)

        # G label inside circle
        painter.setFont(QFont("Arial", 7))
        painter.drawText(0, 10, 20, 20,
                         0x0084,   # AlignCenter flag
                         "G")

        # Generator name above
        painter.setFont(QFont("Arial", 7))
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.drawText(-5, -2, self.generator.name)