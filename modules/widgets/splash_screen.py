import time

from PySide2.QtGui import QMovie, QPixmap, QPainter
from PySide2.QtWidgets import QSplashScreen
from PySide2.QtCore import Qt

from modules.app_globals import Resource


class MovieSplashScreen(QSplashScreen):

    def __init__(self, movie, parent=None):
        movie.jumpToFrame(0)
        pixmap = QPixmap(movie.frameRect().size())

        QSplashScreen.__init__(self or parent, pixmap, Qt.WindowStaysOnTopHint)
        self.movie = movie
        self.movie.setSpeed(200)
        self.movie.frameChanged.connect(self.repaint)

    def showEvent(self, event):
        self.movie.start()

    def hideEvent(self, event):
        self.movie.stop()

    def paintEvent(self, event):

        painter = QPainter(self)
        pixmap = self.movie.currentPixmap()
        self.setMask(pixmap.mask())
        painter.drawPixmap(0, 0, pixmap)

    def sizeHint(self):

        return self.movie.scaledSize()


def show_splash_screen_movie(app):
    movie = QMovie(Resource.icon_paths['splash_screen'])
    splash = MovieSplashScreen(movie, app)
    splash.show()

    start = time.time()

    while movie.state() == QMovie.Running and time.time() < start + 1.2:
        app.processEvents()

    return splash
