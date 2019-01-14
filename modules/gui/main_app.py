import sys

from PySide2 import QtWidgets
from PySide2.QtCore import QTimer

from modules.app_globals import APP_NAME
from modules.detect_language import get_translation
from modules.gui.main_window import MainWindow
from modules.log import init_logging
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

        self.version = version

        self.ui = MainWindow(self)

        if app_exception_hook:
            app_exception_hook.app = self
            app_exception_hook.setup_signal_destination(self.app_exception)

        # self.system_tray = QSystemTrayIcon(self.ui.app_icon, self)
        # self.system_tray.hide()

        self.splash = show_splash_screen_movie(self)
        self.splash.movie.finished.connect(self.show_ui)

        # Make sure we show the ui if there is a problem with the splash screen movie
        QTimer().singleShot(2500, self.show_ui)

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

    def app_exception(self, msg):
        msg = _("Ausnahme aufgetreten: <br><br>") + msg.replace('\n', '<br>')
        GenericMsgBox.warning(self.ui, _("Schwerwiegender Fehler"), msg)

    def about_to_quit(self):
        pass
