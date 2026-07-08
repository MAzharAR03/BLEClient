import json
import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QGuiApplication
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QApplication, QMainWindow, QToolBar, QDockWidget, QWidget, \
    QFileDialog, QInputDialog

from src import AppSettings
from src.LayoutBuilder.CustomButton import CustomButton
from src.LayoutBuilder.CustomImageItem import CustomImageItem
from src.LayoutBuilder.ImageNetworkManager import ImageNetworkManager
from src.LayoutBuilder.PropertiesSidebar import PropertiesSidebar
from src.TutorialOverlay import TutorialOverlay
from src.TutorialSteps import get_ui_builder_steps
from src.XboxMapper.ConfigMapper import ConfigMapper
from src.config import SCENE_WIDTH, SCENE_HEIGHT, ASPECT_RATIO, TOOLBAR_HEIGHT, DOCK_WIDTH


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
    config_saved = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Android Layout Builder")


        self.scene = QGraphicsScene(0,0,SCENE_WIDTH,SCENE_HEIGHT)
        self.view = QGraphicsView(self.scene)
        self.container = ViewContainer(self.view)
        self.setCentralWidget(self.container)

        self.image_fetcher = ImageNetworkManager(self)
        self.image_fetcher.image_ready.connect(self.handle_image_ready)
        self.image_fetcher.error_occurred.connect(self.on_image_error)

        self.pending_image_requests = {}
        self.bg_image_url = ""
        self.bg_pixmap_item = None

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
        self._add_btn = self.toolbar.widgetForAction(add_button_action)

        delete_action = self.toolbar.addAction("Delete Button")
        delete_action.triggered.connect(self.delete_selected)
        self._delete_btn = self.toolbar.widgetForAction(delete_action)

        add_screenshot_action = self.toolbar.addAction("Add Screenshot Button")
        add_screenshot_action.triggered.connect(lambda: self.create_special_button("screenshot", "Screenshot"))
        self._screenshot_btn = self.toolbar.widgetForAction(add_screenshot_action)

        add_pause_action = self.toolbar.addAction("Add Pause Button")
        add_pause_action.triggered.connect(lambda: self.create_special_button("pause", "Pause"))
        self._pause_btn = self.toolbar.widgetForAction(add_pause_action)

        add_recenter_action = self.toolbar.addAction("Add Recenter Action")
        add_recenter_action.triggered.connect(lambda: self.create_special_button("recenter","Recenter"))
        self._recenter_btn = self.toolbar.widgetForAction(add_recenter_action)

        add_rollHold_action = self.toolbar.addAction("Add Roll Hold Button")
        add_rollHold_action.triggered.connect(lambda: self.create_special_button("rollHold","Hold for Roll"))

        add_image_action = self.toolbar.addAction("Add Image")
        add_image_action.triggered.connect(self.add_image_item)
        self._image_btn = self.toolbar.widgetForAction(add_image_action)

        set_bg_action = self.toolbar.addAction("Add Background Image")
        set_bg_action.triggered.connect(self.prompt_background_image)
        self._bg_btn = self.toolbar.widgetForAction(set_bg_action)

        self.toolbar.addSeparator()
        open_mapper_action = self.toolbar.addAction("Open Xbox Mapper")
        open_mapper_action.triggered.connect(self._open_config_mapper)
        self._mapper_btn = self.toolbar.widgetForAction(open_mapper_action)

        self.toolbar.addSeparator()
        replay_tutorial_action = self.toolbar.addAction("Replay Tutorial")
        replay_tutorial_action.triggered.connect(self._run_tutorial)
        self._replay_btn = self.toolbar.widgetForAction(replay_tutorial_action)


        self.dock = QDockWidget("Properties", self)
        self.dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.dock.setMinimumWidth(DOCK_WIDTH)
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)

        self.sidebar = PropertiesSidebar()
        self.dock.setWidget(self.sidebar)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)

        self.setMinimumSize(400 + DOCK_WIDTH, 300 + TOOLBAR_HEIGHT)
        screen_width, screen_height = self.check_monitor_size()
        self.resize(screen_width, screen_height)

        self.scene.selectionChanged.connect(self.on_selection_changed)
        self.sidebar.apply_to_selected = self.apply_sidebar_to_selected

        self.sidebar.image_url_input.editingFinished.connect(self.on_url_entered)

        self._maybe_show_tutorial()

    def _open_config_mapper(self):

        self._config_mapper = ConfigMapper()
        self._config_mapper.config_saved.connect(self.config_saved)
        self._config_mapper.show()

    def add_image_item(self):
        img_item = CustomImageItem(100, 100, 150, 150)
        img_item.on_moved = lambda b=img_item: self.sidebar.populate(b)

        self.scene.addItem(img_item)

    def on_url_entered(self):
        if self.sidebar._updating:
            return

        item = self.sidebar.current_item
        if not item or not hasattr(item, "image_url"):
            return

        url = self.sidebar.image_url_input.text().strip()
        item.image_url = url

        if url:
            self.request_image_for_item(item, url)
        else:
            item.set_pixmap(None)

    def request_image_for_item(self, item, url_string):
        if not url_string:
            return

        if url_string in self.pending_image_requests:
            self.pending_image_requests[url_string].append(item)
        else:
            self.pending_image_requests[url_string] = [item]
            self.image_fetcher.fetch(url_string)

    def handle_image_ready(self, url, pixmap):
        if url == self.bg_image_url:
            scaled_bg = pixmap.scaled(
                SCENE_WIDTH, SCENE_HEIGHT,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            if self.bg_pixmap_item is None:
                self.bg_pixmap_item = self.scene.addPixmap(scaled_bg)
                self.bg_pixmap_item.setZValue(-1000)
            else:
                self.bg_pixmap_item.setPixmap(scaled_bg)

        if url in self.pending_image_requests:
            for item in self.pending_image_requests[url]:
                item.set_pixmap(pixmap)

            del self.pending_image_requests[url]


    def on_image_error(self,url, error_msg):
        print(f"Failed to load {url} - Error: {error_msg}")

    def prompt_background_image(self):
        url, ok = QInputDialog.getText(
            self, "Set Background", "Enter Background Image URL:",
            text = self.bg_image_url
        )
        if ok:
            self.bg_image_url = url.strip()
            if self.bg_image_url:
                self.image_fetcher.fetch(self.bg_image_url)
            else:
                if self.bg_pixmap_item:
                    self.scene.removeItem(self.bg_pixmap_item)
                    self.bg_pixmap_item = None

    def check_monitor_size(self):
        screen = QGuiApplication.primaryScreen()
        available = screen.availableGeometry()  # excludes taskbar

        target_width = SCENE_WIDTH + DOCK_WIDTH
        target_height = SCENE_HEIGHT + TOOLBAR_HEIGHT

        final_width = min(target_width, available.width())
        final_height = min(target_height, available.height())

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
        if len(selected) == 1:
            self.sidebar.populate(selected[0])

    def apply_sidebar_to_selected(self):
        selected = self.scene.selectedItems()
        if not selected:
            return

        item = selected[0]

        item.prepareGeometryChange()
        item.setPos(self.sidebar.x_spin.value(), self.sidebar.y_spin.value())
        item.item_w = self.sidebar.width_spin.value()
        item.item_h = self.sidebar.height_spin.value()
        for handle in item.handles:
            handle.update_position()
        item.update()

        if not isinstance(item, CustomButton):
            return
        item.button_shape = {
            "Rectangle": CustomButton.RECT,
            "Rounded Rectangle": CustomButton.ROUNDED_RECT,
            "Circle": CustomButton.CIRCLE
        }[self.sidebar.shape_combo.currentText()]
        item.rounding = self.sidebar.radius_spin.value()
        color = QColor(self.sidebar.color_input.text())
        if color.isValid():
            item.color = color
            item.update()
        item.text = self.sidebar.text_input.text()
        font_color = QColor(self.sidebar.font_color_input.text())
        if font_color.isValid():
            item.font_color = font_color
        item.font_size = self.sidebar.font_size_spin.value()

        for handle in item.handles:
            handle.update_position()
        item.update()

    def save_layout(self):
        layout_data = {
            "background image": self.bg_image_url,
            "buttons": [],
            "images": []
        }
        for item in self.scene.items():
            if isinstance(item, CustomButton):
                btn_data = {
                        "type": item.button_type,
                        "text": item.text,
                        "textColor": item.font_color.name(),
                        "textFontSize": item.font_size,
                        "width": item.item_w / SCENE_WIDTH,
                        "height": item.item_h / SCENE_HEIGHT,
                        "xOffset": item.pos().x() / SCENE_WIDTH,
                        "yOffset": item.pos().y() / SCENE_HEIGHT,
                        "shape": item.button_shape,
                        "color": item.color.name(),
                        "imageURL": item.image_url,
                        "rounding": item.rounding,
                        "padding": 0
                    }
                layout_data["buttons"].append(btn_data)
            elif isinstance(item, CustomImageItem):
                img_data = {
                    "width": item.item_w,
                    "height": item.item_h,
                    "xOffset": round(item.x() / SCENE_WIDTH, 4),
                    "yOffset": round(item.y() / SCENE_HEIGHT, 4),
                    "imageURL": item.image_url
                }
                layout_data["images"].append(img_data)
        path, _ = QFileDialog.getSaveFileName(self, "Save Layout", "", "Layout files (*.layout)")
        if path:
            with open(path, "w") as file:
                json.dump(layout_data, file, indent=2)

    def load_layout(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Layout", "", "Layout files (*.layout)")
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LayoutBuilder()
    window.create_new_button()
    window.show()
    app.exec()