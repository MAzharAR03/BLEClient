from PySide6.QtGui import QColor, Qt
from PySide6.QtWidgets import QWidget, QColorDialog, QComboBox, QFormLayout, QGroupBox, QSpinBox, QPushButton, \
    QLineEdit, QVBoxLayout, QSlider, QScrollArea

from CustomButton import CustomButton
from constants import SCENE_HEIGHT, SCENE_WIDTH

class PropertiesSidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._updating = False
        self._inner = QWidget()
        layout = QVBoxLayout(self._inner)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        pos_group = QGroupBox("Position")
        pos_form = QFormLayout()
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0,SCENE_WIDTH)
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0,SCENE_HEIGHT)
        pos_form.addRow("X", self.x_spin)
        pos_form.addRow("Y", self.y_spin)
        pos_group.setLayout(pos_form)

        size_group = QGroupBox("Size")
        size_form = QFormLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, SCENE_WIDTH)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, SCENE_HEIGHT)
        size_form.addRow("Width", self.width_spin)
        size_form.addRow("Height", self.height_spin)
        size_group.setLayout(size_form)

        shape_group = QGroupBox("Shape")
        shape_form = QFormLayout()
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["Rounded Rectangle","Rectangle","Circle"])
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(0,100)
        self.radius_spin.setValue(0)
        shape_form.addRow("Shape",self.shape_combo)
        shape_form.addRow("Radius", self.radius_spin)
        shape_group.setLayout(shape_form)

        color_group = QGroupBox("Color")
        color_form = QFormLayout()

        self.color_input = QLineEdit("#000000")
        self.color_preview = QWidget()
        self.color_preview.setStyleSheet("background-color: #ffffff;")
        self.color_input.textChanged.connect(lambda text: self.on_color_changed(text, self.color_preview))

        self.color_pick_btn = QPushButton("Pick Color")
        self.color_pick_btn.clicked.connect(lambda: self.open_color_picker(self.color_input))

        color_form.addRow("Hex", self.color_input)
        color_form.addRow("Preview", self.color_preview)
        color_form.addRow("Picker", self.color_pick_btn)

        color_group.setLayout(color_form)


        label_group = QGroupBox("Label")
        label_form = QFormLayout()
        self.text_input = QLineEdit()

        self.font_color_input = QLineEdit("#ffffff")
        self.font_color_preview = QWidget()
        self.font_color_preview.setStyleSheet("background-color: #ffffff;")
        self.font_color_pick_btn = QPushButton("Pick Color")
        self.font_color_pick_btn.clicked.connect(lambda: self.open_color_picker(self.font_color_input))
        self.font_color_input.textChanged.connect(lambda text: self.on_color_changed(text, self.font_color_preview))

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(7,72)
        self.font_size_spin.setValue(14)
        label_form.addRow("Text",self.text_input)
        label_form.addRow("Font Color", self.font_color_input)
        label_form.addRow("Preview", self.font_color_preview)
        label_form.addRow("Picker", self.font_color_pick_btn)
        label_form.addRow("Font Size", self.font_size_spin)
        label_group.setLayout(label_form)

        image_group = QGroupBox("Button Image")
        image_form = QFormLayout()
        self.image_url_input = QLineEdit()
        self.image_url_input.setPlaceholderText("URL")
        image_form.addRow("URL", self.image_url_input)
        image_group.setLayout(image_form)



        layout.addWidget(pos_group)
        layout.addWidget(size_group)
        layout.addWidget(shape_group)
        layout.addWidget(color_group)
        layout.addWidget(label_group)
        layout.addWidget(image_group)
        layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(self._inner)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self.x_spin.valueChanged.connect(self.on_property_changed)
        self.y_spin.valueChanged.connect(self.on_property_changed)
        self.width_spin.valueChanged.connect(self.on_property_changed)
        self.height_spin.valueChanged.connect(self.on_property_changed)
        self.shape_combo.currentTextChanged.connect(self.on_property_changed)
        self.radius_spin.valueChanged.connect(self.on_property_changed)
        self.text_input.textChanged.connect(self.on_property_changed)
        self.font_size_spin.valueChanged.connect(self.on_property_changed)
        self.image_url_input.textChanged.connect(self.on_property_changed)

    def populate(self, button: CustomButton):
        self._updating = True
        self.x_spin.setValue(int(button.pos().x()))
        self.y_spin.setValue(int(button.pos().y()))
        self.width_spin.setValue(int(button.button_w))
        self.height_spin.setValue(int(button.button_h))
        self.shape_combo.setCurrentText(
            {
                CustomButton.RECT: "Rectangle",
                CustomButton.ROUNDED_RECT: "Rounded Rectangle",
                CustomButton.CIRCLE: "Circle"
            }[button.button_shape]
        )
        self.radius_spin.setValue(button.rounding)
        self.color_input.setText(QColor(button.color).name())

        self.text_input.setText(button.text)
        is_special = button.button_type != "regular"
        self.text_input.setReadOnly(is_special)
        self.text_input.setEnabled(not is_special)

        self.font_color_input.setText(QColor(button.font_color).name())
        self.font_size_spin.setValue(button.font_size)
        self.image_url_input.setText(getattr(button, 'image_url', '') or '')

        self._updating = False

    def open_color_picker(self, target_input):
        current = QColor(target_input.text())
        color = QColorDialog.getColor(current, self, "Pick a Color")
        if color.isValid():
            target_input.setText(color.name())

    def on_color_changed(self, text, target_preview):
        if QColor(text).isValid():
            target_preview.setStyleSheet(f"background-color: {text};")
            self.on_property_changed()

    def on_property_changed(self):
        if self._updating:
            return
        self.apply_to_selected()

    def apply_to_selected(self):
        pass