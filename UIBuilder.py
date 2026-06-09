import json
import sys
from email.mime import image

from PySide6.QtCore import Qt, QPointF, QRectF, QSize
from PySide6.QtGui import QBrush, QPen, QPolygonF, QPixmap, QPainter, QFont, QColor, QGuiApplication
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QApplication, QGraphicsRectItem, QGraphicsItem, \
    QMainWindow, QToolBar, QDockWidget, QWidget, QVBoxLayout, QLabel, QGroupBox, QSpinBox, QFormLayout, QComboBox, \
    QLineEdit, QFileDialog, QPushButton, QColorDialog, QInputDialog

import AppSettings
from CustomButton import CustomButton
from PropertiesSidebar import PropertiesSidebar
from SceneImage import SceneImage
from TutorialOverlay import TutorialOverlay
from TutorialSteps import get_ui_builder_steps
from ImagePropertiesSidebar import ImagePropertiesSidebar
from ImageNetworkManager import ImageNetworkManager

from constants import SCENE_WIDTH, SCENE_HEIGHT, ASPECT_RATIO, TOOLBAR_HEIGHT, DOCK_WIDTH

class ViewContainer(QWidget):
    def __init__(self, view, parent = None):
        super().__init__(parent)
        self.view = view
        self.view.setParent(self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent; border: none;")
        self.setStyleSheet("background: #2b2b2b;")

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self._fit_view()

    def showEvent(self, event):
        super().showEvent(event)
        self._fit_view()

    def _fit_view(self):
        container_w = self.width()
        container_h = self.height()
        target_w = container_w
        target_h = int(target_w / ASPECT_RATIO)
        if target_h > container_h:
            target_h = container_h
            target_w = int(target_h * ASPECT_RATIO)
        x = (container_w - target_w) // 2
        y = (container_h - target_h) //2
        self.view.setGeometry(x,y,target_w, target_h)
        self.view.fitInView(self.view.scene().sceneRect(), Qt.AspectRatioMode.IgnoreAspectRatio)


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
        self._save_btn = self.toolbar.widgetForAction(save_action)

        load_action = self.toolbar.addAction("Load Layout")
        load_action.triggered.connect(self.load_layout)
        self._load_btn = self.toolbar.widgetForAction(load_action)
        self.toolbar.addSeparator()
        self.toolbar.setMinimumHeight(TOOLBAR_HEIGHT)

        add_button_action = self.toolbar.addAction("Add Button")
        add_button_action.triggered.connect(self.create_new_button)

        delete_action = self.toolbar.addAction("Delete Button")
        delete_action.triggered.connect(self.delete_selected)

        add_screenshot_action = self.toolbar.addAction("Add Screenshot Button")
        add_screenshot_action.triggered.connect(lambda: self.create_special_button("screenshot", "Screenshot"))

        add_pause_action = self.toolbar.addAction("Add Pause Action")
        add_pause_action.triggered.connect(lambda: self.create_special_button("pause", "Pause"))

        self.toolbar.addSeparator()

        add_image_action = self.toolbar.addAction("Add Image")
        add_image_action.triggered.connect(self.create_new_image)

        set_bg_action = self.toolbar.addAction("Set Background URL")
        set_bg_action.triggered.connect(self.set_background_url)

        self._add_btn = self.toolbar.widgetForAction(add_button_action)
        self._delete_btn = self.toolbar.widgetForAction(delete_action)
        self._screenshot_btn = self.toolbar.widgetForAction(add_screenshot_action)
        self._pause_btn = self.toolbar.widgetForAction(add_pause_action)
        self._add_image_button = self.toolbar.widgetForAction(add_image_action)
        self._set_bg_btn = self.toolbar.widgetForAction(set_bg_action)

        self.dock = QDockWidget("Properties", self)
        self.dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.dock.setMinimumWidth(DOCK_WIDTH)
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)

        self.sidebar = PropertiesSidebar()
        self.dock.setWidget(self.sidebar)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)

        self._img_dock = QDockWidget("Image Properties", self)
        self._img_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self._img_dock.setMinimumWidth(DOCK_WIDTH)
        self._img_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self._img_dock.setVisible(False)

        self.img_sidebar = ImagePropertiesSidebar()
        self.img_sidebar.apply_to_selected = self._apply_image_properties
        self._img_dock.setWidget(self.img_sidebar)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._img_dock)
        self._current_image = None


        screen_width, screen_height = self.check_monitor_size()
        self.resize(screen_width, screen_height)
        self.setMinimumSize(400 + DOCK_WIDTH, 300 + TOOLBAR_HEIGHT)

        self.scene.selectionChanged.connect(self.on_selection_changed)
        self.sidebar.apply_to_selected = self._apply_button_properties

        self._background_url = ""
        self._maybe_show_tutorial()

    def check_monitor_size(self):
        screens = QGuiApplication.screens()
        max_width = max(screen.geometry().width() for screen in screens)
        max_height = max(screen.geometry().height() for screen in screens)
        target_width = SCENE_WIDTH + DOCK_WIDTH
        target_height = SCENE_HEIGHT + TOOLBAR_HEIGHT

        final_width = min(target_width, max_width)
        final_height = min(target_height, max_height)

        return final_width, final_height

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
        if len(selected) != 1:
            return
        item = selected[0]
        if isinstance(item, CustomButton):
            self._img_dock.setVisible(False)
            self.dock.setVisible(True)
            self.sidebar.populate(item)
        elif isinstance(item, SceneImage):
            self.dock.setVisible(False)
            self._img_dock.setVisible(True)
            self._populate_image_dock(item)

    def _apply_button_properties(self):
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
        btn.text = self.sidebar.text_input.text()
        font_color = QColor(self.sidebar.font_color_input.text())
        if font_color.isValid():
            btn.font_color = font_color
        btn.font_size = self.sidebar.font_size_spin.value()
        btn.image_url = self.sidebar.image_url_input.text().strip()
        for handle in btn.handles:
            handle.update_position()
        btn.update()

    def save_layout(self):
        buttons = []
        images = []
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
                        "imageURL": item.image_url if hasattr(item, 'image_url') else "",
                        "rounding": item.rounding,
                        "padding": 0
                    }
                )
            elif isinstance(item, SceneImage):
                images.append({
                    "imageURL": item.url,
                    "width": item.img_w / SCENE_WIDTH,
                    "height": item.img_h / SCENE_HEIGHT,
                    "xOffset": item.pos().x() / SCENE_WIDTH,
                    "yOffset": item.pos().y() / SCENE_HEIGHT,
                })
        data = {
            "background image": self._background_url,
            "buttons": buttons,
            "images": images
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
            btn.on_moved = lambda b = btn: self.sidebar.populate(b)
            #the default argument b=btn is provided because lambda captures the variable btn - which means all buttons will point to the last loaded button
            #default argument overrides this behaviour as default argument values are evaluated at definition time
            self.scene.addItem(btn)

        self._background_url = data.get("background image")
        self._update_scene_background()

        for img_data in data.get("images", []):
            x = img_data["xOffset"] * SCENE_WIDTH
            y = img_data["yOffset"] * SCENE_HEIGHT
            w = img_data["width"] * SCENE_WIDTH
            h = img_data["height"] * SCENE_HEIGHT
            img = SceneImage(x, y, w, h, url=img_data.get("imageURL", ""))
            img.on_moved = lambda i=img: self._populate_image_dock(i)
            self.scene.addItem(img)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_overlay') and self._overlay.isVisible():
            self._overlay.setGeometry(self.rect())

    def _maybe_show_tutorial(self):
        if AppSettings.get("ui_tutorial_done"):
            return
        AppSettings.set("ui_tutorial_done", True)
        self._run_tutorial()

    def _run_tutorial(self):
        self._overlay = TutorialOverlay(self)
        self._overlay.setGeometry(self.rect())
        self._overlay.set_steps(get_ui_builder_steps(self))

    def create_new_image(self):
        url, ok = QInputDialog.getText(self, "Image URL", "Enter image URL:")
        if not ok:
            return
        img = SceneImage(
            x = SCENE_WIDTH / 2 - 100,
            y = SCENE_HEIGHT / 2 - 100,
            w = 200, h = 200,
            url = url.strip()
        )
        img.on_moved = lambda i=img: self._populate_image_dock(i)
        self.scene.addItem(img)

    def set_background_url(self):
        url, ok = QInputDialog.getText(self, "Background Image URL", "Enter background image URL:", text = self._background_url)
        if ok:
            self._background_url = url.strip()
            self._update_scene_background()

    def _update_scene_background(self):
        if not self._background_url:
            self.scene.setBackgroundBrush(QBrush(QColor("#1e1e1e")))
            return
        ImageNetworkManager.instance().fetch(self._background_url, self._on_bg_pixmap)


    def _on_bg_pixmap(self, pixmap):
        if not pixmap.isNull():
            scaled = pixmap.scaled(SCENE_WIDTH, SCENE_HEIGHT, Qt.KeepAspectRatioByExpanding)
            self.scene.setBackgroundBrush(QBrush(scaled))

    def _populate_image_dock(self, img):
        self._current_image = img
        self.img_sidebar.populate(img)

    def _apply_image_properties(self):
        if not self._current_image:
            return
        img = self._current_image
        img.prepareGeometryChange()
        img.setPos(self.img_sidebar.x_spin.value(), self.img_sidebar.y_spin.value())
        img.img_w = self.img_sidebar.width_spin.value()
        img.img_h = self.img_sidebar.height_spin.value()
        new_url = self.img_sidebar.url_input.text().strip()
        if new_url != img.url:
            img.set_url(new_url)
        img.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LayoutBuilder()
    window.create_new_button()
    window.show()
    app.exec()