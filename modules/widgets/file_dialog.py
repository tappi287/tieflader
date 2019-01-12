import os

from typing import Union
from pathlib import Path
from PySide2.QtWidgets import QFileDialog

from modules.settings import AppSettings
from modules.log import init_logging
from modules.detect_language import get_translation

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class FileDialog:
    """
        Shorthand class to create file dialogs. Dialog will block.
            file_key: see class attribute file_types
    """
    file_types = dict(
        tif=dict(title=_('Tiff Datei auswaehlen'), filter=_('Tif (*.tif; *.tiff)')),
        xlsx=dict(title=_('Excel Dateien *.xlsx auswaehlen'), filter=_('Excel Dateien (*.xlsx)')),
        dir=dict(title=_('Verzeichnis auswaehlen ...'), filter=None)
        )

    @classmethod
    def open(cls,
             parent=None, directory: Union[Path, str]=None, file_key: str= 'xlsx'
             ) -> Union[str, None]:
        return cls.open_existing_file(parent, directory, file_key)

    @classmethod
    def open_dir(cls,
                 parent=None, directory: Union[Path, str] = None
                 ) -> Union[str, None]:
        return cls.open_existing_directory(parent, directory)

    @classmethod
    def open_existing_file(cls, parent=None,
                           directory: Union[Path, str]=None,
                           file_key: str= 'xml') -> Union[str, None]:
        # Update path
        directory = cls._get_current_path(directory)

        # Update filter and title depending on file type
        if file_key not in cls.file_types.keys():
            file_key = 'tif'

        title = cls.file_types[file_key]['title']
        file_filter = cls.file_types[file_key]['filter']

        file, file_ext = cls.__create_file_dialog(parent, title, directory, file_filter)

        if file and Path(file).exists():
            AppSettings.app['current_path'] = Path(file).parent.as_posix()
            AppSettings.add_recent_file(file, file_key)

        return file

    @classmethod
    def open_existing_directory(cls, parent=None, directory: Union[Path, str]=None,) -> Union[str, None]:
        # Update path
        directory = cls._get_current_path(directory)

        title = cls.file_types['dir']['title']

        directory = cls.__create_dir_dialog(parent, title, directory)

        if directory and Path(directory).exists():
            AppSettings.app['current_path'] = Path(directory).as_posix()

        return directory

    # -------------------------------
    # ------- Dialog creation -------
    @staticmethod
    def __create_file_dialog(parent, title: str, directory: Path, file_filter: str) -> Union[str, None]:
        # Create and configure File Dialog
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFile)

        # This will block until the user has selected a file or canceled
        return dlg.getOpenFileName(parent, title, directory.as_posix(), file_filter)

    @staticmethod
    def __create_dir_dialog(parent, title: str, directory: Path) -> Union[str, None]:
        dlg = QFileDialog()

        # This will block until the user has selected a directory or canceled
        return dlg.getExistingDirectory(parent, caption=title, directory=directory.as_posix())

    # -----------------------------------
    # ------- Path helper methods -------
    @staticmethod
    def _get_current_path(d) -> Path:
        # Current settings path
        __c = Path(AppSettings.app['current_path'])
        # Fallback path USERPROFILE path or current directory '.'
        __fallback = Path(os.getenv('USERPROFILE', '.'))

        if not d or not Path(d).exists():
            if AppSettings.app['current_path'] not in ['', '.'] and __c.exists():
                # Set to settings current_path and continue with file vs. dir check
                d = __c
            else:
                return __fallback

        if Path(d).is_file():
            if Path(d).parent.exists():
                # Remove file and return directory
                return Path(d).parent
            else:
                return __fallback

        return Path(d)
