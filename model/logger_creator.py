from logger_wrapper import LoggerWrapper

import logging
from logging.handlers import QueueHandler

class LoggerCreator:
    _level = None
    _queue = None
    _lock = None
    _format = ""
    _loggers = {}

    def __init__(self, queue, lock, format="%(message)s", level=logging.INFO):
        self._level = level
        self._queue = queue
        self._lock = lock
        self._format = format

    
    def create(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(self._level)

        handler = QueueHandler(self._queue)
        formatter = logging.Formatter(self._format)
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        wrapped_logger = LoggerWrapper(logger, self._lock)
        self._loggers[name] = wrapped_logger
        return wrapped_logger
    

    def get_logger(self, name):
        return self._loggers[name]
