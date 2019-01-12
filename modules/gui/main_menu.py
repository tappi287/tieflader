from PySide2 import QtCore, QtWidgets

from modules.widgets.menu_file import FileMenu
from modules.widgets.menu_info import InfoMenu
from modules.widgets.menu_language import LanguageMenu
from modules.detect_language import get_translation
from modules.log import init_logging
from modules.widgets.menu_settings import SettingsMenu

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class MainWindowMenu(QtCore.QObject):
    def __init__(self, ui: QtWidgets.QMainWindow):
        super(MainWindowMenu, self).__init__(parent=ui)
        self.ui = ui

        # File menu
        self.file_menu = FileMenu(ui)
        self.ui.menuBar().addMenu(self.file_menu)

        # Settings menu
        self.settings_menu = SettingsMenu(ui)
        self.ui.menuBar().addMenu(self.settings_menu)

        # Language menu
        self.lang_menu = LanguageMenu(ui)
        self.ui.menuBar().addMenu(self.lang_menu)

        # Info Menu
        self.info_menu = InfoMenu(ui)
        self.ui.menuBar().addMenu(self.info_menu)
