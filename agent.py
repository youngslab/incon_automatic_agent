
import sys
import time
import os
import traceback
from org.incon import Incon

import logging
from account import account_get
from logger import logger_init

from market_factory import create_market

_market_filter = [
    # '국방전자조달',
    # '한국전력',
    # '나라장터'
]


def create_data_provider():
    # create incon object
    id = account_get("incon", "id")
    pw = account_get("incon", "pw")
    return Incon(id, pw)


def log():
    return logging.getLogger(__name__)


def main():
    dp = create_data_provider()

    pres = dp.get_pre_data()
    pres = sorted(pres, key=lambda pre: pre.market)
    pres = [pre for pre in pres if not pre.is_completed()]

    bids = dp.get_bid_data()
    bids = sorted(bids, key=lambda bid: bid.market)
    bids = [bid for bid in bids if bid.is_ready and not bid.is_completed()]

    # markets
    markets = [bid.market for bid in bids] + \
        [pre.market for pre in pres]
    markets = set(markets)
    markets = [create_market(market)
               for market in markets if market not in _market_filter]

    for market in markets:

        # filter not supported markets
        if not market:
            continue

        # login first
        market.login()

        # register prebid
        for pre in pres:
            if pre.market != market.name:
                continue

            if not market.register(pre):
                log().warning(f"Failed to register. pre={pre}")
                continue

            log().info(f"Successfully registered. pre={pre}")
            pre.complete()

        # register bid
        for bid in bids:
            if bid.market != market.name:
                continue

            if not market.participate(bid):
                log().warning(f"Failed to participate. bid={bid}")
                continue

            log().info(f"Successfully participated. bid={bid}")
            bid.complete()

        market.finish()


if __name__ == "__main__":
    logger_init()

    try:
        main()
    except Exception as e:
        traceback.print_exception(*sys.exc_info())
        log().error(e)
        input("Press any keys to finish.")
