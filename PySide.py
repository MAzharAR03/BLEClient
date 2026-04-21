import sys

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QBrush, QPen, QPolygonF, QPixmap, QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QApplication, QGraphicsRectItem, QGraphicsItem, \
    QMainWindow, QToolBar, QDockWidget, QWidget, QVBoxLayout, QLabel

SCENE_WIDTH = 1616
SCENE_HEIGHT = 720
DOCK_WIDTH = 200
ASPECT_RATIO = 20/9
TOOLBAR_HEIGHT = 50

# class AndroidView(QGraphicsView):
#     def __init__(self, scene, parent=None):
#         super().__init__(scene, parent)
#         self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
#         self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
#         self.setRenderHint(self.renderHints().Antialiasing)
#
#     def resizeEvent(self, event):
#         super().resizeEvent(event)
#         self.fitInView(self.scene().sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)

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
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.xbox_button = "None"

    def boundingRect(self):
        return QRectF(0, 0, self.button_w, self.button_h)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))

        if self.button_shape == self.RECT:
            painter.drawRect(0,0, self.button_w, self.button_h)
        elif self.button_shape == self.ROUNDED_RECT:
            painter.drawRoundedRect(0,0, self.button_w, self.button_h, self.rounding, self.rounding)
        elif self.button_shape == self.CIRCLE:
            painter.drawEllipse(0,0, self.button_w, self.button_h)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            scene_rect = self.scene().sceneRect()
            clamped_x = max(scene_rect.left(), min(value.x(), scene_rect.right() - self.button_w))
            clamped_y = max(scene_rect.top(), min(value.y(), scene_rect.bottom() - self.button_h))
            return QPointF(clamped_x, clamped_y)

        return super().itemChange(change, value)

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
         self.toolbar.addAction("Save Layout")
         self.toolbar.addAction("Load Layout")
         self.toolbar.addSeparator()
         self.toolbar.setFixedHeight(TOOLBAR_HEIGHT)
         add_button_action = self.toolbar.addAction("Add Button")
         add_button_action.triggered.connect(self.create_new_button)

         self.dock = QDockWidget("Properties", self)
         self.dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
         self.dock.setFixedWidth(DOCK_WIDTH)

         self.sidebar_container = QWidget()
         self.sidebar_layout = QVBoxLayout()

         self.sidebar_layout.addWidget(QLabel("Selected Element Properties"))
         self.sidebar_layout.addStretch()

         self.sidebar_container.setLayout(self.sidebar_layout)
         self.dock.setWidget(self.sidebar_container)
         self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
         self.setFixedSize(SCENE_WIDTH + DOCK_WIDTH, SCENE_HEIGHT + TOOLBAR_HEIGHT)

    def create_new_button(self):
        # Create a button at the center of the scene
        # Using fixed pixel sizes as you mentioned before (e.g., 100x50)
        w, h = 100, 50
        x = (SCENE_WIDTH / 2) - (w / 2)
        y = (SCENE_HEIGHT / 2) - (h / 2)

        btn = CustomButton(x, y, w, h)
        self.scene.addItem(btn)

app = QApplication(sys.argv)
window = LayoutBuilder()
window.create_new_button()
window.show()
app.exec()