from PySide2.QtWidgets import QMessageBox
from modules.gui.icon_resource import IconRsc
from modules.detect_language import get_translation

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


def get_msg_box_icon(icon_key):
    if not icon_key:
        return IconRsc.get_icon('RK_Icon')
    else:
        return IconRsc.get_icon(icon_key)


class GenericMsgBox(QMessageBox):
    def __init__(self, parent, title: str = 'Message Box', text: str = 'Message Box.', icon_key=None, *__args):
        super(GenericMsgBox, self).__init__()
        self.parent = parent

        self.setWindowIcon(get_msg_box_icon(icon_key))

        self.setWindowTitle(title)
        self.setText(text)


class ExcelLoadFailedMsgBox(GenericMsgBox):
    title = _('Xml Datei oeffnen ...')

    text = _('Das gewaehlte Dokument konnte nicht geladen werden.<br><br>'
             'Es enthaelt entweder Keine oder keine unterstuetzten Daten.')

    icon_key = 'folder'

    def __init__(self, parent):
        super(ExcelLoadFailedMsgBox, self).__init__(parent, self.title, self.text, self.icon_key)


class QuestionBox:
    @staticmethod
    def ask(parent,
            title_txt: str = _('Frage'),
            message: str = '',
            ok_btn_txt: str=_('OK'),
            abort_btn_txt: str= _('Abbrechen')
            ) -> bool:
        """ Pop-Up Warning Box ask to continue or break, returns False on abort """
        msg_box = QMessageBox(QMessageBox.Question,
                              title_txt, message, parent=parent)

        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Abort)

        msg_box.button(QMessageBox.Ok).setText(ok_btn_txt)
        msg_box.button(QMessageBox.Abort).setText(abort_btn_txt)

        # Block until answered
        answer = msg_box.exec()

        if answer == QMessageBox.Abort:
            # User selected abort
            return False

        # User selected -Ok-, continue
        return True
