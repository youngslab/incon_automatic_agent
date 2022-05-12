
import sys
import time
import os
import traceback
from org.incon import Incon
from org.g2b.g2b import G2B

import logging
from account import account_get
from logger import logger_init


settings_enable_pres = True
settings_enable_bids = True


def create_data_provider():
    # create incon object
    id = account_get("incon", "id")
    pw = account_get("incon", "pw")
    return Incon(id, pw)


def create_markets() -> dict:
    markets = dict()
    pw = account_get("g2b", "pw")
    rn = account_get("g2b", "rn")
    markets['나라장터'] = G2B(pw, rn)
    return markets


def iaa_get_config_directory():
    dir = os.path.join(os.path.expanduser('~'), ".iaa")
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir


def log():
    return logging.getLogger(__name__)


def main():
    dp = create_data_provider()
    ms = create_markets()

    if settings_enable_pres:
        log().info("Start pre market business.")
        pres = dp.get_pre_data()
        for pre in pres:
            log().info(f"Try to register pre. pre={pre}")
            market = ms.get(pre.market)
            if not market:
                log().info(f"Skip. Market is not supported. ")
                continue

            if pre.is_completed():
                log().info(f"Skip. Already completed.")
                continue

            success = market.register(pre)
            if not success:
                log().error(f"Failed to register a pre.")
                continue

            pre.complete()
            time.sleep(0.1)
            if not pre.is_completed():
                raise Exception(f"Clicked But Not Completed.")

            log().info(f"Registered.")

    if settings_enable_bids:
        log().info("Start bid market business.")
        bids = dp.get_bid_data()
        for bid in bids:
            log().info(f"Try to register bid. bid={bid}")
            market = ms.get(bid.market)
            if not market:
                log().info(f"Skip. Market is not supported.")
                continue

            if bid.is_completed():
                log().info(f"Skip. Already completed.")
                continue

            if not bid.is_ready:
                log().info(f"Skip. Not ready.")
                continue

            success, message = market.participate(bid)

            if not success:
                log().warning(f"Failed to register. message={message}")
                continue

            bid.complete()
            log().info(f"Registered.")


if __name__ == "__main__":
    # logger setup
    logger_init(basedir=iaa_get_config_directory())

    try:
        main()
    except Exception as e: 
        traceback.print_exception(*sys.exc_info())
        log().error(e)
