from TransmissionLine import TransmissionLine
from BusVisual import BusVisual

class TransmissionLineVisual(QGraphicsItem):
    def __init__(self, transmissionline: TransmissionLine, bus1_visual: BusVisual, bus2_visual: BusVisual):
        super().__init__()
        self.transmissionLine = transmissionline
        self.bus1_visual = bus1_visual
        self.bus2_visual = bus2_visual

        # Register itself with both buses immediately
        self.bus1_visual.connected_lines.append(self)
        self.bus2_visual.connected_lines.append(self)




    def boundingRect(self): # Makes this only valid if it connected to buses
        p1 = self.bus1_visual.scenePos()
        p2 = self.bus2_visual.scenePos()
        return QRectF(p1, p2).normalized()

    def paint(self, painter, option, widget): # Makes the shape for the line bases off the connected buses
        p1 = self.bus1_visual.scenePos()
        p2 = self.bus2_visual.scenePos()
        painter.drawLine(p1, p2)

        # Label in the middle
        mid_x = (p1.x() + p2.x()) / 2
        mid_y = (p1.y() + p2.y()) / 2
        painter.drawText(mid_x, mid_y, self.transmissionLine.name)

    def update_position(self):
        self.prepareGeometryChange()  # tells Qt the shape is about to change
        self.update()