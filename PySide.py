import json
import sys

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QBrush, QPen, QPolygonF, QPixmap, QPainter, QFont
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QApplication, QGraphicsRectItem, QGraphicsItem, \
    QMainWindow, QToolBar, QDockWidget, QWidget, QVBoxLayout, QLabel, QGroupBox, QSpinBox, QFormLayout, QComboBox, \
    QLineEdit, QFileDialog
from shiboken6.Shiboken import delete

SCENE_WIDTH = 1616
SCENE_HEIGHT = 720
DOCK_WIDTH = 200
ASPECT_RATIO = 20/9
TOOLBAR_HEIGHT = 50

class ViewContainer(QWidget):
    def __init__(self, view, parent = None):
        super().__init__(parent)
        self.view = view
        self.view.setParent(self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("background: white;")

    # def resizeEvent(self, event):
    #     super().resizeEvent(event)
    #     container_width, container_height = self.width(), self.height()
    #
    #     if container_width / container_height > ASPECT_RATIO:
    #         view_width = int(container_height * ASPECT_RATIO)
    #         view_height = container_height
    #     else:
    #         view_width = container_width
    #         view_height = int(container_width / ASPECT_RATIO)
    #
    #     x = (container_width - view_width) // 2
    #     y = (container_height - view_height) // 2
    #     self.view.setGeometry(x, y, view_width, view_height)
    #     self.view.fitInView(self.view.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)


class CustomButton(QGraphicsItem):
    RECT = "rect"
    ROUNDED_RECT = "rounded_rect"
    CIRCLE = "circle"

    def __init__(self, x, y, width, height,shape = ROUNDED_RECT, parent=None, rounding = 10, color=Qt.GlobalColor.red):
        super().__init__(parent)
        self.setPos(x, y)
        self.button_w = width
        self.button_h = height
        self.button_shape = shape
        self.rounding = rounding
        self.color = color
        self.text = "Button"
        self.font_size = 14
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.xbox_button = "None"
        self.on_moved = None

    def boundingRect(self):
        return QRectF(0, 0, self.button_w, self.button_h)

    def paint(self, painter, option, widget = None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))

        if self.button_shape == self.RECT:
            painter.drawRect(0,0, self.button_w, self.button_h)
        elif self.button_shape == self.ROUNDED_RECT:
            painter.drawRoundedRect(0,0, self.button_w, self.button_h, self.rounding, self.rounding)
        elif self.button_shape == self.CIRCLE:
            painter.drawEllipse(0,0, self.button_w, self.button_h)

        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.setFont(QFont("Arial", self.font_size))
        painter.drawText(QRectF(0,0,self.button_w, self.button_h), Qt.AlignmentFlag.AlignCenter, self.text)

        if self.isSelected():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(Qt.GlobalColor.blue, 1, Qt.PenStyle.DashLine))
            painter.drawRect(0,0, self.button_w, self.button_h)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            scene_rect = self.scene().sceneRect()
            clamped_x = max(scene_rect.left(), min(value.x(), scene_rect.right() - self.button_w))
            clamped_y = max(scene_rect.top(), min(value.y(), scene_rect.bottom() - self.button_h))
            return QPointF(clamped_x, clamped_y)

        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if self.on_moved:
                self.on_moved()


        return super().itemChange(change, value)



class PropertiesSidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._updating = False
        layout = QVBoxLayout()
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

        label_group = QGroupBox("Label")
        label_form = QFormLayout()
        self.text_input = QLineEdit()
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(7,72)
        self.font_size_spin.setValue(14)
        label_form.addRow("Text",self.text_input)
        label_form.addRow("Font Size", self.font_size_spin)
        label_group.setLayout(label_form)


        #Add triggers and joystick, add joystick button, add direction and value for triggers and joystick
        xbox_group = QGroupBox("Xbox Mapping")
        xbox_form = QFormLayout()
        self.xbox_combo = QComboBox()
        self.xbox_combo.addItems([
            "None",
            "A",
            "B",
            "X",
            "Y",
            "LB",
            "RB",
            "LT",
            "RT",
            "Up",
            "Down",
            "Left",
            "Right",
            "Left Analog",
            "Right Analog"
        ])
        xbox_form.addRow("Xbox Button", self.xbox_combo)
        xbox_group.setLayout(xbox_form)

        layout.addWidget(pos_group)
        layout.addWidget(size_group)
        layout.addWidget(shape_group)
        layout.addWidget(label_group)
        layout.addWidget(xbox_group)
        layout.addStretch()
        self.setLayout(layout)

        self.x_spin.valueChanged.connect(self.on_property_changed)
        self.y_spin.valueChanged.connect(self.on_property_changed)
        self.width_spin.valueChanged.connect(self.on_property_changed)
        self.height_spin.valueChanged.connect(self.on_property_changed)
        self.shape_combo.currentTextChanged.connect(self.on_property_changed)
        self.radius_spin.valueChanged.connect(self.on_property_changed)
        self.text_input.textChanged.connect(self.on_property_changed)
        self.font_size_spin.valueChanged.connect(self.on_property_changed)
        self.xbox_combo.currentTextChanged.connect(self.on_property_changed)

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
        self.text_input.setText(button.text)
        self.font_size_spin.setValue(button.font_size)
        self.xbox_combo.setCurrentText(button.xbox_button)
        self._updating = False


    def on_property_changed(self):
        if self._updating:
            return
        self.apply_to_selected()

    def apply_to_selected(self):
        pass


