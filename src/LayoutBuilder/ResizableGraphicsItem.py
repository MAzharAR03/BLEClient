from PySide6.QtCore import QRectF
from PySide6.QtWidgets import QGraphicsItem
from src.LayoutBuilder.ResizeHandle import ResizeHandle

class ResizableGraphicsItem(QGraphicsItem):
    def __init__(self, x, y, width, height, parent = None):
        super().__init__(parent)
        self.setPos(x,y)
        self.item_w = width
        self.item_h = height

        self.on_moved = None
        self.handles = []
        for corner in ("tl", "tr", "bl", "br"):
            h = ResizeHandle(corner, self)
            h.setVisible(False)
            self.handles.append(h)

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

    def boundingRect(self):
        return QRectF(0,0,self.item_w, self.item_h)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            for handle in self.handles:
                handle.setVisible(bool(value))
        if bool(value) and self.on_moved:
            self.on_moved()

        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            if self.scene:
                scene_rect = self.scene().sceneRect()
                clamped_x = max(scene_rect.left(), min(value.x(), scene_rect.right() - self.item_w))
                clamped_y = max(scene_rect.top(), min(value.y(), scene_rect.bottom() - self.item_h))

                if self.on_moved:
                    self.on_moved()

                value.setX(clamped_x)
                value.setY(clamped_y)

        return super().itemChange(change, value)
