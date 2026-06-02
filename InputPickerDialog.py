from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QAbstractItemView, QListWidgetItem, \
    QDialogButtonBox


class InputPickerDialog(QDialog):
    def __init__(self, available_inputs, slot_type, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Add Input")
        self.setMinimumWidth(300)
        self._slot_type = slot_type
        self._selected = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Choose an input to add: "))

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        for input in available_inputs:
            is_float = input.startswith("float:")
            if is_float and slot_type not in ("axis","trigger"):
                continue
            if input == "toggle:pause" and slot_type in ("axis","trigger"):
                continue
            item = QListWidgetItem(input.split(":",1)[-1])
            item.setData(Qt.UserRole, input)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)

        self.list_widget.itemDoubleClicked.connect(self._accept)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _accept(self):
        items = self.list_widget.selectedItems()
        if not items:
            return
        self._selected = items[0].data(Qt.UserRole)
        self.accept()

    def selected_input(self) -> str | None:
        return self._selected