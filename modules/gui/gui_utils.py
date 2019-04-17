import datetime
import logging

from pathlib import Path

from PySide2.QtCore import QObject, QFile, Signal
from modules.gui.ui_loader import loadUi

from modules.app_globals import UI_PATH, get_settings_dir
from modules.log import init_logging

LOGGER = init_logging(__name__)


class SetupWidget(QObject):
    @staticmethod
    def from_ui_file(widget_cls, ui_file, custom_widgets=dict()):
        """ Load a Qt .ui file to setup the provided widget """
        # Store current log level and set it to ERROR for Ui load
        current_log_level = logging.root.getEffectiveLevel()
        logging.root.setLevel(logging.ERROR)

        # Load the Ui file
        ui_file = Path(UI_PATH + '/' + ui_file)
        file = QFile(ui_file.as_posix())
        file.open(QFile.ReadOnly)
        loadUi(file, widget_cls, custom_widgets)
        file.close()

        # Restore previous log level
        logging.root.setLevel(current_log_level)


def replace_widget(old_widget, new_widget):
    parent = old_widget.parent()
    layout = parent.layout()
    layout.replaceWidget(old_widget, new_widget)
    old_widget.deleteLater()


class ConnectCall(QObject):
    def __init__(self, *args, target=None, parent=None):
        super(ConnectCall, self).__init__(parent=parent)
        self.args = args
        self.target = target

    def call(self):
        self.target(*self.args)


class ExceptionSignal(QObject):
    exception_signal = Signal(str)


class GuiExceptionHook:
    app = None
    signals = None
    signal_destination = None

    @classmethod
    def exception_hook(cls, etype, value, tb):
        """ sys.excepthook will call this method """
        import traceback

        # Print exception
        traceback.print_exception(etype, value, tb)

        # Log exception
        stacktrace_msg = ''.join(traceback.format_tb(tb))
        if etype:
            exception_msg = '{0}: {1}'.format(etype, value)
        else:
            exception_msg = 'Exception: {}'.format(value)

        LOGGER.critical(stacktrace_msg)
        LOGGER.critical(exception_msg)

        # Write to exception log file
        exception_file_name = datetime.datetime.now().strftime('Tieflader_Exception_%Y-%m-%d_%H%M%S.log')
        settings_dir = Path(get_settings_dir())
        exception_file = settings_dir / exception_file_name

        with open(exception_file, 'w') as f:
            traceback.print_exception(etype, value, tb, file=f)

        # Inform GUI of exception if QApplication set
        if cls.app:
            gui_msg = f'{stacktrace_msg}\n{exception_msg}'
            cls.send_exception_signal(gui_msg)

    @classmethod
    def setup_signal_destination(cls, dest):
        """ Setup GUI exception receiver from QApplication"""
        cls.signal_destination = dest

    @classmethod
    def send_exception_signal(cls, msg):
        """ This will fail if not run inside a QApplication """
        cls.signals = ExceptionSignal()
        cls.signals.exception_signal.connect(cls.signal_destination)
        cls.signals.exception_signal.emit(msg)
