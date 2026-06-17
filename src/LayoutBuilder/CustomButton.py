from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, Qt, QFont, QPainterPath

from src.LayoutBuilder.ResizableGraphicsItem import ResizableGraphicsItem


class CustomButton(ResizableGraphicsItem):
    RECT = "rect"
    ROUNDED_RECT = "rounded_rect"
    CIRCLE = "circle"

    def __init__(self, x, y, width, height,shape = ROUNDED_RECT, parent=None, rounding = 10, color="#000000"):
        super().__init__(x, y, width, height, parent)

        self.button_shape = shape
        self.rounding = rounding
        self.color = QColor(color) if isinstance(color, str) else color
        self.text = "Button"
        self.font_color = QColor("#ffffff")
        self.font_size = 14
        self.button_type = "regular"
        self.pixmap = None
        self.image_url = ""

    def set_pixmap(self, pixmap):
        self.pixmap = pixmap
        self.update()


    def paint(self, painter, option, widget = None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        if self.button_shape == self.RECT:
            path.addRect(0,0, self.item_w, self.item_h)
        elif self.button_shape == self.ROUNDED_RECT:
            path.addRoundedRect(0,0, self.item_w, self.item_h, self.rounding, self.rounding)
        elif self.button_shape == self.CIRCLE:
            path.addEllipse(0,0, self.item_w, self.item_h)

        if self.pixmap and not self.pixmap.isNull():
            painter.save()
            painter.setClipPath(path)
            scaled_pixmap = self.pixmap.scaled(
                self.item_w, self.item_h,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled_pixmap)
            painter.restore()

            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.drawPath(path)
        else:
            painter.setBrush(QBrush(self.color))
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.drawPath(path)

        painter.setPen(QPen(self.font_color))
        painter.setFont(QFont("Arial", self.font_size))
        painter.drawText(QRectF(0,0,self.item_w, self.item_h), Qt.AlignmentFlag.AlignCenter, self.text)

        if self.isSelected():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(Qt.GlobalColor.blue, 1, Qt.PenStyle.DashLine))
            painter.drawRect(0,0, self.item_w, self.item_h)
