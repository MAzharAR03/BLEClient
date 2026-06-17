from PySide6.QtCore import QObject, Slot


class MapBridge(QObject):
    def __init__(self):
        super().__init__()
        self._lat = None
        self._lon = None

    @Slot(float, float)
    def pin_placed(self, lat, lon):
        self._lat = lat
        self._lon = lon
        if self._on_pin:
            self._on_pin(lat, lon)

    def set_callback(self,cb):
        self._on_pin = cb

    def position(self):
        return self._lat, self._lon