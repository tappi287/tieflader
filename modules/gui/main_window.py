from pathlib import Path

from PySide2.QtCore import QTimer, Slot, Qt
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QCheckBox, QLabel

from modules import AppSettings
from modules.app_globals import Resource
from modules.detect_language import get_translation
from modules.gui.drop_action import FileDrop
from modules.gui.gui_utils import SetupWidget, replace_widget
from modules.gui.icon_resource import IconRsc
from modules.gui.main_menu import MainWindowMenu
from modules.log import init_logging
from modules.widgets.progress_overlay import ProgressOverlay
from modules.widgets.settings_dialog import ResolutionLineEdit

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class MainWindow(QMainWindow):
    expand_height = 80

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

        # --- Setup main window resolution box ---
        # Setup expand area
        self.res_btn: QPushButton
        self.res_label: QLabel

        # Setup Resolution line edits
        self.res_x_edit = self.replace_resolution_edit(self.res_x_edit)
        self.res_y_edit = self.replace_resolution_edit(self.res_y_edit)
        self.update_resolution(from_settings=True)
        self.res_x_edit.textEdited.connect(self.update_resolution)
        self.res_y_edit.textEdited.connect(self.update_resolution)

        # Setup expandable resolution widget
        self.res_widget.setVisible(self.res_btn.isChecked())

        # Prepare translations
        self.translations()

        # ---- Setup Main Menu ----
        self.main_menu = MainWindowMenu(self)

        # Setup Main Window Open PSD CheckBox
        self.open_psd_box: QCheckBox
        self.open_psd_box.setText(self.main_menu.settings_menu.open_action.text())
        self.open_psd_box.setChecked(self.main_menu.settings_menu.open_action.isChecked())
        self.open_psd_box.toggled.connect(self.main_menu.settings_menu.open_action.toggle)
        self.main_menu.settings_menu.open_action.toggled.connect(self._update_psd_box)

        self.adv_settings_btn: QPushButton
        self.adv_settings_btn.clicked.connect(self.main_menu.settings_menu.open_settings_dialog)

        # ---- Setup File Drop ----
        self.drop = FileDrop(self)

        QTimer.singleShot(10, self.delayed_setup)

    def delayed_setup(self):
        pass

    def closeEvent(self, close_event):
        close_event.ignore()
        self.app.quit()

    @staticmethod
    def replace_resolution_edit(default_widget: QWidget):
        parent = default_widget.parent()
        new_widget = ResolutionLineEdit(parent)
        replace_widget(default_widget, new_widget)

        return new_widget

    @Slot()
    def update_resolution(self, from_settings=False):
        def limit_res(res):
            return max(0, min(19999, res))

        if from_settings is True:
            self.res_x_edit.setText(str(AppSettings.app['psd_size'][0]))
            self.res_y_edit.setText(str(AppSettings.app['psd_size'][1]))

        x, y = int(self.res_x_edit.text()), int(self.res_y_edit.text())
        x, y = limit_res(x), limit_res(y)

        # Update Resolution Setting
        AppSettings.app['psd_size'] = (x, y)
        self.res_x_edit.setText(str(x))
        self.res_y_edit.setText(str(y))

    @Slot()
    def _update_psd_box(self):
        self.open_psd_box.blockSignals(True)
        self.open_psd_box.setChecked(self.main_menu.settings_menu.open_action.isChecked())
        self.open_psd_box.blockSignals(False)

    def translations(self):
        self.appLabel.setText(_('Bilddateien in dieses Fenster oder auf das Dock Icon ziehen um PSD zu erstellen'))

        self.cancelBtn.setText(_('Vorgang abbrechen'))
        self.lastFileBtn.setText(_('< Keine zuletzt verwendete Datei >'))

        self.res_btn.setText(_('Einstellungen'))
        self.res_btn.setStatusTip(_('Einstellungen einblenden'))
        self.res_label.setText(_('Zielauflösung in px'))
        self.adv_settings_btn.setText(_('Erweiterte Einstellungen'))

        editor = Path(AppSettings.app['editor_path'])
        if editor.exists() and editor.is_file():
            self.lastFileBtn.setDescription(_('Mit benutzerdefiniertem Editor öffnen'))
        else:
            self.lastFileBtn.setDescription(_('Mit Standardanwendung öffnen'))
