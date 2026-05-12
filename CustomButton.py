from PySide6.QtCore import QRectF, QPointF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, Qt, QFont
from PySide6.QtWidgets import QGraphicsItem

from ResizeHandle import ResizeHandle


class CustomButton(QGraphicsItem):
    RECT = "rect"
    ROUNDED_RECT = "rounded_rect"
    CIRCLE = "circle"

    def __init__(self, x, y, width, height,shape = ROUNDED_RECT, parent=None, rounding = 10, color="#000000"):
        super().__init__(parent)
        self.setPos(x, y)
        self.button_w = width
        self.button_h = height
        self.button_shape = shape
        self.rounding = rounding
        self.color = QColor(color) if isinstance(color, str) else color
        self.text = "Button"
        self.font_color = QColor("#ffffff")
        self.font_size = 14
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.xbox_button = "None"
        self.on_moved = None
        self.handles = []
        for corner in ("tl","tr","bl","br"):
            h = ResizeHandle(corner,self)
            h.setVisible(False)
            self.handles.append(h)
        self.button_type = "regular"

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

        painter.setPen(QPen(self.font_color))
        painter.setFont(QFont("Arial", self.font_size))
        painter.drawText(QRectF(0,0,self.button_w, self.button_h), Qt.AlignmentFlag.AlignCenter, self.text)

        if self.isSelected():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(Qt.GlobalColor.blue, 1, Qt.PenStyle.DashLine))
            painter.drawRect(0,0, self.button_w, self.button_h)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            for handle in self.handles:
                handle.setVisible(bool(value))
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            scene_rect = self.scene().sceneRect()
            clamped_x = max(scene_rect.left(), min(value.x(), scene_rect.right() - self.button_w))
            clamped_y = max(scene_rect.top(), min(value.y(), scene_rect.bottom() - self.button_h))
            return QPointF(clamped_x, clamped_y)

        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if self.on_moved:
                self.on_moved()


        return super().itemChange(change, value)