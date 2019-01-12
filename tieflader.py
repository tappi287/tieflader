import sys
import logging
from pathlib import Path
from queue import Queue

from ui import gui_resource
from modules import AppSettings
from modules.gui.main_app import MainApp
from modules.gui.gui_utils import GuiExceptionHook
from modules.log import init_logging, setup_log_queue_listener
from modules.pyshop import PyShop

VERSION = '0.75'

# Prepare exception handling
# sys.excepthook = GuiExceptionHook.exception_hook


def initialize_log_listener():
    global LOGGER
    LOGGER = init_logging('tieflader')

    try:
        log_queue = AppSettings.log_queue
    except AttributeError or ReferenceError:
        log_queue = Queue(-1)

    # This will move all handlers from LOGGER to the queue listener
    log_listener = setup_log_queue_listener(LOGGER, log_queue)

    return log_listener


def shutdown(log_listener):
    # Shutdown logging and remove handlers
    LOGGER.info('Shutting down log queue listener and logging module.')
    log_listener.stop()
    logging.shutdown()
    sys.exit()


def example_2():
    psd = PyShop()

    for file in Path('_ts/bsp_2').glob('*.*'):
        psd.add_image_as_layer(file)

    output_file = psd.create_psd_from_existing('_ts/bsp_2/Pfade.psd', '_ts/bsp_2.psd')
    LOGGER.debug('PSD file saved at %s', output_file)


def example_1():
    psd = PyShop()

    for file in Path('_ts/bsp_1').glob('*.*'):
        psd.add_image_as_layer(file)

    output_file = psd.create_psd('_ts/bsp_1.psd')
    LOGGER.debug('PSD file saved at %s', output_file)


def main():
    #
    # ---- StartUp ----
    # Start log queue listener in it's own thread
    log_listener = initialize_log_listener()
    log_listener.start()

    LOGGER.debug('---------------------------------------')
    LOGGER.debug('Application start.')

    app = MainApp(VERSION)
    result = app.exec_()

    #
    #
    # ---- Application Result ----
    LOGGER.debug('---------------------------------------')
    LOGGER.debug('Qt Application finished with exitcode: %s', result)
    AppSettings.save()
    #
    #
    shutdown(log_listener)


if __name__ == "__main__":
    main()
