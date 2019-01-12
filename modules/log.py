import sys
from pathlib import Path
import logging
import logging.config

from logging.handlers import QueueHandler, QueueListener
from modules.app_globals import get_settings_dir, LOG_FILE_NAME


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
            'queue_formatter': {
                'format': '%(asctime)s %(name)s %(levelname)s: %(message)s', 'datefmt': '%d.%m.%Y %H:%M'},
            },
        'handlers': {
            'console': {
                'level': 'DEBUG', 'class': 'logging.StreamHandler',
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
                'queue': logging_queue, 'formatter': 'queue_formatter',
                },
            },
        'loggers': {
            # Main logger, these handlers will be moved to the QueueListener
            'tieflader': {
                'handlers': ['file', 'guiHandler', 'console'], 'propagate': False, 'level': 'DEBUG',
                },
            # Log Window Logger
            'gui_logger': {
                'handlers': ['guiHandler', 'queueHandler'], 'propagate': False, 'level': 'INFO'
                },
            # Module loggers
            '': {
                'handlers': ['queueHandler'], 'propagate': False, 'level': 'DEBUG',
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
    print('Logger requested by: ',
          Path(sys._getframe().f_back.f_code.co_filename).name,
          sys._getframe().f_back.f_code.co_name)

    logger_name = logger_name.replace('modules.', '')
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    return logger
