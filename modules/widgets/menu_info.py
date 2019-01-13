from PySide2.QtWidgets import QMenu, QMessageBox, QAction

from modules.gui.icon_resource import IconRsc
from modules.app_globals import APP_NAME
from modules.detect_language import get_translation
from modules.log import init_logging

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class InfoMenu(QMenu):
    def __init__(self, ui):
        super(InfoMenu, self).__init__('?', ui)
        self.ui = ui
        self.software_title = '{} v{}'.format(APP_NAME.capitalize(), self.ui.app.version)
        self.about_title = _("Über {} GPL v3").format(self.software_title)

        icon = IconRsc.get_icon('tieflader_icon')
        info = QAction(icon, self.about_title, self)
        info.triggered.connect(self.show_about_box)
        self.addAction(info)

        icon = IconRsc.get_icon('info')
        qt_info = QAction(icon, _('Über Qt'), self)
        qt_info.triggered.connect(self.show_about_qt)
        self.addAction(qt_info)

    def show_about_qt(self):
        QMessageBox.aboutQt(self.ui, self.about_title)

    def show_about_box(self):
        txt = _('<b>{0} licensed under GPL v3</b><br><i>Copyright © 2018 Stefan Tapper</i><br><br>'
                ''
                'Besuche den <a href="https://github.com/tappi287/tieflader">Quelltext@github</a>'
                ' dieser Software!<br><br>'
                ''
                '{0} ist <b>Freie Software</b>: Sie können es unter den Bedingungen '
                'der GNU General Public License, wie von der Free Software Foundation, '
                'Version 3 der Lizenz oder (nach Ihrer Wahl) jeder neueren '
                'veröffentlichten Version, weiter verteilen und/oder modifizieren.<br><br>'
                ''
                'Dieses Programm wird in der Hoffnung bereitgestellt, dass es nützlich sein wird, jedoch '
                'OHNE JEDE GEWÄHR,; sogar ohne die implizite '
                'Gewähr der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK. '
                'Siehe die GNU General Public License für weitere Einzelheiten.<br><br>'
                ''
                'Sie sollten eine Kopie der GNU General Public License zusammen mit diesem '
                'Programm erhalten haben. Wenn nicht, siehe '
                '<a href="http://www.gnu.org/licenses/">hier</a>.').format(self.software_title)

        about_box = QMessageBox.about(self.ui, self.about_title, txt)
