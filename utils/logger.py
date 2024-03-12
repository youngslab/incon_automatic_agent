import logging


class Logger:
    def __init__(self, name, *, loglevel=logging.INFO):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(loglevel)
        self.logger.handlers.clear()

        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
