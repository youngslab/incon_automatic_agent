
import sys, time, os
import traceback
from data.incon import Incon
from market.g2b import G2B

from res.resource_manager import resource_manager as resmgr

import json,  datetime
import logging, logging.config

settings_enable_pres = True
settings_enable_bids = True




def update_handler_filename_if_neccessary(config:dict, handler_name:str, filename:str) -> bool:
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

def iaa_get_config_directory():
    dir = os.path.join(os.path.expanduser('~'), ".iaa")
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir

def iaa_get_config_file(filename):    
    return os.path.join(iaa_get_config_directory(), filename)

def iaa_load_logger_config():
    filepath = os.path.join(iaa_get_config_directory(),"logger.json")
    if not os.path.exists(filepath):
        return None        
    with open(filepath,'r') as f:
        config = json.load(f)
        return config

def iaa_get_log_filepath():
    filename = f'{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.txt'
    dir = os.path.join(iaa_get_config_directory(), "log")
    if not os.path.exists(dir):
        os.makedirs(dir)
    return os.path.join(dir, filename)


def iaa_configure_logger(config):
    filename = iaa_get_log_filepath()
    success = update_handler_filename_if_neccessary(config, "file", filename)
    if not success:
        raise Exception("Handler is not configured correctly. Please check your handler." \
            "\n - \"file\" handler exists" \
            "\n - \"filename\" should not be in \"file\" handler"
        )
    logging.config.dictConfig(config)

def iaa_get_default_logger_config():
    return {
        'version': 1,
        'disable_existing_loggers': False,
        "formatters": { 
            "standard": { 
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            }
        },  
        'loggers': {
            'file': {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "standard",
                'level': 'DEBUG',
            },
        }
    }

def create_data_provider():
    # create incon object
    id = resmgr.get_account("incon","id")
    pw = resmgr.get_account("incon","pw")
    return Incon(id, pw, headless=False)

def create_markets() -> dict:
    markets = dict()       
    pw = resmgr.get_account("g2b","pw")
    rn = resmgr.get_account("g2b","rn")
    markets['나라장터'] = G2B(pw, rn)
    return markets

def main():
    
    # logger setup
    logger_config = iaa_load_logger_config()
    if not logger_config:
        logger_config = iaa_get_default_logger_config()
    iaa_configure_logger(logger_config)
    logger = logging.getLogger(__name__)

    try:
        dp = create_data_provider()
        ms = create_markets()


        if settings_enable_pres:
            logger.info("Start pre market business.")
            pres = dp.get_pre_data()
            for pre in pres:
                market = ms.get(pre.market)
                if not market:
                    logger.debug(f"market({pre.market}) is not supported.")
                    continue

                if pre.is_completed():
                    logger.debug(f"pre({pre.number}) has already been completed.")
                    continue

                success = market.register(pre)
                if not success:
                    logger.error(f"failed to register a pre({pre.number}).")
                    continue

                pre.complete()
                time.sleep(0.1)
                if not pre.is_completed():
                    raise Exception(f"agent) Clicked But Not Completed {pre.number}")
                logger.info(f"agent) Registered {pre.number} - {pre.title} ")

        if settings_enable_bids:     
            logger.info("Start bid market business.")
            bids = dp.get_bid_data()
            for bid in bids:                
                market = ms.get(bid.market)
                if not market:
                    continue

                if bid.is_completed():
                    continue

                if not bid.is_ready:
                    continue

                success, message = market.participate(bid)

                if not success:
                    logger.warning(f"agent) Can not participate in {bid.number}, {bid.title} - {message}")

                bid.complete()
                logger.info(f"agent) Registered {bid.number} - {bid.title} ")

    except Exception as e:        
        traceback.print_exception(*sys.exc_info())
        logger.error(e)

if __name__ == "__main__":    
    main()
