import os
import sys

from appdirs import user_data_dir

APP_NAME = 'tieflader'

# Base path depending on running in dev or PyInstaller
BASE_PATH = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__ + '/..')))

UI_PATH = os.path.join(BASE_PATH, 'ui')
UI_PATHS_FILE = 'gui_resource_paths.json'

LOG_FILE_NAME = 'tieflader.log'

SETTINGS_FILE = 'settings.json'
SETTINGS_DIR_NAME = 'tieflader'


def get_current_modules_dir():
    """ Return path to this app modules directory """
    return BASE_PATH


def get_settings_dir() -> str:
    _knecht_settings_dir = user_data_dir(SETTINGS_DIR_NAME, '')

    if not os.path.exists(_knecht_settings_dir):
        try:
            os.mkdir(_knecht_settings_dir)
        except Exception as e:
            print('Error creating settings directory', e)
            return ''

    return _knecht_settings_dir


class Resource:
    """
        Qt resource paths for ui files and icons.
        Will be loaded from json dict on startup.

        create_gui_resource.py will create the json file for us.
        ui_path[filename] = relative path to ui file
        icon_path[filename] = Qt resource path
    """
    ui_paths = dict()
    icon_paths = dict()
