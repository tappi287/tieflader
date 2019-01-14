import logging
import logging.config
import sys
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path

from modules.app_globals import LOG_FILE_NAME, get_settings_dir, APP_NAME


class DefaultLogLevel:
    level = 'DEBUG'


def setup_logging(logging_queue):
    # Track calls to this method
    print('Logging setup called: ',
          Path(sys._getframe().f_back.f_code.co_filename).name,
          sys._getframe().f_back.f_code.co_name)

    log_file_path = Path(get_settings_dir()) / Path(LOG_FILE_NAME)

    log_conf = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
                },
            'simple': {
                'format': '%(asctime)s %(name)s %(levelname)s: %(message)s',
                'datefmt': '%d.%m.%Y %H:%M'
                },
            'guiFormatter': {
                'format': '%(name)s %(levelname)s: %(message)s',
                'datefmt': '%d.%m.%Y %H:%M',
                },
            'file_formatter': {
                'format': '%(asctime)s.%(msecs)03d %(name)s %(levelname)s: %(message)s',
                'datefmt': '%d.%m.%Y %H:%M:%S'
                },
            },
        'handlers': {
            'console': {
                'level': 'INFO', 'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout', 'formatter': 'simple'
                },
            'guiHandler': {
                'level': 'INFO', 'class': 'logging.NullHandler',
                'formatter': 'simple',
                },
            'file': {
                'level': 'DEBUG', 'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_file_path.absolute().as_posix(), 'maxBytes': 5000000, 'backupCount': 4,
                'formatter': 'file_formatter',
                },
            'queueHandler': {
                'level': 'DEBUG', 'class': 'logging.handlers.QueueHandler',
                # From Python 3.7.1 defining a formatter will output the formatter of the queueHandler
                # as well as the re-routed handler formatter eg. console -> queue listener
                'queue': logging_queue
                },
            },
        'loggers': {
            # Main logger, these handlers will be moved to the QueueListener
            APP_NAME: {
                'handlers': ['file', 'guiHandler', 'console'], 'propagate': False, 'level': DefaultLogLevel.level,
                },
            # Log Window Logger
            'gui_logger': {
                'handlers': ['guiHandler', 'queueHandler'], 'propagate': False, 'level': 'INFO'
                },
            # Module loggers
            '': {
                'handlers': ['queueHandler'], 'propagate': False, 'level': DefaultLogLevel.level,
                }
            }
        }

    logging.config.dictConfig(log_conf)


def setup_log_queue_listener(logger, queue):
    """
        Moves handlers from logger to QueueListener and returns the listener
        The listener needs to be started afterwwards with it's start method.
    """
    handler_ls = list()
    for handler in logger.handlers:
        print('Removing handler that will be added to queue listener: ', str(handler))
        handler_ls.append(handler)

    for handler in handler_ls:
        logger.removeHandler(handler)

    handler_ls = tuple(handler_ls)
    queue_handler = QueueHandler(queue)
    logger.addHandler(queue_handler)

    listener = QueueListener(queue, *handler_ls)
    return listener


def init_logging(logger_name):
    logger_name = logger_name.replace('modules.', '')
    logger = logging.getLogger(logger_name)

    print('Logger requested by: ',
          Path(sys._getframe().f_back.f_code.co_filename).name,
          sys._getframe().f_back.f_code.co_name, logging.getLevelName(logger.getEffectiveLevel()))

    return logger
