
import sys
import time
import os
import traceback
from org.incon import Incon
from org.g2b.g2b import G2B
from org.g2b.g2b import SafeG2B
from org.kepco import Kepco
from org.d2b import D2B

import logging
from account import account_get
from logger import logger_init


settings_enable_pres = True
settings_enable_bids = True

__pre_markets = dict()

# To skip some market
_market_filter = ['한국전력', '나라장터']
# _market_filter = ['나라장터']
# _market_filter = ['나라장터', '국방전자조달']
# _market_filter = []


def create_data_provider():
    # create incon object
    id = account_get("incon", "id")
    pw = account_get("incon", "pw")
    return Incon(id, pw)


def create_pre_market(market: str):
    if market in _market_filter:
        return None

    if market == "나라장터":
        pw = account_get("g2b", "pw")
        return G2B(pw, headless=False)
    elif market == "한국전력":
        kepco_id = account_get("kepco", "id")
        kepco_pw = account_get("kepco", "pw")
        # login to support
        return Kepco(kepco_id, kepco_pw)
    elif market == "국방전자조달":
        d2b_id = account_get("d2b", "id")
        d2b_pw = account_get("d2b", "pw")
        d2b_user = account_get("d2b", "user")
        d2b_cert = account_get("d2b", "cert")
        return D2B(d2b_id, d2b_pw, d2b_user, d2b_cert, headless=False)
    else:
        return None


def get_pre_market(market: str):
    res = __pre_markets.get(market)
    if res:
        return res
    else:
        obj = create_pre_market(market)
        __pre_markets[market] = obj
        return obj


__markets = dict()


def get_bid_market(market: str):

    if market in _market_filter:
        return None

    res = __markets.get(market)
    if res:
        return res
    else:
        obj = create_bid_market(market)
        __markets[market] = obj
        return obj


def create_bid_market(market: str):
    if market in _market_filter:
        return None
    if market == "나라장터":
        return SafeG2B()
    else:
        return get_pre_market(market)


def iaa_get_config_directory():
    dir = os.path.join(os.path.expanduser('~'), ".iaa")
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir


def log():
    return logging.getLogger(__name__)


def main():
    dp = create_data_provider()

    pres = dp.get_pre_data()
    for pre in pres:
        if not pre.is_completed():
            _ = get_pre_market(pre.market)

    # create markets in advance.
    bids = dp.get_bid_data()
    for bid in bids:
        if not bid.is_completed() and bid.is_ready:
            _ = get_bid_market(bid.market)

    if settings_enable_pres:
        log().info("Start pre market business.")
        pres = dp.get_pre_data()

        for pre in pres:
            log().info(f"Try to register pre. pre={pre}")

            if pre.is_completed():
                log().info(f"Skip. Already completed.")
                continue

            market = get_pre_market(pre.market)
            if not market:
                log().info(f"Skip. Market is not supported. ")
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

            log().info(f"Register a bid. bid={bid}")

            if bid.is_completed():
                log().info(f"Skip. Already completed.")
                continue

            if not bid.is_ready:
                log().info(f"Skip. Not ready.")
                continue

            market = get_bid_market(bid.market)
            if not market:
                log().info(f"Skip. Market is not supported.")
                continue

            success = market.participate(bid)

            if not success:
                log().warning(f"Failed to register.")
                continue

            bid.complete()
            log().info(f"Registered.")


if __name__ == "__main__":
    # logger setup
    # logger_init(basedir=iaa_get_config_directory())
    logger_init()

    try:
        main()
    except Exception as e:
        traceback.print_exception(*sys.exc_info())
        log().error(e)
        input("Press any keys to finish.")
