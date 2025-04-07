
import argparse
from datetime import datetime
import sys
import os
import time
import traceback
import logging
import account
from selenium.common.exceptions import WebDriverException


from dotenv import load_dotenv

LOGGER_AGENT = "Agent"
logger = logging.getLogger(LOGGER_AGENT)

# fmt: off
load_dotenv()
pythonpath = os.getenv("PYTHONPATH")
if pythonpath:
    absolute_paths = [os.path.abspath(path) for path in pythonpath.split(os.pathsep)]
    sys.path.extend(absolute_paths)

from automatic.common.exceptions import ElementNotFoundException
import org.d2b
import org.kepco
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

def print_bids_summary(bids):
    logger.info(" --------------- ")
    logger.info(" - Bids Summary ")
    logger.info(" --------------- ")
    table = to_agent_table(bids, ["is_completed", "market", "number", "price", "title"])
    logger.info(f'\n{table}')


def print_pres_summary(pres):
    logger.info(" --------------- ")
    logger.info(" - Pres Summary ")
    logger.info(" --------------- ")
    table = to_agent_table(pres, [ "is_completed", "market", "number", "title"])
    logger.info(f"\n{table}")



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


def is_driver_alive(driver):
    if driver is None:
        return False
    try:
        driver.execute_script("return 1;")
        return True
    except WebDriverException:
        return False



def main(target_markets):   
    dp = create_data_provider()
    dp.login()

    dp.init_pre()
    pres = dp.get_pre_data()
    pres = sorted(pres, key=lambda pre: pre.market)
    print_pres_summary(pres)
    # pres = [pre for pre in pres if not pre.is_completed]

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

        logger.info(f"--------------------------------------------")
        logger.info(f"Start to process for a market({market.name})")

        # login first
        if not market.login():
            logger.warning(f"Failed to login to {market.name}")
            continue


        # register prebid
        for pre in pres:
            if pre.market != market.name:
                continue
            logger.info(f"--------------------------------------------")
            logger.info(f"Try to register. pre={pre}")
            if not market.register(pre):
                logger.warning(f"Failed to register. pre={pre}")
                logger.info(f"--------------------------------------------")
                continue

            pre.complete()
            count_pre = count_pre + 1
            logger.info(f"Successfully registered. pre={pre}")
            logger.info(f"--------------------------------------------")

        # register bid
        for bid in bids:
            if bid.market != market.name:
                continue

            logger.info(f"--------------------------------------------")
            logger.info(f"Try to participate. bid={bid}")
            if not market.participate(bid):
                logger.warning(f"Failed to participate. bid={bid}")
                logger.info(f"--------------------------------------------")
                continue
            
            bid.complete()
            count_bid = count_bid + 1
            logger.info(f"Successfully participated. bid={bid}")
            logger.info(f"--------------------------------------------")

        logger.info(f"Finish to process. market={market.name}")
        market.finish()

    reporter = get_reporter()
    result = f"pre: {count_pre}/{len(pres)}, bid: {count_bid}/{len(bids)}"
    reporter.send_message(result)
    logger.info(result)
    
    # update the lastest states
    bids = dp.get_bid_data()
    reporter.send_message(f'```{to_agent_table(bids, ["is_completed", "market", "number", "price", "title"])}```')


def handle_exception(e, *, driver=None, debug=False):
    # 예외 상세 로그
    exc_info = sys.exc_info()
    if exc_info[0] is not None:
        exception_str = ''.join(traceback.format_exception(*exc_info))
        logger.error(f"An exception occurred:\n{exception_str}")
    logger.error(e)

    # 스크린샷 전송 (있을 경우)
    if is_driver_alive(driver):
        try:
            screenshot_path = os.path.join(os.path.expanduser('~'), '.iaa', 'log', "error_screenshot.png")
            if driver.save_screenshot(screenshot_path):
                logger.info(f"Screenshot saved to {screenshot_path}")
                get_reporter().send_file(screenshot_path, title="Screenshot", initial_comment="Check this screen.")
            else:
                logger.error(f"Failed to save screenshot.")
        except Exception as screenshot_error:
            logger.error(f"Failed to capture screenshot: {screenshot_error}")
    else:
        logger.error(f"Driver is not valid to save screenshot")

    # 로그 파일 전송
    flush_file_handler(loggers)
    logger.info("Waiting for log file to be flushed...")
    while not os.path.exists(log_path):
        time.sleep(1)
    get_reporter().send_file(log_path, title="Log File", initial_comment="Check this file.")

    # 디버깅 대기
    if debug:
        input("Press any key to finish.")

if __name__ == "__main__":
    # For debugging porpuse, Stop before finishing 
    parser = argparse.ArgumentParser(description="Debug option example")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    parser.add_argument("--markets", nargs="+", help="List of markets", default=[])
    args = parser.parse_args()

    # setup reporter
    get_reporter().send_message(f"Incon agent start now. From {os.getlogin()}")

    # setup loggers
    import org, automatic
    
    loggers = [LOGGER_AGENT, 
               org.incon.LOGGER_INCON,
               org.g2b.LOGGER_G2B, 
               org.d2b.LOGGER_D2B,
               org.kepco.LOGGER_KEPCO, 
               automatic.automatic.LOGGER_AUTOMATIC]
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
    log_path = os.path.join('~', '.iaa', 'log', f"incon_agent_{current_time}.log")
    log_path = os.path.expanduser(log_path)
    setup_agent_logger(loggers, log_path)

    logger.info(f"Argument: markets={args.markets}, debug={args.debug}")

    try:
        main(args.markets)
    except ElementNotFoundException as e:
        handle_exception(e, driver=e.driver)

    except Exception as e:
        handle_exception(e)