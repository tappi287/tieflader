from pathlib import Path
from threading import Thread
from typing import List

from PySide2.QtCore import QObject, Signal, Slot

from modules import AppSettings
from modules.detect_language import get_translation
from modules.log import init_logging
from modules.pyshop import PyShop
from modules.widgets.settings_dialog import ResampleFilterSetting

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class CreateLayeredPsdSignals(QObject):
    started = Signal()
    progress_step = Signal()
    finished = Signal()
    file_created = Signal(Path)


class CreateLayeredPsdThread(Thread):
    counter = 0
    psd_base_name = _('Dateien')
    psd_name_suffix = _('Stapel')

    def __init__(self, parent, files: List[Path]):
        super(CreateLayeredPsdThread, self).__init__()
        self.parent = parent
        self.files = files
        self.abort = False

        self.size = AppSettings.app['psd_size']

        for (name, filter_setting, desc) in ResampleFilterSetting.values:
            if name == AppSettings.app['resampling_filter']:
                self.resample_filter = filter_setting

        self.signals = CreateLayeredPsdSignals()

        if files:
            self.current_dir = files[0].parent
        else:
            self.current_dir = Path('.')

    @Slot()
    def abort_creation(self):
        self.abort = True

    def _abort(self):
        self.files = list()
        self.signals.finished.emit()

    def run(self):
        if not self.files:
            return

        self.signals.started.emit()
        pyshop = PyShop(self.size, self.resample_filter)

        for file in reversed(sorted(self.files)):
            self.signals.progress_step.emit()

            if self.abort:
                del pyshop
                self._abort()
                return

            pyshop.add_image_as_layer(file)

        if self.abort:
            del pyshop
            self._abort()
            return

        psd_file = self._create_psd_path()
        pyshop.create_psd(psd_file=psd_file)

        self.signals.finished.emit()
        self.signals.file_created.emit(psd_file)

    def _create_psd_name(self) -> str:
        return f'{self.psd_base_name}_{self.counter:02d}_{self.psd_name_suffix}.psd'

    def _create_psd_path(self):
        psd_name: str = self._create_psd_name()
        psd_path: Path = self.current_dir / psd_name

        while psd_path.exists():
            self.counter += 1
            psd_name: str = self._create_psd_name()
            psd_path: Path = self.current_dir / psd_name

            if CreateLayeredPsdThread.counter >= 99:
                LOGGER.error('Could not find a unique Psd file name!')
                break

        return psd_path
