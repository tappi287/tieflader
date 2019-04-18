import sys
from pathlib import Path

from PySide2 import QtWidgets
from PySide2.QtCore import QTimer, QEvent
from PySide2.QtGui import QFileOpenEvent

from modules.app_globals import APP_NAME
from modules.detect_language import get_translation
from modules.gui.main_window import MainWindow
from modules.log import init_logging
from modules.pyshop import PyShop
from modules.widgets.message_box import GenericMsgBox
from modules.widgets.splash_screen import show_splash_screen_movie

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class MainApp(QtWidgets.QApplication):
    def __init__(self, version, app_exception_hook=None):
        super(MainApp, self).__init__(sys.argv)
        LOGGER.warning('Sys argv:\n%s', sys.argv)

        self.version = version
        self.argv: list = sys.argv

        self.open_file_queue = list()
        self.open_file_timer = QTimer()
        self.open_file_timer.setSingleShot(True)
        self.open_file_timer.setInterval(100)
        self.open_file_timer.timeout.connect(self.open_file_timeout)

        self.ui = MainWindow(self)

        if app_exception_hook:
            app_exception_hook.app = self
            app_exception_hook.setup_signal_destination(self.app_exception)

        # self.system_tray = QSystemTrayIcon(self.ui.app_icon, self)
        # self.system_tray.hide()

        self.splash = show_splash_screen_movie(self)
        self.splash.movie.finished.connect(self.show_ui)

        self.instance().installEventFilter(self)
        self.instance().event = self.event

        # Make sure we show the ui if there is a problem with the splash screen movie
        QTimer().singleShot(2500, self.show_ui)
        QTimer().singleShot(1000, self.queue_startup_files)

    def event(self, event):
        return self.file_open_event(event)

    def eventFilter(self, obj, event):
        return self.file_open_event(event)

    def file_open_event(self, event):
        if event.type() == QEvent.FileOpen or type(event) is QFileOpenEvent:
            LOGGER.debug('Open file event with url: %s %s', event.url(), event)
            self.ui.res_btn.setText(str(event.url()))

            url = event.url()
            if not url.isLocalFile():
                return False

            # Queue files added via FileOpen Event
            local_file_path = Path(url.toLocalFile())
            self.open_file_queue.append(local_file_path)
            self.open_file_timer.start()
            return True

        return False

    def open_file_timeout(self):
        self.queue_startup_files(self.open_file_queue)
        self.open_file_queue = list()

    def show_ui(self):
        """ Used when splash screen finished """
        if self.ui.isVisible():
            return

        if self.splash is not None:
            self.splash.hide()
            self.splash.deleteLater()

        self.ui.show()

    def show_tray_notification(self,
                               title=_(APP_NAME),
                               message=_('Keine Nachricht angegeben.')):
        self.system_tray.show()
        self.system_tray.showMessage(title, message, self.rk_icon)
        self.system_tray.hide()

    def queue_startup_files(self, files: list=None):
        """ Add the file urls of startup arguments or QOpenFile to pyshop """
        img_files = list()
        files = files or self.argv

        for entry in files:
            if not isinstance(entry, str):
                continue

            file = Path(entry)
            if file.suffix.casefold() not in PyShop.supported_img or not file.is_file():
                continue

            img_files.append(file)

        if img_files:
            LOGGER.info('Add files to queue: %s', img_files)
            self.ui.drop.run_py_shop(img_files)

        self.argv = list()

    def app_exception(self, msg):
        msg = _("Ausnahme aufgetreten: <br><br>") + msg.replace('\n', '<br>')
        GenericMsgBox.warning(self.ui, _("Schwerwiegender Fehler"), msg)

    def about_to_quit(self):
        pass
