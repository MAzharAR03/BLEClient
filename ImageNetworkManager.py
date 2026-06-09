from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtCore import QUrl, QObject
from PySide6.QtGui import QPixmap

class ImageNetworkManager(QObject):
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        self._network_access_manager = QNetworkAccessManager(self)
        self._pending = []

    def fetch(self, url, callback):
        if not url:
            callback(QPixmap())
            return
        reply = self._network_access_manager.get(QNetworkRequest(QUrl(url)))
        self._pending.append(reply)
        reply.finished.connect(lambda: self._on_reply(reply, callback))

    def _on_reply(self, reply, callback):
        try:
            self._pending.remove(reply)
        except ValueError:
            pass
        data = reply.readAll()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        reply.deleteLater()
        callback(pixmap)

