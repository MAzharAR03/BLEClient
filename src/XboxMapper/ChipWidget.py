from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QDoubleSpinBox, QPushButton


class ChipWidget(QFrame):
    removed = Signal(object)
    changed = Signal()

    def __init__(self, chip, slot_type, parent = None):
        super().__init__(parent)
        self.chip = chip
        self.slot_type = slot_type
        self._build()

    def _build(self):
        self.setFrameShape(QFrame.StyledPanel)
        input = self.chip["input"]
        is_float = input.startswith("float:")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6,3,4,3)
        layout.setSpacing(4)

        label = QLabel(input.split(":",1)[-1])
        label.setStyleSheet("font-size: 12px;")
        layout.addWidget(label)

        if is_float and self.slot_type in ("axis","trigger"):
            layout.addWidget(QLabel("scale:"))
            self.spin = QDoubleSpinBox()
            self.spin.setRange(0.001,100.0)
            self.spin.setDecimals(4)
            self.spin.setSingleStep(0.1)
            self.spin.setValue(self.chip.get("scale") or 1.5708)
            self.spin.setFixedWidth(800)
            self.spin.valueChanged.connect(self._on_scale_changed)
            layout.addWidget(self.spin)
        elif not is_float and self.slot_type in ("axis","trigger"):
            layout.addWidget(QLabel("value:"))
            self.spin = QDoubleSpinBox()
            self.spin.setRange(0.0,1.0)
            self.spin.setDecimals(2)
            self.spin.setSingleStep(0.1)
            self.spin.setValue(self.chip.get("value") or 1.0)
            self.spin.setFixedWidth(60)
            self.spin.valueChanged.connect(self._on_value_changed)
            layout.addWidget(self.spin)
        else:
            self.spin = None

        remove_button = QPushButton("x")
        remove_button.setFixedSize(18,18)
        remove_button.setFlat(True)
        remove_button.setCursor(Qt.PointingHandCursor)
        remove_button.clicked.connect(lambda: self.removed.emit(self))
        layout.addWidget(remove_button)

    def _on_scale_changed(self, value):
        self.chip["scale"] = value
        self.changed.emit()

    def _on_value_changed(self, value):
        self.chip["value"] = value
        self.changed.emit()