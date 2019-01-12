from PySide2.QtCore import Qt, QEvent, QTimer, QSize
from PySide2.QtWidgets import QWidget, QHBoxLayout, QProgressBar, QSizePolicy

from modules.log import init_logging

LOGGER = init_logging(__name__)


class ProgressOverlay(QWidget):
    """ Displays a progress bar on top of the provided parent QWidget """
    progress_bar_width_factor = 0.75

    def __init__(self, parent):
        super(ProgressOverlay, self).__init__(parent=parent)

        self.parent = parent
        self.setStyleSheet('background: rgba(255, 0, 0, 100);')

        # Make widget transparent
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Setup widget Layout
        self.box_layout = QHBoxLayout(self)
        self.box_layout.setContentsMargins(0, 0, 0, 0)
        self.box_layout.setSpacing(0)
        self.box_layout.setAlignment(Qt.AlignHCenter)

        self.progress = QProgressBar(self)
        self.progress.setFormat('%v/%m')
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.box_layout.addWidget(self.progress, 0, Qt.AlignCenter)

        self.parent.installEventFilter(self)
        self.progress.hide()

    def eventFilter(self, obj, event):
        if obj == self.progress:
            """ Hide or Show ProgressOverlay if progress bar is hidden or shown """
            if event.type() == QEvent.Hide:
                self.hide()
                return True
            elif event.type() == QEvent.Show:
                self.show()
                return True

        if obj == self.parent:
            """ Resize ProgressOverlay on parent widget resize event """
            if event.type() == QEvent.Resize:

                self.resize(self.parent.size())
                width = self.parent.size().width() * self.progress_bar_width_factor
                self.progress.setMinimumSize(QSize(width, 20))

                return True

        return False
