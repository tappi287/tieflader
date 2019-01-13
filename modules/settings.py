import json
import os
from pathlib import Path
from typing import Union, Any

from modules.app_globals import Resource, UI_PATH, UI_PATHS_FILE, SETTINGS_FILE
from modules.app_globals import get_settings_dir
from modules.log import init_logging
from modules.detect_language import setup_translation

LOGGER = init_logging(__name__)


def delayed_log_setup():
    from modules.log import init_logging
    global LOGGER
    LOGGER = init_logging(__name__)


class Settings:
    """
        Load and save methods to save class attributes of setting classes
    """
    @staticmethod
    def load(obj: object, file):
        try:
            with open(file, 'r') as f:
                load_dict = json.load(f, encoding='utf-8')
        except Exception as e:
            LOGGER.error('Could not load setting data:\n%s', e)
            return

        for key, attr in load_dict.items():
            setattr(obj, key, attr)

    @staticmethod
    def save(obj: object, file: Union[Path, str]):
        save_dict = dict()

        for key, value in obj.__dict__.items():
            if key.startswith('__'):
                # Skip internal attributes
                continue

            if not Settings.is_serializable(value):
                # Skip non-serializable data
                continue

            LOGGER.debug('Saving %s: %s', key, value)
            save_dict.update({key: value})

        try:
            with open(file, 'w') as f:
                json.dump(save_dict, f, indent='\t')

            LOGGER.info('Saved settings to file: %s', file.absolute().as_posix())
        except Exception as e:
            LOGGER.error('Could not save file!\n%s', e)

    @staticmethod
    def is_serializable(data: Any) -> bool:
        try:
            json.dumps(data)
            return True
        except Exception as e:
            LOGGER.debug(e)

        return False


class AppSettings:
    """
        Store and Re-store application settings

        Settings are stored inside this class as class attributes(not instanced)
    """
    # --- Default values ----
    app = dict(
        version='0.0.0',
        current_path='',
        introduction_shown=False,
        recent_files=list(),
        open_editor=False,
        editor_path='.',
        psd_size=(1920, 1080),
        resampling_filter='Bicubic'
        )

    language = 'de'

    log_queue = None

    @classmethod
    def load(cls) -> None:
        file = Path(cls.get_settings_path())

        if not file or not file.exists():
            LOGGER.warning('Could not locate settings file! Using default settings!')
            return

        default_settings = dict()
        default_settings.update(cls.app)

        Settings.load(AppSettings, file)

        for k, v in default_settings.items():
            # Make sure all default keys exists if
            # settings are migrated from older version
            if k not in cls.app:
                cls.app[k] = v

        cls.setup_lang()
        LOGGER.debug('AppSettings successfully loaded from file.')

    @classmethod
    def save(cls) -> None:
        file = Path(cls.get_settings_path())

        if not file:
            LOGGER.warning('Could not save settings file! No setting will be saved.')
            return

        Settings.save(cls, file)

    @staticmethod
    def setup_lang():
        setup_translation(language=AppSettings.language)
        LOGGER.debug('Application language loaded from settings: %s', AppSettings.language)

    @classmethod
    def load_ui_resources(cls) -> bool:
        """ update app globals with GUI resource paths """
        ui_paths_file = Path(UI_PATH) / Path(UI_PATHS_FILE)

        if not ui_paths_file.exists():
            LOGGER.fatal('Could not locate gui resource file: %s. Aborting application.',
                         ui_paths_file.absolute().as_posix())
            return False

        try:
            Settings.load(Resource, ui_paths_file)
        except Exception as e:
            LOGGER.fatal('Could not load GUI resources from file %s. Aborting application. Error:\n%s',
                         ui_paths_file.absolute().as_posix(), e)
            return False
        return True

    @classmethod
    def add_recent_file(cls, file: Union[Path, str], file_type: str='', list_length: int=10) -> None:
        if 'recent_files' not in cls.app.keys():
            cls.app['recent_files'] = list()

        file_str = Path(file).as_posix()
        recent_files = cls.app['recent_files']

        # Remove already existing/duplicate entry's
        for idx, entry in enumerate(recent_files):
            entry_file, entry_type = entry

            if file_str == entry_file and file_type == entry_type:
                recent_files.pop(idx)

        recent_files.insert(0, (file_str, file_type))

        # Only keep the last [list_length] number of items
        if len(recent_files) > list_length:
            recent_files = recent_files[:list_length]

    @staticmethod
    def get_settings_path() -> str:
        _knecht_settings_dir = get_settings_dir()
        _knecht_settings_file = os.path.join(_knecht_settings_dir, SETTINGS_FILE)

        return _knecht_settings_file
