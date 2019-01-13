from pathlib import Path

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction, QDialog, QMenu

from modules import AppSettings
from modules.detect_language import get_translation
from modules.gui.icon_resource import IconRsc
from modules.log import init_logging
from modules.widgets.settings_dialog import PhotoshopSettings

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class SettingsMenu(QMenu):
    def __init__(self, ui):
        super(SettingsMenu, self).__init__(_('Einstellungen'), ui)
        self.ui = ui

        check_icon = IconRsc.get_icon('check_box_empty')
        check_icon.addPixmap(IconRsc.get_pixmap('check_box'), QIcon.Normal, QIcon.On)

        self.open_action = QAction(check_icon, _('PSD Datei nach dem Erstellen öffnen'), self)
        self.open_action.setCheckable(True)
        self.open_action.setChecked(AppSettings.app['open_editor'])
        self.open_action.toggled.connect(self.toggle_psd_open_action)
        self.addAction(self.open_action)

        self.addSeparator()

        img_icon = IconRsc.get_icon('setting')
        set_ps_path = QAction(img_icon, _('Erweiterte Einstellungen'), self)
        set_ps_path.triggered.connect(self.open_settings_dialog)
        self.addAction(set_ps_path)

    def toggle_psd_open_action(self):
        AppSettings.app['open_editor'] = self.open_action.isChecked()

    def update_btn_desc(self):
        editor = Path(AppSettings.app['editor_path'])

        if editor.exists() and editor.is_file():
            self.ui.lastFileBtn.setDescription(_('Mit benutzerdefiniertem Editor öffnen'))
        else:
            self.ui.lastFileBtn.setDescription(_('Mit Standardanwendung öffnen'))

    def open_settings_dialog(self):
        psd_settings_window = PhotoshopSettings(self.ui)
        psd_settings_window.finished.connect(self.update_btn_desc)
        psd_settings_window.open()
