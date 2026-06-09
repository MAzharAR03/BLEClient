from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox,
    QSpinBox, QLineEdit, QPushButton, QScrollArea
)
from constants import SCENE_WIDTH, SCENE_HEIGHT

class ImagePropertiesSidebar(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._updating = False

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        url_group = QGroupBox("Image")
        url_form = QFormLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL")
        url_form.addRow("URL: ", self.url_input)
        url_group.setLayout(url_form)

        pos_group = QGroupBox("Position")
        pos_form = QFormLayout()
        self.x_spin = QSpinBox();
        self.x_spin.setRange(0, SCENE_WIDTH)
        self.y_spin = QSpinBox();
        self.y_spin.setRange(0, SCENE_HEIGHT)
        pos_form.addRow("X", self.x_spin)
        pos_form.addRow("Y", self.y_spin)
        pos_group.setLayout(pos_form)

        size_group = QGroupBox("Size")
        size_form = QFormLayout()
        self.width_spin = QSpinBox();
        self.width_spin.setRange(1, SCENE_WIDTH)
        self.height_spin = QSpinBox();
        self.height_spin.setRange(1, SCENE_HEIGHT)
        size_form.addRow("Width", self.width_spin)
        size_form.addRow("Height", self.height_spin)
        size_group.setLayout(size_form)

        self.apply_btn = QPushButton("Apply")

        layout.addWidget(url_group)
        layout.addWidget(pos_group)
        layout.addWidget(size_group)
        layout.addWidget(self.apply_btn)
        layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(inner)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self.apply_btn.clicked.connect(self.on_apply)

    def populate(self, img):
        self._updating = True
        self.url_input.setText(img.url)
        self.x_spin.setValue(int(img.pos().x()))
        self.y_spin.setValue(int(img.pos().y()))
        self.width_spin.setValue(int(img.img_w))
        self.height_spin.setValue(int(img.img_h))
        self._updating = False

    def on_apply(self):
        self.apply_to_selected()

    def apply_to_selected(self):
        pass

