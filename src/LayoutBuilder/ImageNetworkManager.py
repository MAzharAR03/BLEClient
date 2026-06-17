from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtGui import QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


class ImageNetworkManager(QObject):
    image_ready = Signal(str, QPixmap)
    error_occurred = Signal(str, str)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self.handle_finished)

    def fetch(self, url_string):
        request = QNetworkRequest(QUrl(url_string))
        reply = self.manager.get(request)
        reply.setProperty("original_url",url_string)

    def handle_finished(self, reply):
        url_string = reply.property("original_url")

        if reply.error() == QNetworkReply.NetworkError.NoError:
            image_data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)

            if not pixmap.isNull():
                self.image_ready.emit(url_string, pixmap)
            else:
                self.error_occurred.emit(url_string, "Invalid Data")

        else:
            self.error_occurred.emit(url_string, reply.errorString())

        reply.deleteLater()