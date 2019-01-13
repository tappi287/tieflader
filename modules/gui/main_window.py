from pathlib import Path

from PySide2.QtWidgets import QApplication, QMainWindow

from modules import AppSettings
from modules.app_globals import Resource
from modules.detect_language import get_translation
from modules.gui.drop_action import FileDrop
from modules.gui.gui_utils import SetupWidget
from modules.gui.icon_resource import IconRsc
from modules.gui.main_menu import MainWindowMenu
from modules.log import init_logging
from modules.widgets.progress_overlay import ProgressOverlay

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication):
        super(MainWindow, self).__init__()
        self.app = app
        SetupWidget.from_ui_file(self, Resource.ui_paths['tieflader'])

        self.app_icon = IconRsc.get_icon('tieflader_icon')
        self.setWindowIcon(self.app_icon)

        # Set version window title
        self.setWindowTitle(
            f'{_("Tieflader")} - v{self.app.version}'
            )

        # ---- Setup overlay progress widget ----
        self.progress_widget = ProgressOverlay(self.topWidget)

        # Prepare translations
        self.translations()

        # ---- Setup Main Menu ----
        self.main_menu = MainWindowMenu(self)

        # ---- Setup File Drop ----
        self.drop = FileDrop(self)

    def closeEvent(self, close_event):
        close_event.ignore()
        self.app.quit()

    def translations(self):
        self.appLabel.setText(_('Bilddateien in dieses Fenster ziehen um PSD zu erstellen'))

        self.cancelBtn.setText(_('Vorgang abbrechen'))
        self.lastFileBtn.setText(_('< Keine zuletzt verwendete Datei >'))

        editor = Path(AppSettings.app['editor_path'])
        if editor.exists() and editor.is_file():
            self.lastFileBtn.setDescription(_('Mit benutzerdefiniertem Editor öffnen'))
        else:
            self.lastFileBtn.setDescription(_('Mit Standardanwendung öffnen'))
