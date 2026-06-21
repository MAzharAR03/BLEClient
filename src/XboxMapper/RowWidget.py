from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QDialog

from src.XboxMapper.ChipWidget import ChipWidget
from src.XboxMapper.InputPickerDialog import InputPickerDialog


class RowWidget(QWidget):
    changed = Signal()
    def __init__(self, key, label, slot_type, chips, available_inputs, parent = None):
        super().__init__(parent)
        self.key = key
        self.slot_type = slot_type
        self._chips = chips
        self._available_inputs = available_inputs

        self._outer = QHBoxLayout(self)
        self._outer.setContentsMargins(0,2,0,2)
        self._outer.setSpacing(8)

        label = QLabel(label)
        label.setFixedWidth(60)
        label.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        label.setStyleSheet("font-weight: bold; font-size: 13px")
        self._outer.addWidget(label)

        self._chips_layout = QHBoxLayout()
        self._chips_layout.setContentsMargins(0,0,0,0)
        self._chips_layout.setSpacing(4)
        self._chips_layout.setAlignment(Qt.AlignLeft)
        self._outer.addLayout(self._chips_layout)

        add_button = QPushButton("+ Add")
        add_button.setFixedWidth(60)
        add_button.setCursor(Qt.PointingHandCursor)
        add_button.clicked.connect(self._add_input)
        self._outer.addWidget(add_button)
        self._outer.addStretch()

        self._refresh_chips()

    def _refresh_chips(self):
        while self._chips_layout.count():
            item = self._chips_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for chip_data in self._chips:
            chip_widgets = ChipWidget(chip_data, self.slot_type)
            chip_widgets.removed.connect(self._remove_chip)
            chip_widgets.changed.connect(self.changed)
            self._chips_layout.addWidget(chip_widgets)

    def _add_input(self):
        dialog = InputPickerDialog(self._available_inputs, self.slot_type, self)
        if dialog.exec() != QDialog.Accepted:
            return
        input = dialog.selected_input()
        if not input:
            return
        chip = {"input": input, "scale": None, "value": None}
        if input.startswith("float:") and self.slot_type in ("axis","trigger"):
            chip["scale"] = 1.5708
        elif not input.startswith("float:") and self.slot_type in ("axis", "trigger"):
            chip["value"] = 1.0
        self._chips.append(chip)
        self._refresh_chips()
        self.changed.emit()

    def _remove_chip(self, chip_widget):
        self._chips.remove(chip_widget.chip)
        self._refresh_chips()
        self.changed.emit()

    def update_inputs(self,available_inputs):
        self._available_inputs = available_inputs

    def get_chips(self) -> list:
        return self._chips