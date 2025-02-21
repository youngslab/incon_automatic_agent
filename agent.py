
import argparse
from datetime import datetime
import sys
import os
import time
import traceback
import logging
import account

from dotenv import load_dotenv

# fmt: off
load_dotenv()
pythonpath = os.getenv("PYTHONPATH")
if pythonpath:
    absolute_paths = [os.path.abspath(path) for path in pythonpath.split(os.pathsep)]
    sys.path.extend(absolute_paths)

from org.markets import create_market
from org.incon import InconMRO
from utils.logger import setup_agent_logger, flush_file_handler
from utils import edge
from utils.reporter_slack import SlackReporter, report
from utils.table import to_agent_table
from account import account_get
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
    table = to_agent_table(bids, ["is_completed", "market", "number", "price", "title"])
    log().info(f'\n{table}')


def print_pres_summary(pres):
    log().info(" --------------- ")
    log().info(" - Pres Summary ")
    log().info(" --------------- ")
    table = to_agent_table(pres, [ "is_completed", "market", "number", "title"])
    log().info(f"\n{table}")



# Factory function for getting a single instance of SlackReporter
_reporter_instance = None

def get_reporter() -> SlackReporter:
    """
    Factory function to get a single instance of SlackReporter.

    :param slack_token: The Slack API token.
    :param channel: The Slack channel name.
    :return: A single instance of SlackReporter.
    """
    global _reporter_instance
    if _reporter_instance is None:
        # report to slack channel
        token=account.account_get("slack", "token")
        channel=account.account_get("slack", "channel")
        _reporter_instance = SlackReporter(token, channel)
    return _reporter_instance




def main(target_markets):   
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


    # 직접이행 지원
    #  - market name 을 변경 
    enable_direct_excecution = True
    if enable_direct_excecution:
        def uniform_market_name(items):
            for item in items:
                item.market = item.market.replace("(직접이행)", "")
        uniform_market_name(pres)
        uniform_market_name(bids)

    markets = []
    markets = [bid.market for bid in bids] + \
        [pre.market for pre in pres]
    markets = set(markets)
    # filter for user specific markets
    if len(target_markets) != 0:
        markets = [ market for market in markets if market in target_markets ]
    # filter for supported markets
    markets = [create_market(market)
                for market in markets if market not in _market_filter]

    markets = [market for market in markets if market is not None]

    count_pre = 0
    count_bid = 0


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
            count_pre = count_pre + 1

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
            count_bid = count_bid + 1

        log().info(f"Finish to process. market={market.name}")
        market.finish()

    reporter = get_reporter()
    result = f"pre: {count_pre}/{len(pres)}, bid: {count_bid}/{len(bids)}"
    reporter.send_message(result)
    log().info(result)
    
    # update the lastest states
    bids = dp.get_bid_data()
    reporter.send_message(f'```{to_agent_table(bids, ["is_completed", "market", "number", "price", "title"])}```')

if __name__ == "__main__":
    # For debugging porpuse, Stop before finishing 
    parser = argparse.ArgumentParser(description="Debug option example")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    parser.add_argument("--markets", nargs="+", help="List of markets", default=[])
    args = parser.parse_args()

    # setup reporter
    get_reporter().send_message(f"Incon agent start now. From {os.getlogin()}")

    # setup loggers
    loggers = ["Agent", "G2B", "Incon", "D2b", "Kepco", "Automatic"]
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
    log_path = os.path.join('~', '.iaa', 'log', f"incon_agent_{current_time}.log")
    log_path = os.path.expanduser(log_path)
    setup_agent_logger(loggers, log_path)

    try:
        main(args.markets)
    except Exception as e:
        exc_info = sys.exc_info()
        if exc_info[0] is not None:
            exception_str = ''.join(traceback.format_exception(*exc_info))
            log().error(f"An exception occurred:\n {exception_str}", )
        log().error(e)

        # flush logger
        flush_file_handler(loggers)
        print(f"wait {log_path}")
        while not os.path.exists(log_path):
            time.sleep(1)
        get_reporter().send_file(log_path, title="log file", initial_comment="Check this file.")

        if args.debug:
            input("Press any keys to finish.")
