import json
import sys

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QBrush, QPen, QPolygonF, QPixmap, QPainter, QFont, QColor
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QApplication, QGraphicsRectItem, QGraphicsItem, \
    QMainWindow, QToolBar, QDockWidget, QWidget, QVBoxLayout, QLabel, QGroupBox, QSpinBox, QFormLayout, QComboBox, \
    QLineEdit, QFileDialog, QPushButton, QColorDialog
from CustomButton import CustomButton
from PropertiesSidebar import PropertiesSidebar

from config import SCENE_WIDTH, SCENE_HEIGHT, ASPECT_RATIO, TOOLBAR_HEIGHT, DOCK_WIDTH

class ViewContainer(QWidget):
    def __init__(self, view, parent = None):
        super().__init__(parent)
        self.view = view
        self.view.setParent(self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("background: white;")


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

        load_action = self.toolbar.addAction("Load Layout")
        load_action.triggered.connect(self.load_layout)
        self.toolbar.addSeparator()
        self.toolbar.setFixedHeight(TOOLBAR_HEIGHT)

        add_button_action = self.toolbar.addAction("Add Button")
        add_button_action.triggered.connect(self.create_new_button)
        delete_action = self.toolbar.addAction("Delete Button")
        delete_action.triggered.connect(self.delete_selected)

        add_screenshot_action = self.toolbar.addAction("Add Screenshot Button")
        add_screenshot_action.triggered.connect(lambda: self.create_special_button("screenshot", "Screenshot"))

        add_pause_action = self.toolbar.addAction("Add Pause Action")
        add_pause_action.triggered.connect(lambda: self.create_special_button("pause", "Pause"))

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

    def create_special_button(self, button_type, label):
        width, height = 100, 100
        x = (SCENE_WIDTH / 2) - (width / 2)
        y = (SCENE_HEIGHT / 2) - (height / 2)

        btn = CustomButton(x, y, width, height, shape = CustomButton.CIRCLE)
        btn.on_moved = lambda: self.sidebar.populate(btn)
        self.scene.addItem(btn)

        btn.text = label
        btn.button_type = button_type


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
        color = QColor(self.sidebar.color_input.text())
        if color.isValid():
            btn.color = color
            btn.update()
        btn.text = self.sidebar.text_input.text()
        font_color = QColor(self.sidebar.font_color_input.text())
        if font_color.isValid():
            btn.font_color = font_color
        btn.font_size = self.sidebar.font_size_spin.value()
        btn.xbox_button = self.sidebar.xbox_combo.currentText()

        for handle in btn.handles:
            handle.update_position()
        btn.update()

    def save_layout(self):
        buttons = []
        for item in self.scene.items():
            if isinstance(item, CustomButton):
                buttons.append(
                    {
                        "type": item.button_type,
                        "text": item.text,
                        "textColor": item.font_color.name(),
                        "textFontSize": item.font_size,
                        "width": item.button_w / SCENE_WIDTH,
                        "height": item.button_h / SCENE_HEIGHT,
                        "xOffset": item.pos().x() / SCENE_WIDTH,
                        "yOffset": item.pos().y() / SCENE_HEIGHT,
                        "shape": item.button_shape,
                        "color": item.color.name(),
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

    def load_layout(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Layout", "", "JSON files (*.json)")
        if not path:
            return

        with open(path, "r") as file:
            data = json.load(file)

        self.scene.clear()

        shape_map = {
            "rect": CustomButton.RECT,
            "rounded_rect": CustomButton.ROUNDED_RECT,
            "circle": CustomButton.CIRCLE,
        }

        for button in data.get("buttons", []):
            x = button["xOffset"] * SCENE_WIDTH
            y = button["yOffset"] * SCENE_HEIGHT
            w = button["width"] * SCENE_WIDTH
            h = button["height"] * SCENE_HEIGHT
            shape = shape_map.get(button.get("shape","rounded_rect"), CustomButton.ROUNDED_RECT)

            btn = CustomButton(x, y, w, h, shape = shape, rounding = button.get("rounding", 10), color = button.get("color", "#000000"))
            btn.text = button.get("text", "")
            btn.button_type = button.get("type","regular")
            btn.font_color = QColor(button.get("textColor","#ffffff"))
            btn.font_size = int(button.get("textFontSize", 14))
            btn.on_moved = lambda: self.sidebar.populate(btn)
            self.scene.addItem(btn)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LayoutBuilder()
    window.create_new_button()
    window.show()
    app.exec()