class LayoutBuilder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Android Layout Builder")


        self.scene = QGraphicsScene(0,0,SCENE_WIDTH,SCENE_HEIGHT)
        self.view = QGraphicsView(self.scene)
        self.container = ViewContainer(self.view)
        self.setCentralWidget(self.container)

        self.toolbar = QToolBar("Toolbar")
        self.addToolBar(self.toolbar)
        save_action = self.toolbar.addAction("Save Layout")
        save_action.triggered.connect(self.save_layout)

        self.toolbar.addAction("Load Layout")
        self.toolbar.addSeparator()
        self.toolbar.setFixedHeight(TOOLBAR_HEIGHT)

        add_button_action = self.toolbar.addAction("Add Button")
        add_button_action.triggered.connect(self.create_new_button)
        delete_action = self.toolbar.addAction("Delete Button")
        delete_action.triggered.connect(self.delete_selected)

        self.dock = QDockWidget("Properties", self)
        self.dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.dock.setFixedWidth(DOCK_WIDTH)
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)

        self.sidebar = PropertiesSidebar()
        self.dock.setWidget(self.sidebar)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        self.setFixedSize(SCENE_WIDTH + DOCK_WIDTH, SCENE_HEIGHT + TOOLBAR_HEIGHT)

        self.scene.selectionChanged.connect(self.on_selection_changed)
        self.sidebar.apply_to_selected = self.apply_sidebar_to_selected

    def create_new_button(self):

        width, height = 100, 100
        x = (SCENE_WIDTH / 2) - (width / 2)
        y = (SCENE_HEIGHT / 2) - (height / 2)

        btn = CustomButton(x, y, width, height, shape = CustomButton.CIRCLE)
        btn.on_moved = lambda: self.sidebar.populate(btn)
        self.scene.addItem(btn)

    def delete_selected(self):
        for item in self.scene.selectedItems():
            self.scene.removeItem(item)

    def on_selection_changed(self):
        selected = self.scene.selectedItems()
        if len(selected) == 1 and isinstance(selected[0], CustomButton):
            self.sidebar.populate(selected[0])

    def apply_sidebar_to_selected(self):
        selected = self.scene.selectedItems()
        if not selected or not isinstance(selected[0], CustomButton):
            return

        btn = selected[0]
        btn.prepareGeometryChange()
        btn.setPos(self.sidebar.x_spin.value(), self.sidebar.y_spin.value())
        btn.button_w = self.sidebar.width_spin.value()
        btn.button_h = self.sidebar.height_spin.value()
        btn.button_shape = {
            "Rectangle": CustomButton.RECT,
            "Rounded Rectangle": CustomButton.ROUNDED_RECT,
            "Circle": CustomButton.CIRCLE
        }[self.sidebar.shape_combo.currentText()]
        btn.rounding = self.sidebar.radius_spin.value()
        btn.text = self.sidebar.text_input.text()
        btn.font_size = self.sidebar.font_size_spin.value()
        btn.xbox_button = self.sidebar.xbox_combo.currentText()

        btn.update()

    def save_layout(self):
        buttons = []
        for item in self.scene.items():
            if isinstance(item, CustomButton):
                buttons.append(
                    {
                        "text": item.text,
                        "textColor": "#ffffff",
                        "textFontSize": item.font_size,
                        "width": item.button_w / SCENE_WIDTH,
                        "height": item.button_h / SCENE_HEIGHT,
                        "xOffset": item.pos().x() / SCENE_WIDTH,
                        "yOffset": item.pos().y() / SCENE_HEIGHT,
                        "shape": item.button_shape,
                        "color": "#000000",
                        "imageURL": "",
                        "rounding": item.rounding,
                        "padding": 0
                    }
                )
        data = {
            "background image": "",
            "buttons": buttons,
            "images": []
        }
        path, _ = QFileDialog.getSaveFileName(self, "Save Layout", "", "JSON files (*.json)")
        if path:
            with open(path, "w") as file:
                json.dump(data, file, indent=2)

app = QApplication(sys.argv)
window = LayoutBuilder()
window.create_new_button()
window.show()
app.exec()