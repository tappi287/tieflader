import sys
import logging
from queue import Queue

from modules.gui.gui_utils import GuiExceptionHook
from modules.settings import delayed_log_setup
from ui import gui_resource
from modules import AppSettings
from modules.gui.main_app import MainApp
from modules.app_globals import APP_NAME
from modules.log import init_logging, setup_log_queue_listener, setup_logging

VERSION = '0.98'
AppSettings.app['version'] = VERSION

sys.excepthook = GuiExceptionHook.exception_hook


def initialize_log_listener(logging_queue):
    global LOGGER
    LOGGER = init_logging(APP_NAME)

    # This will move all handlers from LOGGER to the queue listener
    log_listener = setup_log_queue_listener(LOGGER, logging_queue)

    return log_listener


def shutdown(log_listener):
    # CleanUp Resources
    gui_resource.qCleanupResources()

    # Shutdown logging and remove handlers
    LOGGER.info('Shutting down log queue listener and logging module.')
    log_listener.stop()
    logging.shutdown()
    sys.exit()


def main():
    #
    # ---- StartUp ----
    # Start log queue listener in it's own thread
    logging_queue = Queue(-1)
    setup_logging(logging_queue)
    log_listener = initialize_log_listener(logging_queue)
    log_listener.start()

    # Setup KnechtSettings logger
    delayed_log_setup()

    LOGGER.info('---------------------------------------')
    LOGGER.info('Application start.')

    AppSettings.load()

    if not AppSettings.load_ui_resources():
        LOGGER.fatal('Can not locate UI resource files! Shutting down application.')
        shutdown(log_listener)
        return

    app = MainApp(VERSION, GuiExceptionHook)
    result = app.exec_()

    #
    #
    # ---- Application Result ----
    LOGGER.info('---------------------------------------')
    LOGGER.info('Qt Application finished with exitcode: %s', result)
    AppSettings.save()
    #
    #
    shutdown(log_listener)


if __name__ == "__main__":
    main()
