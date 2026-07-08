import json
import sys
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, \
    QFileDialog, QMessageBox, QTextEdit, QDialog, QApplication

from src import AppSettings
from src.ReadFile import resource_path
from src.TutorialOverlay import TutorialOverlay
from src.TutorialSteps import get_config_mapper_steps
from src.XboxMapper.MapperHelperFunctions import rows_to_config, config_to_rows, get_android_inputs
from src.XboxMapper.RowWidget import RowWidget
from src.XboxMapper.XboxDictionary import XBOX_CONTROLS, ALWAYS_AVAILABLE, FLOAT_INPUTS


class ConfigMapper(QMainWindow):

    config_saved = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Config Mapper")
        final_width, final_height = self.check_monitor_size(900,700)
        self.resize(900,700)

        self._layout_data = {}
        self._available_inputs = list(ALWAYS_AVAILABLE) + FLOAT_INPUTS
        self._rows = {k: [] for k, *_ in XBOX_CONTROLS}
        self._row_widgets = {}

        self._build_ui()
        self._load_current_config()
        self._maybe_show_tutorial()

    def _load_current_config(self):
        path = resource_path("config.cfg")
        try:
            with open(path, "r") as f:
                config = json.load(f)
            self._rows = config_to_rows(config)
            self._build_rows()
        except (OSError, json.JSONDecodeError):
            pass


    def check_monitor_size(self, target_width, target_height):
        screen = QGuiApplication.primaryScreen()
        available = screen.availableGeometry()

        final_width = min(target_width, available.width())
        final_height = min(target_height, available.height())

        return final_width, final_height

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0,0,0,0)

        toolbar = QWidget()
        toolbar.setStyleSheet("background: #1a1a2e; padding: 8px;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12,6,12,6)

        title = QLabel("Config Mapper")
        title.setStyleSheet("color: white; font-size: 15px; font-weight: bold;")
        toolbar_layout.addWidget(title)
        toolbar_layout.addStretch()

        self._toolbar_buttons = {}
        for text, slot in [
            ("Load Layout", self._load_layout),
            ("Load Config", self._load_config),
            ("Export Config", self._export_config),
        ]:
            button = QPushButton(text)
            button.setStyleSheet(
                "QPushButton { color: white; background: #2d2d54; border: 1px solid #4a4a8a;"
                " border-radius: 4px; padding: 4px 12px; }"
                "QPushButton:hover { background: #3d3d74; }"
            )
            button.clicked.connect(slot)
            toolbar_layout.addWidget(button)
            self._toolbar_buttons[text] = button

        replay_btn = QPushButton("Tutorial")
        replay_btn.setStyleSheet(
            "QPushButton { color: white; background: #2d2d54; border: 1px solid #4a4a8a;"
            " border-radius: 4px; padding: 4px 12px; }"
            "QPushButton:hover { background: #3d3d74; }"
        )
        replay_btn.clicked.connect(self._run_tutorial)
        toolbar_layout.addWidget(replay_btn)
        self._toolbar_buttons["Tutorial"] = replay_btn
        root.addWidget(toolbar)

        self._status_label = QLabel("No layout loaded: showing default inputs")
        self._status_label.setStyleSheet(
            "background: #f0f0f0; padding: 4px 14px; font-size: 11px; color: #555;"
        )
        root.addWidget(self._status_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(16, 12, 16, 12)
        self._content_layout.setSpacing(0)
        scroll.setWidget(self._content)
        root.addWidget(scroll, 1)

        self._build_rows()

    def _build_rows(self):
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._row_widgets.clear()

        current_group = None
        for key, label, slot_type, group in XBOX_CONTROLS:
            if group != current_group:
                current_group = group
                group_label = QLabel(group.upper())
                group_label.setStyleSheet(
                    "font-size: 10px; font-weight: bold; color: #888;"
                    " margin-top: 14px; margin-bottom: 4px; letter-spacing: 1px;"
                )
                self._content_layout.addWidget(group_label)

                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setStyleSheet("color: #ddd;")
                self._content_layout.addWidget(separator)

            row_widget = RowWidget(
                key, label, slot_type,
                self._rows[key],
                self._available_inputs,
            )
            row_widget.changed.connect(self._on_changed)
            self._row_widgets[key] = row_widget
            self._content_layout.addWidget(row_widget)

        self._content_layout.addStretch()

    def _load_layout(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Layout File", "", "Layout Files (*.layout)"
        )
        if not path:
            return
        try:
            with open(path, "r") as f:
                self._layout_data = json.load(f)
            self._available_inputs = get_android_inputs(self._layout_data)
            for rw in self._row_widgets.values():
                rw.update_inputs(self._available_inputs)
            self._status_label.setText(
                f"Layout: {Path(path).name}  —  "
                f"{len(self._available_inputs)} inputs available"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load layout:\n{e}")

    def _load_config(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Config File", "", "Config Files (*.cfg)"
        )
        if not path:
            return
        try:
            with open(path, "r") as f:
                config = json.load(f)
            self._rows = config_to_rows(config)
            self._build_rows()
            self._status_label.setText(
                self._status_label.text().split(" | Config:")[0]
                + f" | Config: {Path(path).name}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load config:\n{e}")

    def _on_changed(self):
        pass

    def _export_config(self):
        for key, rw in self._row_widgets.items():
            self._rows[key] = rw.get_chips()

        config = rows_to_config(self._rows)
        output = json.dumps(config, indent = 4)

        dialog = QDialog(self)
        dialog.setWindowTitle("Export Config")
        dialog.resize(520, 400)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Save to File:"))
        te = QTextEdit()
        te.setPlainText(output)
        te.setReadOnly(True)
        layout.addWidget(te)

        button_row = QHBoxLayout()
        save_button = QPushButton("Save")
        close_button = QPushButton("Close")
        button_row.addWidget(save_button)
        button_row.addWidget(close_button)
        button_row.addStretch()
        layout.addLayout(button_row)

        def save():
            path = resource_path("config.cfg")
            with open(path, "w") as f:
                f.write(output)
            self.config_saved.emit(path)
            QMessageBox.information(dialog, "Saved", f"Config saved to:\n{path}")


        save_button.clicked.connect(save)
        close_button.clicked.connect(dialog.accept)
        dialog.exec()

    def _maybe_show_tutorial(self):
        if AppSettings.get("config_tutorial_done"):
            return
        AppSettings.set("config_tutorial_done", True)
        self._run_tutorial()

    def _run_tutorial(self):
        self._overlay = TutorialOverlay(self)
        self._overlay.setGeometry(self.rect())
        self._overlay.set_steps(get_config_mapper_steps(self))


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = ConfigMapper()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()