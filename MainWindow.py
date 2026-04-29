from PyQt6.QtWidgets import (QMainWindow, QSplitter, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QTextEdit, QToolBar,
                             QSizePolicy)
from PyQt6.QtCore import Qt, QSize

from circuit import Circuit
from SchematicScene import SchematicScene, SchematicView
from DraggableButton import DraggableButton
from CircuitController import CircuitController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Power System Simulator")
        self.setMinimumSize(1100, 700)

        # Circuit holds all buses, lines, generators, loads
        self.circuit = Circuit("My Circuit")

        # Build the three panels
        palette = self._build_palette()
        canvas  = self._build_canvas()
        results = self._build_results()

        # Splitter holds all three panels side by side
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(palette)
        splitter.addWidget(canvas)
        splitter.addWidget(results)

        # Set starting widths: palette=160, canvas=fills rest, results=220
        splitter.setSizes([160, 720, 220])

        # Lock the sidebars so they can shrink but not disappear
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(2, False)

        self.setCentralWidget(splitter)

        # Toolbar only — no menu bar
        self._build_toolbar()


        # Controller — wires run buttons to the solver
        self.controller = CircuitController(
            self.circuit, self.results_box, self.scene
        )

    # ------------------------------------------------------------------ #
    #  Panel builders
    # ------------------------------------------------------------------ #

    def _build_palette(self):
        """Left sidebar — one button per component type."""
        panel = QWidget()
        panel.setFixedWidth(160)

        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 12, 8, 12)

        layout.addWidget(QLabel("Components"))

        for component in ["Bus", "Generator", "Load",
                          "Transmission Line", "Transformer"]:
            btn = DraggableButton(component)
            btn.setFixedHeight(36)
            layout.addWidget(btn)

        layout.addStretch()
        return panel

    def _build_canvas(self):
        """Centre panel — the real schematic canvas."""
        self.scene = SchematicScene(self.circuit)
        self.view  = SchematicView(self.scene)
        return self.view

    def _build_results(self):
        """Right sidebar — read-only text area for solver output."""
        panel = QWidget()
        panel.setFixedWidth(220)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(6)

        layout.addWidget(QLabel("Results"))

        self.results_box = QTextEdit()
        self.results_box.setReadOnly(True)
        self.results_box.setPlaceholderText("Run a solver to see results...")
        layout.addWidget(self.results_box)

        return panel

    # ------------------------------------------------------------------ #
    #  Toolbar
    # ------------------------------------------------------------------ #

    def _build_toolbar(self):
        """Run buttons on the left, New button pushed to the right."""
        toolbar = QToolBar("Run Tools")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        # Helper to build a small square symbol button
        def icon_btn(symbol, color, hover, pressed, slot):
            btn = QPushButton(symbol)
            btn.setFixedSize(32, 32)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border-radius: 6px;
                    font-size: 15px;
                }}
                QPushButton:hover  {{ background-color: {hover}; }}
                QPushButton:pressed{{ background-color: {pressed}; }}
            """)
            btn.clicked.connect(slot)
            return btn

        # Power Flow — label + green button

        gapstart= QWidget()
        gapstart.setFixedWidth(6)
        toolbar.addWidget(gapstart)

        toolbar.addWidget(QLabel("Power Flow"))

        gap1= QWidget()
        gap1.setFixedWidth(6)
        toolbar.addWidget(gap1)

        toolbar.addWidget(icon_btn("▶", "#2e7d32", "#388e3c", "#1b5e20",
                                   self._on_run_powerflow))

        gaptoolbar1 = QWidget()
        gaptoolbar1.setFixedWidth(6)
        toolbar.addWidget(gaptoolbar1)

        toolbar.addSeparator()

        gaptoolbar2 = QWidget()
        gaptoolbar2.setFixedWidth(6)
        toolbar.addWidget(gaptoolbar2)

        # Fault Study — label + orange button
        toolbar.addWidget(QLabel("Fault Study"))

        gap2= QWidget()
        gap2.setFixedWidth(6)
        toolbar.addWidget(gap2)
        toolbar.addWidget(icon_btn("⚡", "#e65100", "#ef6c00", "#bf360c",
                                   self._on_run_fault))

        # Spacer — pushes New to the far right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding,
                             QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        # New — label + blue button
        toolbar.addWidget(QLabel("New"))

        gap3= QWidget()
        gap3.setFixedWidth(6)
        toolbar.addWidget(gap3)

        toolbar.addWidget(icon_btn("＋", "#1565c0", "#1976d2", "#0d47a1",
                                   self._on_new))


        gapend= QWidget()
        gapend.setFixedWidth(6)
        toolbar.addWidget(gapend)




    # ------------------------------------------------------------------ #
    #  Slots (stubs — filled in later)
    # ------------------------------------------------------------------ #
    def _on_new(self):
        self.circuit = Circuit("My Circuit")
        self.results_box.clear()
        self.scene.clear()
        self.scene.bus_visuals = {}
        self.scene.circuit = self.circuit
        self.controller.circuit = self.circuit

    def _on_run_powerflow(self):
        self.controller.run_powerflow()

    def _on_run_fault(self):
        self.controller.run_fault(parent_widget=self)


# ------------------------------------------------------------------ #
#  Entry point
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())