from Load import Load
from BusVisual import BusVisual

class LoadVisual(QGraphicsItem):
    def __init__(self, load: Load, bus1_visual: BusVisual):
        super().__init__()
        self.load = load
        self.bus1_visual = bus_visual
        self.setParentItem(bus_visual)  # automatically moves with the bus


    def boundingRect(self):
        return QRectF(0, 0, 20, 20)   # fixed size circle/square

    def paint(self, painter, option, widget): # Makes the shape for the Load bases off the connected buses
        painter.drawEllipse(0, 0, 20, 20)
        painter.drawText(0, -5, self.laod.name)


]