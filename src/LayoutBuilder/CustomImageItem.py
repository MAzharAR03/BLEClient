from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, Qt, QPen
from ResizableGraphicsItem import ResizableGraphicsItem

class CustomImageItem(ResizableGraphicsItem):
    def __init__(self, x, y, width, height, parent=None):
        super().__init__(x, y, width, height, parent)
        self.image_url = ""
        self.pixmap = None

    def set_pixmap(self, pixmap):
        self.pixmap = pixmap
        self.update()

    def paint(self,painter,option, widget = None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.pixmap and not self.pixmap.isNull():
            scaled_pix = self.pixmap.scaled(
                self.item_w, self.item_h,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled_pix)
        else:
            painter.fillRect(0, 0, self.item_w, self.item_h, Qt.GlobalColor.gray)
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(QRectF(0, 0, self.item_w, self.item_h), Qt.AlignmentFlag.AlignCenter, "Image")

        if self.isSelected():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(Qt.GlobalColor.blue, 1, Qt.PenStyle.DashLine))
            painter.drawRect(0, 0, self.item_w, self.item_h)