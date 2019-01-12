
"""
    Pfad Aeffchen language detection

    https://stackoverflow.com/questions/3425294/how-to-detect-the-os-default-language-in-python#3425316

    Copyright (C) 2017 Stefan Tapper, All rights reserved.

        This file is part of Pfad Aeffchen.

        Pfad Aeffchen is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        Pfad Aeffchen is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with Pfad Aeffchen.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import locale
import ctypes
from gettext import translation

from modules.app_globals import BASE_PATH


def get_ms_windows_language():
    """ Currently we only support english and german """
    windll = ctypes.windll.kernel32

    # Get the language setting of the Windows GUI
    try:
        os_lang = windll.GetUserDefaultUILanguage()
    except Exception as e:
        print(e)
        return

    # Convert language code to string
    lang = locale.windows_locale.get(os_lang)

    # Only return supported languages
    if not lang.startswith('de'):
        lang = 'en'

    # Return de or en
    return lang[:2]


def setup_translation(language=None):
    if not language:
        if not os.environ.get('LANGUAGE'):
            # Set from OS language en or de
            os.environ.setdefault('LANGUAGE', get_ms_windows_language())
    else:
        # Set language from settings
        os.environ.setdefault('LANGUAGE', language)


def get_translation():
    # Set OS language if not already set
    lang = os.environ.get('LANGUAGE')
    if not lang:
        if os.name == 'nt':
            lang = get_ms_windows_language()
        else:
            lang = 'de'

    os.environ.setdefault('LANGUAGE', lang)

    locale_dir = os.path.join(BASE_PATH, 'locale')
    return translation('tieflader', localedir=locale_dir)
