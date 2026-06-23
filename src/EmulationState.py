from PySide6.QtCore import QObject, Signal


class EmulationState(QObject):
    changed = Signal(bool)

    def __init__(self):
        super().__init__()
        self._enabled = True

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        if self._enabled != value:
            self._enabled = value
            self.changed.emit(value)


