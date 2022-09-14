
import sys
import traceback
import logging
from logger import logger_init

from account import account_get
from org.incon import Incon
from markets import create_market

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
    return logging.getLogger()


def print_bids_summary(bids):
    log().info(" - Bids Summary ")
    for bid in bids:
        check = 'v' if bid.is_completed() else ' '
        print(f"    [{check}] {bid}")
    log().info(" --------------- ")


def print_pres_summary(pres):
    log().info(" - Pres Summary ")
    for pre in pres:
        check = 'v' if pre.is_completed() else ' '
        print(f"    [{check}] {pre}")
    log().info(" --------------- ")


def main():

    dp = create_data_provider()

    pres = dp.get_pre_data()
    pres = sorted(pres, key=lambda pre: pre.market)
    print_pres_summary(pres)
    pres = [pre for pre in pres if not pre.is_completed()]

    bids = dp.get_bid_data()
    bids = sorted(bids, key=lambda bid: bid.market)
    print_bids_summary(bids)
    bids = [bid for bid in bids if bid.is_ready and not bid.is_completed()]

    # markets(asynchronously)
    markets = [bid.market for bid in bids] + \
        [pre.market for pre in pres]
    markets = set(markets)
    markets = [create_market(market)
               for market in markets if market not in _market_filter]

    # market reorder
    markets.sort(key=lambda x: x == "나라장터(안전입찰)")

    for market in markets:

        # filter not supported markets
        if not market:
            continue

        log().info(f"--------------------------------------------")
        log().info(f"Start to process for a market({market.name})")

        # login first
        if not market.login():
            log().warn(f"Failed to login to {market.name}")
            continue

        # register prebid
        for pre in pres:
            if pre.market != market.name:
                continue

            log().info(f"Registered. pre={pre}")
            if not market.register(pre):
                log().warning(f"Failed to register. pre={pre}")
                continue

            log().info(f"Successfully registered. pre={pre}")
            pre.complete()

        # register bid
        for bid in bids:
            if bid.market != market.name:
                continue

            log().info(f"Participated. bid={bid}")
            if not market.participate(bid):
                log().warning(f"Failed to participate. bid={bid}")
                continue

            log().info(f"Successfully participated. bid={bid}")
            bid.complete()

        log().info(f"Finish to process. market={market.name}")
        market.finish()


if __name__ == "__main__":
    logger_init()

    try:
        main()
    except Exception as e:
        traceback.print_exception(*sys.exc_info())
        log().error(e)
        input("Press any keys to finish.")
