from Bus import Bus
class BusVisual(QGraphicsItem):
    def __init__(self, bus: Bus):
        super().__init__()
        self.bus = bus

        self.width = 80
        self.height = 10
        self.connected_lines = []

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable) # Makes the object movable
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable) # Select object
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges) # How it knows what element it is connected to

    def boundingRect(self):  # This defines the area where you click
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget): # Makes the shape for the bus
        # draw the bus bar
        # draw the name label

        painter.drawLine(self.width//2, 0, self.width//2, self.height)
        painter.drawText(0, -5, self.bus.name)

    def itemChange(self, change, value): # If bus is moved, this code updates the lines
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            for line in self.connected_lines:
                line.update_position()  # Redraw line


        return super().itemChange(change, value)