from PySide6.QtCore import QRectF, QPointF
from PySide6.QtGui import QBrush, Qt, QPen
from PySide6.QtWidgets import QGraphicsItem


class ResizeHandle(QGraphicsItem):
    SIZE = 8

    def __init__(self, corner, parent_button):
        super().__init__(parent_button)
        self.corner = corner
        self.parent_button = parent_button
        self.setAcceptHoverEvents(True)
        self.setZValue(10)
        self._dragging = False
        self.update_position()

    def boundingRect(self):
        s = self.SIZE
        return QRectF(-s /2, -s /2, s, s)

    def paint(self, painter, option, widget = None):
        s = self.SIZE
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.setPen(QPen(Qt.GlobalColor.blue,1))
        painter.drawRect(QRectF(-s /2, -s /2, s, s))

    def update_position(self):
        button = self.parent_button
        w, h = button.button_w, button.button_h
        corners = {
            "tl":QPointF(0,0),
            "tr":QPointF(w,0),
            "bl":QPointF(0,h),
            "br":QPointF(w,h),
        }
        self.setPos(corners[self.corner])

    def hoverEnterEvent(self, event):
        cursors = {
            "tl": Qt.CursorShape.SizeFDiagCursor,
            "br": Qt.CursorShape.SizeFDiagCursor,
            "tr": Qt.CursorShape.SizeBDiagCursor,
            "bl": Qt.CursorShape.SizeBDiagCursor,
        }
        self.setCursor(cursors[self.corner])
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.unsetCursor()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._start_scene_pos = event.scenePos()
            btn = self.parent_button
            self._start_w = btn.button_w
            self._start_h = btn.button_h
            self._start_btn_pos = btn.pos()
            event.accept()
        else:
            super().mousePressEvent()


    def mouseMoveEvent(self, event):
        if not self._dragging:
            return

        delta = event.scenePos() - self._start_scene_pos
        btn = self.parent_button
        btn.prepareGeometryChange()

        min_size = 20
        sw, sh = self._start_w, self._start_h
        bx, by = self._start_btn_pos.x(), self._start_btn_pos.y()

        if self.corner == "br":
            btn.button_w = max(min_size, sw + delta.x())
            btn.button_h = max(min_size, sh + delta.y())
        elif self.corner == "bl":
            new_w = max(min_size, sw - delta.x())
            btn.setPos(bx + (sw - new_w),by)
            btn.button_w = new_w
            btn.button_h = max(min_size, sh + delta.y())
        elif self.corner == "tr":
            new_h = max(min_size, sh - delta.y())
            btn.setPos(bx, by + (sh - new_h))
            btn.button_w = max(min_size, sw + delta.x())
            btn.button_h = new_h
        elif self.corner == "tl":
            new_w = max(min_size, sw - delta.x())
            new_h = max(min_size, sh - delta.y())
            btn.setPos(bx + (sw - new_w), by + (sh - new_h))
            btn.button_w = new_w
            btn.button_h = new_h

        for handle in btn.handles:
            handle.update_position()
        btn.update()
        if btn.on_moved:
            btn.on_moved()
        event.accept()

    def mouseReleaseEvent(self, event):
        self._dragging = False
        event.accept()
