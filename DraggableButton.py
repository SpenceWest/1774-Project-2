from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QMimeData, QPoint
from PyQt6.QtGui import QDrag, QPixmap, QPainter, QPen, QColor, QBrush


class DraggableButton(QPushButton):
    def __init__(self, component_type: str, parent=None):
        super().__init__(component_type, parent)
        self.component_type = component_type

    def mouseMoveEvent(self, event):
        """Start a drag when the user clicks and moves."""
        if event.buttons() != Qt.MouseButton.LeftButton:
            return

        # Package the component type as text mime data
        mime_data = QMimeData()
        mime_data.setText(self.component_type)

        # Build the drag object and attach the preview pixmap
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(self._make_pixmap())
        drag.setHotSpot(QPoint(25, 25))  # centre of the 50x50 pixmap

        drag.exec(Qt.DropAction.CopyAction)

    # ------------------------------------------------------------------ #
    #  Shape preview pixmaps
    # ------------------------------------------------------------------ #

    def _make_pixmap(self) -> QPixmap:
        """Draw a small preview shape matching the component's visual."""
        size    = 50
        pixmap  = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor(50, 50, 50))
        pen.setWidth(2)
        painter.setPen(pen)

        if self.component_type == "Bus":
            self._draw_bus(painter, size)

        elif self.component_type == "Generator":
            self._draw_generator(painter, size)

        elif self.component_type == "Load":
            self._draw_load(painter, size)

        elif self.component_type == "Transmission Line":
            self._draw_transmission_line(painter, size)

        elif self.component_type == "Transformer":
            self._draw_transformer(painter, size)

        painter.end()
        return pixmap

    def _draw_bus(self, painter, size):
        """Horizontal bar across the middle."""
        mid = size // 2
        painter.drawLine(5, mid, size - 5, mid)
        # Small vertical tick in the centre
        painter.drawLine(mid, mid - 8, mid, mid + 8)

    def _draw_generator(self, painter, size):
        """Circle with a G inside."""
        margin = 6
        painter.drawEllipse(margin, margin, size - margin * 2, size - margin * 2)
        painter.drawText(0, 0, size, size, Qt.AlignmentFlag.AlignCenter, "G")

    def _draw_load(self, painter, size):
        """Triangle pointing downward — standard load symbol."""
        mid = size // 2
        # Vertical line from top to triangle
        painter.drawLine(mid, 4, mid, 16)
        # Triangle
        points = [
            QPoint(mid - 12, 16),
            QPoint(mid + 12, 16),
            QPoint(mid, size - 6),
        ]
        from PyQt6.QtGui import QPolygon
        painter.drawPolygon(QPolygon(points))

    def _draw_transmission_line(self, painter, size):
        """Diagonal line with dots at each end."""
        painter.drawLine(6, 6, size - 6, size - 6)
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.drawEllipse(3, 3, 7, 7)
        painter.drawEllipse(size - 10, size - 10, 7, 7)

    def _draw_transformer(self, painter, size):
        """Two circles side by side."""
        r = 10
        mid_y = size // 2
        # Left circle
        painter.drawEllipse(4, mid_y - r, r * 2, r * 2)
        # Right circle
        painter.drawEllipse(size - 4 - r * 2, mid_y - r, r * 2, r * 2)
        # Line on each side
        painter.drawLine(4 + r, mid_y, 4, mid_y)
        painter.drawLine(size - 4 - r, mid_y, size - 4, mid_y)