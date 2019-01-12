from pathlib import Path

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction, QDialog, QHBoxLayout, QLabel, QLineEdit, QMenu, QPushButton, QToolButton, \
    QVBoxLayout

from modules import AppSettings
from modules.app_globals import APP_NAME
from modules.detect_language import get_translation
from modules.gui.icon_resource import IconRsc
from modules.gui.path_util import SetDirectoryPath
from modules.log import init_logging

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

        self.open_action = QAction(check_icon, _('Photoshop Datei nach dem Erstellen öffnen?'), self)
        self.open_action.setCheckable(True)
        self.open_action.setChecked(AppSettings.app['open_editor'])
        self.open_action.toggled.connect(self.toggle_psd_open_action)
        self.addAction(self.open_action)

        self.addSeparator()

        img_icon = IconRsc.get_icon('img')
        set_ps_path = QAction(img_icon, _('Manuellen Pfad zur ausführbaren Photoshop Programmdatei angeben.'), self)
        set_ps_path.triggered.connect(self.open_path_window)
        self.addAction(set_ps_path)

    def toggle_psd_open_action(self):
        AppSettings.app['open_editor'] = self.open_action.isChecked()

    def open_path_window(self):
        psd_path_window = PhotoshopPathWin(self.ui)
        psd_path_window.finished.connect(self.open_path_dialog_finished)
        psd_path_window.open()

    def open_path_dialog_finished(self, result):
        if result == QDialog.Accepted:
            psd_editor_path = Path(AppSettings.app['editor_path'])

            if psd_editor_path.exists() and psd_editor_path.is_file():
                AppSettings.app['open_editor'] = True
                self.open_action.setChecked(True)
            else:
                AppSettings.app['editor_path'] = ''


class PhotoshopPathWin(QDialog):
    psd_path = Path('.')

    def __init__(self, ui):
        super(PhotoshopPathWin, self).__init__(parent=ui)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(_('{} - Pfad zu Photoshop angeben').format(APP_NAME.capitalize()))
        self.resize(512, 150)

        vbox = QVBoxLayout(self)
        box = QHBoxLayout()
        lower_box = QHBoxLayout()

        self.desc = QLabel(self)
        self.desc.setWordWrap(True)
        self.desc.setText(_('<h3>Photoshop Pfad</h3>'
                            'Pfad zur ausführbaren Anwendung angeben.<br>'))
        vbox.addWidget(self.desc)
        vbox.addLayout(box)

        self.line = QLineEdit(self)
        self.line.setText(AppSettings.app['editor_path'])
        box.addWidget(self.line)

        self.btn = QToolButton(self)
        self.btn.setIcon(IconRsc.get_icon('folder'))
        box.addWidget(self.btn)

        self.path_util = SetDirectoryPath(
            ui.app, ui, line_edit=self.line, tool_button=self.btn, mode='file', reject_invalid_path_edits=True,
            )
        self.path_util.path_changed.connect(self.update_path)

        vbox.addLayout(lower_box)
        ok_btn = QPushButton(_('OK'), self)
        ok_btn.setDefault(False)
        ok_btn.pressed.connect(self.accept)
        cancel_btn = QPushButton(_('Abbrechen'), self)
        cancel_btn.setDefault(True)
        cancel_btn.pressed.connect(self.reject)

        lower_box.addWidget(ok_btn)
        lower_box.addWidget(cancel_btn)
        lower_box.setAlignment(Qt.AlignHCenter)

    def update_path(self, user_path: Path):
        if user_path.exists():
            AppSettings.app['editor_path'] = user_path.as_posix()
