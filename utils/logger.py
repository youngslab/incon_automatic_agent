import logging
import os
import json
import datetime
import logging
import logging.config


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

def logger_update_handler_filename_if_neccessary(config: dict, handler_name: str, filename: str) -> bool:
    if not 'handlers' in config.keys():
        return False

    handlers = config['handlers']
    if not handler_name in handlers.keys():
        return False

    handler = handlers[handler_name]
    if 'filename' in handler.keys():
        return False

    handler['filename'] = filename
    return True


def iaa_load_logger_config(filepath):
    if not os.path.exists(filepath):
        return None

    print("open logger.json")
    with open(filepath, 'r') as f:
        config = json.load(f)
        return config


def logger_create_log_filepath(basedir):
    filename = f'{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.txt'
    dir = os.path.join(basedir, "log")
    if not os.path.exists(dir):
        os.makedirs(dir)
    return os.path.join(dir, filename)


def logger_get_default_config():
    return {
        'version': 1,
        'disable_existing_loggers': True,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname).1s] %(name)7s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "standard"
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "WDM": {
                "handlers": [],
                "level": "CRITICAL",
                "propagate": False
            }
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
            # "propagate": True
        }
    }

# precondition
# base: logger.json file exists. and
# {base}/log/{date}.log


def logger_init(basedir: str = None, new_log_file=True):
    config = logger_get_default_config()

    if basedir:

        config_file = os.path.join(basedir, "logger.json")
        if os.path.exists(config_file):
            config = iaa_load_logger_config(config_file)

        # create a new lof file of "file" logger at {basedir}/log/xxxxxx-xxxxxx.txt
        # logger should have name - "file".
        if new_log_file:
            log_filepath = logger_create_log_filepath(basedir)
            logger_update_handler_filename_if_neccessary(
                config, "file", log_filepath)

    logging.config.dictConfig(config)
