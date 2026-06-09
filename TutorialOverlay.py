from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QRect, QPoint, QRectF
from PySide6.QtGui import QPainter, QColor, QPainterPath, QFont, QPen


class TutorialOverlay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setGeometry(parent.rect())

        self.spotlight_color = QColor(0,0,0,160)

        self._steps = []
        self._current = 0
        self._spotlight_rect = QRect()

        self._bubble = QWidget(self)
        self._bubble.setFixedWidth(260)

        bubble_layout = QVBoxLayout(self._bubble)
        bubble_layout.setContentsMargins(12,10,12,10)
        bubble_layout.setSpacing(6)

        self._title_label = QLabel()
        self._title_label.setWordWrap(True)

        self._desc_label = QLabel()
        self._desc_label.setWordWrap(True)

        button_row = QWidget()
        button_row.setStyleSheet("background: transparent; border: none;")
        button_layout = QVBoxLayout(button_row)
        button_layout.setContentsMargins(0,4,0,0)

        self._next_button = QPushButton("Next")

        self._next_button.clicked.connect(self._advance)
        self._skip_button = QPushButton("Skip Tutorial")

        button_layout.addWidget(self._next_button)
        button_layout.addWidget(self._skip_button)

        self._skip_button.clicked.connect(self.close)

        bubble_layout.addWidget(self._title_label)
        bubble_layout.addWidget(self._desc_label)
        bubble_layout.addWidget(button_row)

        self._bubble.setStyleSheet("""
            background: #1e1e2e;
            border: 1px solid #5a5aaa;
            border-radius: 10px;
        """)
        self._title_label.setStyleSheet(
            "color: #a0a0ff; font-weight: bold; font-size: 13px; background: transparent; border: none;")
        self._desc_label.setStyleSheet("color: #cccccc; font-size: 11px; background: transparent; border: none;")
        self._next_button.setStyleSheet(
            "QPushButton { background: #3a3a7a; color: white; border-radius: 5px; padding: 5px 14px; } QPushButton:hover { background: #5a5aaa; }")
        self._skip_button.setStyleSheet(
            "QPushButton { background: transparent; color: #666688; border: none; font-size: 10px; } QPushButton:hover { color: #aaaacc; }")

        self.raise_()

    def set_steps(self, steps):
        self._steps = steps
        self._current = 0
        self._show_step(0)
        self.show()

    def _show_step(self, index):
        if index >= len(self._steps):
            self.close()
            return

        widget, title, desc = self._steps[index]
        is_last = (index == len(self._steps) - 1)
        self._next_button.setText("Finish" if is_last else "Next")
        self._title_label.setText(f"{index + 1}/{len(self._steps)} {title}")
        self._desc_label.setText(desc)

        if widget:
            global_rect = QRect(widget.mapToGlobal(QPoint(0, 0)), widget.size())
            self._spotlight_rect = QRect(self.mapFromGlobal(global_rect.topLeft()),global_rect.size())
        else:
            self._spotlight_rect = QRect()

        self._position_bubble()
        self.update()

    def _position_bubble(self):
        self._bubble.adjustSize()
        margin = 16
        overlay_rect = self.rect()
        bw, bh = self._bubble.width(), self._bubble.height()

        if self._spotlight_rect.isNull():
            self._bubble.move((overlay_rect.width() - bw) // 2,
                              (overlay_rect.height() - bh) // 2)
            return

        #Try right of spotlight, else left, else below, else above
        candidates = [
            QPoint(self._spotlight_rect.right() + margin, self._spotlight_rect.top()),
            QPoint(self._spotlight_rect.left() - bw - margin, self._spotlight_rect.top()),
            QPoint(self._spotlight_rect.left(), self._spotlight_rect.bottom() + margin),
            QPoint(self._spotlight_rect.left(), self._spotlight_rect.top() - bh - margin),
        ]

        for pos in candidates:
            candidate_rect = QRect(pos, self._bubble.size())
            if overlay_rect.contains(candidate_rect):
                self._bubble.move(pos)
                return

        x = max(0, min(self._spotlight_rect.right() + margin, overlay_rect.width() - bw))
        y = max(0, min(self._spotlight_rect.top(), overlay_rect.height() - bh))
        self._bubble.move(x, y)

    def _advance(self):
        self._current += 1
        self._show_step(self._current)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        full_path = QPainterPath()
        full_path.addRect(QRectF(self.rect()))

        if not self._spotlight_rect.isNull():
            padding = 6
            padded = self._spotlight_rect.adjusted(-padding, -padding, padding, padding)
            hole_path = QPainterPath()
            hole_path.addRoundedRect(QRectF(padded), 8, 8)
            full_path = full_path.subtracted(hole_path)

        painter.fillPath(full_path, self.spotlight_color )

        if not self._spotlight_rect.isNull():
            painter.setPen(QPen(QColor("#6666cc"), 2))
            padding = 6
            padded = self._spotlight_rect.adjusted(-padding, -padding, padding, padding)
            painter.drawRoundedRect(QRectF(padded), 8, 8)

        painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent():
            self.setGeometry(self.parent().rect())
        if self._steps and self._current < len(self._steps):
            widget, _, _ = self._steps[self._current]
            if widget:
                global_rect = QRect(widget.mapToGlobal(QPoint(0, 0)), widget.size())
                self._spotlight_rect = QRect(self.mapFromGlobal(global_rect.topLeft()), global_rect.size())
            else:
                self._spotlight_rect = QRect()
        self._position_bubble()
        self.update()