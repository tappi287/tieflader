from pathlib import Path
from typing import List
from subprocess import Popen

from PySide2.QtGui import QDesktopServices
from PySide2.QtCore import QObject, QEvent, Qt, Signal, QUrl, QTimer

from modules import AppSettings
from modules.detect_language import get_translation
from modules.log import init_logging
from modules.pyshop import PyShop
from modules.run_pyshop import CreateLayeredPsdThread

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class FileDrop(QObject):
    cancel_thread = Signal()
    current_psd_file = Path('.')

    def __init__(self, ui):
        """ Initializes file drag&drop events on to the Main Window and handles the py shop layering threads.

        :param modules.gui.main_window.MainWindow ui: Application QMainWindow
        """
        super(FileDrop, self).__init__(parent=ui)
        self.ui = ui

        self.ui.cancelBtn.released.connect(self.cancel_thread)

        # --- Install file drop on main window ---
        self.ui.setAttribute(Qt.WA_AcceptDrops)
        self.ui.installEventFilter(self)

        # -- Open file delay --
        self.file_timer = QTimer()
        self.file_timer.setInterval(1500)
        self.file_timer.setSingleShot(True)
        self.file_timer.timeout.connect(self._open_psd_file)

        self.py_shop_thread = CreateLayeredPsdThread(self, list())

    def thread_started(self):
        self.ui.progress_widget.progress.setValue(0)
        self.ui.progress_widget.progress.show()
        self.ui.cancelBtn.setEnabled(True)

    def thread_progress(self):
        progress = self.ui.progress_widget.progress.value()
        progress += 1
        self.ui.progress_widget.progress.setValue(progress)

    def thread_finished(self):
        self.ui.progress_widget.progress.hide()
        self.ui.cancelBtn.setEnabled(False)

    def thread_file_created(self, psd_file: Path):
        self.current_psd_file = psd_file
        self.file_timer.start()

    # noinspection PyCallByClass,PyTypeChecker
    def _open_psd_file(self):
        if AppSettings.app['open_editor']:
            external_app_path: Path = Path(AppSettings.app['editor_path'])

            if external_app_path.exists() and external_app_path.is_file():
                # Open Psd in user defined editor
                args = [external_app_path.as_posix(), self.current_psd_file.resolve().__str__()]
                Popen(args)
            else:
                # Open psd thru QDesktopService with OS associated app
                file_url = QUrl.fromLocalFile(self.current_psd_file.as_posix())
                QDesktopServices.openUrl(file_url)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.DragEnter:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            return True

        if event.type() == QEvent.Drop:
            mime = event.mimeData()
            if self.file_drop(mime):
                return True

        return False

    def file_drop(self, mime):
        if not mime.hasUrls():
            return False

        if not mime.urls()[0].isLocalFile():
            return False

        file_paths = list()
        for file_url in mime.urls():
            if not file_url.isLocalFile():
                continue

            local_file_path = Path(file_url.toLocalFile())

            if local_file_path.suffix.casefold() not in PyShop.supported_img or not local_file_path.is_file():
                continue

            file_paths.append(local_file_path)
            LOGGER.debug('Dropped local file: %s', local_file_path.name)

        if not file_paths:
            return False

        self.run_py_shop(file_paths)
        return True

    def run_py_shop(self, files: List[Path]):
        if self.py_shop_thread.is_alive():
            return

        self.ui.progress_widget.progress.setMaximum(len(files))

        self.py_shop_thread = CreateLayeredPsdThread(self, files)

        self.py_shop_thread.signals.started.connect(self.thread_started)
        self.py_shop_thread.signals.progress_step.connect(self.thread_progress)
        self.py_shop_thread.signals.finished.connect(self.thread_finished)
        self.py_shop_thread.signals.file_created.connect(self.thread_file_created)
        self.cancel_thread.connect(self.py_shop_thread.abort_creation)

        self.py_shop_thread.start()
