from pathlib import Path

from PySide2.QtCore import QEvent, Qt
from PySide2.QtWidgets import QAction, QMainWindow, QMenu

from modules.detect_language import get_translation
from modules.gui.icon_resource import IconRsc
from modules.log import init_logging

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class FileMenu(QMenu):
    def __init__(self, ui: QMainWindow):
        super(FileMenu, self).__init__(_('Datei'), ui)
        self.ui = ui

        self.setup_file_menu()

    def setup_file_menu(self):
        # ---- Open ----

        # ---- Exit ----
        action_exit = QAction(IconRsc.get_icon('close'), _("Beenden"), self)
        action_exit.triggered.connect(self.ui.close)
        self.addAction(action_exit)
