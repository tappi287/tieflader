"""
    This setup should be imported before any application modules are imported.

    Imported only -ONCE- from main.
"""
import sys

from modules.log import DefaultLogLevel
from modules.settings import AppSettings

# Set log level based on Release / Debug
if getattr(sys, '_MEIPASS', False):
    DefaultLogLevel.level = 'INFO'
else:
    DefaultLogLevel.level = 'DEBUG'

try:
    AppSettings.load()
except Exception as e:
    print('Error loading settings from file!\n%s', e)
