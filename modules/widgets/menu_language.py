from PySide2.QtWidgets import QMainWindow, QMenu, QAction

from modules import AppSettings
from modules.gui.gui_utils import ConnectCall
from modules.widgets.message_box import GenericMsgBox
from modules.detect_language import get_translation
from modules.log import init_logging

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class LanguageMenu(QMenu):
    def __init__(self, ui: QMainWindow):
        super(LanguageMenu, self).__init__(_("Sprache"), ui)
        self.ui = ui
        self.en, self.de = QAction(), QAction()
        self.setup()

    def setup(self):
        self.en = QAction('English [en]', self)
        self.en.setCheckable(True)
        en_call = ConnectCall('en', target=self.change_language, parent=self.en)
        self.en.triggered.connect(en_call.call)

        self.de = QAction('Deutsch [de]', self)
        self.de.setCheckable(True)
        de_call = ConnectCall('de', target=self.change_language, parent=self.de)
        self.de.triggered.connect(de_call.call)
        self.addActions([self.de, self.en])

        self.aboutToShow.connect(self.update_menu)

    def change_language(self, l: str):
        if AppSettings.language == l:
            return

        if 'de' == l:
            title = 'Sprache auswählen'
            msg = 'Die Anwendung muss neu gestartet werden um die Sprache auf Deutsch zu aendern.<br>' \
                  'Bitte File > Exit waehlen und Anwendung anschließend erneut starten.'
        else:
            title = 'Change Language'
            msg = 'The Application needs to be restarted to change the language to English.<br>' \
                  'Please choose Datei > Beenden to exit and then start the application again.'

        AppSettings.language = l

        msg_box = GenericMsgBox(self.ui, title, msg)
        msg_box.exec()

    def update_menu(self):
        self.de.setChecked(False)
        self.en.setChecked(False)

        if AppSettings.language.casefold() == 'de':
            self.de.setChecked(True)
        elif AppSettings.language.casefold() == 'en':
            self.en.setChecked(True)
