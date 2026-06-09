from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPixmap, QPainter, QBrush, QColor
from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QApplication

from ImageNetworkManager import ImageNetworkManager


class SceneImage(QGraphicsItem):

    def __init__(self, x, y, w, h, url=""):
        super().__init__()
        self.img_w = w
        self.img_h = h
        self.url = url
        self._pixmap = None
        self.on_moved = None

        self.setPos(x, y)
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )

        if url:
            self._fetch_image(url)

    def boundingRect(self):
        return QRectF(0, 0, self.img_w, self.img_h)

    def paint(self, painter, option, widget = None):
        if self._pixmap:
            painter.drawPixmap(0, 0, int(self.img_w), int(self.img_h), self._pixmap)
        else:
            painter.setBrush(QBrush(QColor("#3a3a5c")))
            painter.setPen(Qt.NoPen)
            painter.drawRect(0, 0, int(self.img_w), int(self.img_h))
            painter.setPen(QColor("#aaaacc"))
            painter.drawRect(0,0, int(self.img_w), int(self.img_h))
            painter.setPen(QColor("#aaaacc"))
            painter.drawText(
                QRectF(0, 0, int(self.img_w), int(self.img_h)),
                Qt.AlignCenter,
                "Image\n(loading...)" if self.url else "Image\n(no URL)"
            )

        if self.isSelected():
            painter.setPen(QColor("#5588ff"))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(0, 0, int(self.img_w) - 1, int(self.img_h) - 1)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.on_moved:
            self.on_moved()
        return super().itemChange(change, value)


    def _fetch_image(self, url):
        ImageNetworkManager.instance().fetch(url, self._on_pixmap)

    def _on_pixmap(self, pixmap):
        if not pixmap.isNull():
            self._pixmap = pixmap
            self.update()

    def set_url(self, url):
        self.url = url
        self._pixmap = None
        self.update()
        if url:
            self._fetch_image(url)
