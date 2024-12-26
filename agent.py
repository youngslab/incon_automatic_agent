
import argparse
from hmac import new
from operator import is_
import sys
import os
import traceback
import logging
from turtle import title

from attrs import field
from pandas import to_numeric
from account import account_get
from utils import edge
from utils.reporter_slack import report
from utils.table import to_agent_table


# fmt: off
module_directory = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    "thirdparty", "automatic")
if module_directory not in sys.path:
    sys.path.append(module_directory)

from automatic.utils.logger import Logger
from org.markets import create_market
from org.incon import InconMRO

# fmt: on)

_market_filter = [
    # '국방전자조달',
    # '한국전력',
    # '나라장터',
    # '나라장터(직접이행)',
]

def create_data_provider():
    # create incon object
    driver = edge.create_driver()
    id = account_get("incon", "id")
    pw = account_get("incon", "pw")
    return InconMRO(driver, id, pw)


def log():
    return logging.getLogger("Agent")

def print_bids_summary(bids):
    log().info(" --------------- ")
    log().info(" - Bids Summary ")
    log().info(" --------------- ")
    print(to_agent_table(bids, ["is_completed", "market", "number", "price", "title"]))


def print_pres_summary(pres):
    log().info(" --------------- ")
    log().info(" - Pres Summary ")
    log().info(" --------------- ")
    table = to_agent_table(pres, [ "is_completed", "market", "number", "title"])
    print(table)


def main():

    # automatic debugging log
    import automatic.utils
    import logging
    automatic.utils.Logger.init(automatic.utils.LOGGER_AUTOMATIC, logging.DEBUG)
    
    dp = create_data_provider()
    dp.login()

    dp.init_pre()
    pres = dp.get_pre_data()
    pres = sorted(pres, key=lambda pre: pre.market)
    print_pres_summary(pres)
    pres = [pre for pre in pres if not pre.is_completed]

    dp.init_bid()
    bids = dp.get_bid_data()
    bids = sorted(bids, key=lambda bid: bid.market)
    print_bids_summary(bids)
    bids = [bid for bid in bids if not bid.is_completed]


    # market name 을 변경 
    enable_direct_excecution = True
    if enable_direct_excecution:
        def uniform_market_name(items):
            for item in items:
                item.market = item.market.replace("(직접이행)", "")
        uniform_market_name(pres)
        uniform_market_name(bids)

    markets = []
    # explicit market from user input
    if len(sys.argv) == 2:
        market = sys.argv[1]
        print(f"Create a market \"{market}\" explicitly.")
        markets = [create_market(market)]
    else:
        # markets(asynchronously)
        markets = [bid.market for bid in bids] + \
            [pre.market for pre in pres]
        markets = set(markets)
        print("markets")
        print(markets)



        markets = [create_market(market)
                   for market in markets if market not in _market_filter]

    markets = [market for market in markets if market is not None]

    for market in markets:
        # filter not supported markets
        if not market:
            continue

        log().info(f"--------------------------------------------")
        log().info(f"Start to process for a market({market.name})")

        # login first
        if not market.login():
            log().warning(f"Failed to login to {market.name}")
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

    bids = dp.get_bid_data()
    # report to slack channel
    import account
    token=account.account_get("slack", "token")
    channel=account.account_get("slack", "channel")
    report(token, channel, f"From {os.getlogin()}")
    report(token, channel, f'```{to_agent_table(bids, ["is_completed", "market", "number", "price", "title"])}```')
    
    

if __name__ == "__main__":

    Logger.init("Agent", logging.DEBUG)

    try:
        main()
    except Exception as e:
        traceback.print_exception(*sys.exc_info())
        log().error(e)

        # For debugging porpuse, Stop before finishing 
        parser = argparse.ArgumentParser(description="Debug option example")
        parser.add_argument('--debug', action='store_true', help="Enable debug mode")
        args = parser.parse_args()
        debug = args.debug
        if args.debug:
            input("Press any keys to finish.")
