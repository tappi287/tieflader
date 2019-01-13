from pathlib import Path

from PIL import Image
from PySide2.QtCore import Qt, QRegExp, Slot
from PySide2.QtGui import QRegExpValidator
from PySide2.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QToolButton, QVBoxLayout, QComboBox

from modules.pyshop import PyShop
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


class SettingsDialog(QDialog):
    def __init__(self, ui):
        super(SettingsDialog, self).__init__(parent=ui)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(_('{} - Einstellungsdialog').format(APP_NAME.capitalize()))

        min_size = (768, 384)

        self.setMinimumSize(*min_size)

        if ui.size().width() < min_size[0]:
            ui.resize(*min_size)

        self.resize(*min_size)

        self.setStyleSheet('QLabel {'
                           '    padding: 0; margin: 0 13px 0 0;'
                           '}'
                           'QLineEdit, QComboBox {'
                           '    margin:  0 13px 0 0;'
                           '}'
                           'QPushButton {'
                           '    min-width: 180px; min-height: 30px;'
                           '}')


class ResolutionLineEdit(QLineEdit):
    regex = QRegExp('^\d{1,5}$')
    regex.setCaseSensitivity(Qt.CaseInsensitive)
    validator = QRegExpValidator(regex)

    def __init__(self, parent):
        super(ResolutionLineEdit, self).__init__(parent)
        self.setValidator(self.validator)


class ResampleFilterSetting(QComboBox):
    values = [
        ('Bilinear', Image.BILINEAR, _('Schnell - niedrige Qualität.')),
        ('Hamming', Image.HAMMING, _('Schnell - vertretbare Qualität beim Verkleinern.')),
        ('Bicubic', Image.BICUBIC, _('Langsam - Sehr gute Qualität beim Verkleinern und Vergrößern')),
        ('Lanczos', Image.LANCZOS, _('Sehr Langsam - Sehr gute Qualität. Ergebnis erscheint schärfer.'))
        ]

    default_value_idx = 2  # Bicubic

    def __init__(self, parent, desc_label: QLabel):
        super(ResampleFilterSetting, self).__init__(parent)
        self.desc_label = desc_label
        self.desc_text = self.desc_label.text()

        self.currentIndexChanged.connect(self.update_setting)

        current_setting_idx = self.default_value_idx

        for idx, (text, data, description) in enumerate(self.values):
            self.addItem(text, data)

            if text == AppSettings.app['resampling_filter']:
                current_setting_idx = idx

        self.setCurrentIndex(current_setting_idx)

    @Slot(int)
    def update_setting(self, current_idx):
        description = '{}<br><b>{}:</b> {}'.format(self.desc_text,  # Filter setting description
                                                   self.values[current_idx][0],  # Filter name
                                                   self.values[current_idx][2],  # Filter description
                                                   )
        self.desc_label.setText(description)


