class LoggerWrapper:
    _logger = None
    _lock = None

    def __init__(self, logger, lock):
        self._logger = logger
        self._lock = lock


    def debug(self, msg):
        with self._lock:
            self._logger.debug(msg)

    
    def info(self, msg):
        with self._lock:
            self._logger.info(msg)


    def warning(self, msg):
        with self._lock:
            self._logger.warning(msg)


    def error(self, msg):
        with self._lock:
            self._logger.error(msg)


    def critical(self, msg):
        with self._lock:
            self._logger.critical(msg)