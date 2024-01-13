import logging


class MyLogger:
    """
    A class for configuring and using logging in Python.

    Args:
    - name (str): The logger's name (default is 'my_logger').
    - log_level (int): The logging level (default is logging.DEBUG).
    - log_file (str | None): The path to a log file (default is None, meaning no file logging).

    Methods:
    - set_log_level(log_level): Sets the logging level for the logger.
    - add_file_handler(log_file): Adds a file handler for logging to a file.
    - add_handler(handler): Adds a handler to the logger.
    - remove_handler(handler): Removes a handler from the logger.
    - log_exception(msg, *args, **kwargs): Logs an exception with a custom message and arguments.

    - get_logger(): Returns the logger object for usage.

    default format:
        logging.Formatter('[%(levelname)s] %(asctime)s: %(name)s %(module)s %(funcName)s:%(lineno)d - "%(message)s"')

    Example usage:
    ```
    logger = MyLogger().get_logger()
    logger.info("This is an informational message")
    logger.error("This is an error message")
    ```
    """

    def __init__(self, name: str = 'my_logger', log_level: int = logging.DEBUG, log_file: str | None = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.log_format = logging.Formatter(
            '[%(levelname)s] %(asctime)s: %(name)s %(module)s %(funcName)s:%(lineno)d - "%(message)s"')
        # Создаем обработчик для вывода лога в консоль
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.log_format)
        self.logger.addHandler(console_handler)

        # Если указан файл для логирования, создаем обработчик для записи в файл
        if log_file:
            self.add_file_handler(log_file)

    def set_log_level(self, log_level):
        self.logger.setLevel(log_level)

    def add_file_handler(self, log_file):
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(self.log_format)
        self.logger.addHandler(file_handler)

    def add_handler(self, handler):
        self.logger.addHandler(handler)

    def remove_handler(self, handler):
        self.logger.removeHandler(handler)

    def log_exception(self, msg, *args, **kwargs):
        self.logger.exception(msg, *args, **kwargs)

    def get_logger(self):
        return self.logger


logger = MyLogger('parser', 10).get_logger()


if __name__ == "__main__":
    pass