class PhotoshopSettings(SettingsDialog):
    psd_editor_path = ''

    def __init__(self, ui):
        super(PhotoshopSettings, self).__init__(ui)
        self.ui = ui
        self.accepted.connect(self.update_settings)

        # Load Path Setting on open
        self.psd_editor_path = AppSettings.app['editor_path']

        vbox = QVBoxLayout(self)
        vbox.setSpacing(0)
        vbox.setContentsMargins(13, 13, 13, 13)
        resolution_box = QHBoxLayout()
        resolution_box.setContentsMargins(13, 13, 13, 26)
        filter_box = QHBoxLayout()
        filter_box.setContentsMargins(13, 13, 13, 26)
        path_box = QHBoxLayout()
        path_box.setContentsMargins(13, 13, 13, 26)
        dialog_btn_box = QHBoxLayout()
        dialog_btn_box.setSpacing(13)

        # --- Description ---
        self.desc = QLabel(self)
        self.desc.setWordWrap(True)
        self.desc.setText(_('<h3>Erweiterte Einstellungen</h3>'
                            '<h4 style="margin: 2px 0;">Auflösung</h4>'
                            'Pixel-Auflösung der Photoshop Datei. '
                            'Bildinhalte der Ebenen werden zu dieser Auflösung skaliert.'
                            ))
        vbox.addWidget(self.desc)

        # --- Resolution Settings ---
        res_lbl = QLabel(_('Auflösung'), self)
        resolution_box.addWidget(res_lbl)
        x_lbl = QLabel('x', self)
        self.x_edit, self.y_edit = ResolutionLineEdit(self), ResolutionLineEdit(self)
        self.x_edit.setText(str(AppSettings.app['psd_size'][0]))
        self.y_edit.setText(str(AppSettings.app['psd_size'][1]))
        resolution_box.addWidget(self.x_edit)
        resolution_box.addWidget(x_lbl)
        resolution_box.addWidget(self.y_edit)

        vbox.addLayout(resolution_box)

        # --- Resampling Filter Setting ---
        filter_title = QLabel(_('<h4 style="margin: 2px 0;">Umrechnungsfilter</h4>'
                                'Filter der bei Größenänderungen angewandt wird.<br>'), self)
        vbox.addWidget(filter_title)

        filter_lbl = QLabel(_('Filter wählen:'), self)
        filter_box.addWidget(filter_lbl)

        self.filter_combo_box = ResampleFilterSetting(self, filter_title)

        filter_box.addWidget(self.filter_combo_box)
        vbox.addLayout(filter_box)

        # --- Path Settings ---
        path_desc = QLabel(self)
        path_desc.setWordWrap(True)
        path_desc.setText(_('<h4 style="margin: 2px 0;">Photoshop Editor Pfad</h4>'
                            'Pfad zur ausführbaren Anwendung angeben mit der das erstellte Dokument '
                            'geöffnet werden soll.<br><br>'
                            ''
                            'Sollte kein Pfad festgelegt werden(Voreinstellung) wird '
                            'die vom Betriebssystem assozierte Anwendung '
                            'zum öffnen des Dokumentes verwendet. Die Voreinstellung '
                            'ist die zuverlässigste Einstellung.'))
        vbox.addWidget(path_desc)

        path_line = QLineEdit(self)
        path_line.setText(AppSettings.app['editor_path'])
        path_box.addWidget(path_line)

        path_btn = QToolButton(self)
        path_btn.setIcon(IconRsc.get_icon('folder'))
        path_box.addWidget(path_btn)

        vbox.addLayout(path_box)

        self.path_util = SetDirectoryPath(
            ui.app, ui, line_edit=path_line, tool_button=path_btn, mode='file', reject_invalid_path_edits=True,
            )
        self.path_util.path_changed.connect(self.update_path)

        # --- Dialog Buttons ---
        vbox.addLayout(dialog_btn_box)

        ok_btn = QPushButton(_('OK'), self)
        ok_btn.setDefault(False)
        ok_btn.pressed.connect(self.accept)

        cancel_btn = QPushButton(_('Abbrechen'), self)
        cancel_btn.setDefault(True)
        cancel_btn.pressed.connect(self.reject)

        reset_btn = QPushButton(_('Zurücksetzen'))
        reset_btn.pressed.connect(self.reset)

        dialog_btn_box.addWidget(ok_btn)
        dialog_btn_box.addWidget(cancel_btn)
        dialog_btn_box.addWidget(reset_btn)
        dialog_btn_box.setAlignment(Qt.AlignHCenter)

    def update_settings(self):
        """ Update Settings if Dialog was accepted """

        # Update Resolution Setting
        AppSettings.app['psd_size'] = (int(self.x_edit.text()), int(self.y_edit.text()))

        # Update Resample Filter Setting
        AppSettings.app['resampling_filter'] = self.filter_combo_box.currentText()

        # Update Photoshop Editor Path Setting
        if self.psd_editor_path:
            AppSettings.app['editor_path'] = self.psd_editor_path

    def update_path(self, user_path: Path):
        if user_path.exists() and user_path.is_file():
            self.psd_editor_path = user_path.as_posix()

    def reset(self):
        AppSettings.app['editor_path'] = ''
        AppSettings.app['psd_size'] = PyShop.default_img_size

        for (name, filter_setting, desc) in ResampleFilterSetting.values:
            if filter_setting == PyShop.default_resample_filter:
                AppSettings.app['resampling_filter'] = name

        self.reject()
