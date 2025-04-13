# WebDriver Manager (selenium 4)
# https://pypi.org/project/webdriver-manager/#use-with-edge
from selenium  import webdriver
from enum import Enum
from org.d2b import D2B
from org.kepco import Kepco
from org.g2b.g2b_new_gen import G2B_new_gen
from selenium.webdriver.remote.webdriver import WebDriver

from account import account_get
import logging

from utils import edge

def log():
    return logging.getLogger("Agent")


def to_code(market_title: str):
    if market_title == "국방전자조달":
        return "d2b"
    elif market_title == "나라장터":
        return "g2b"
    elif market_title == "한국전력":
        return "kepco"
    elif market_title == "가스공사":
        return "kogas"
    else:
        return "unknown"


class MarketType(Enum):
    D2B = "국방전자조달"
    KEPCO = "한국전력"
    G2B = "나라장터"
    KOGAS = "가스공사"
    Unknown = "unknown"


class MarketFactory:
    @staticmethod
    def create(drv: WebDriver, market):
        try:
            market = MarketType(market)
        except ValueError:
            log().error(f"Unknown market: {market}")
            market = MarketType.Unknown

        if market == MarketType.G2B:
            g2b_pw = account_get("g2b", "pw")
            g2b_id = account_get("g2b", "id")
            # 공동인증서(기업)
            public_cert = account_get("g2b", "public_cert")
            # 금융인증서서
            financial_cert = account_get("g2b", "financial_cert")
            return G2B_new_gen(drv, g2b_pw, g2b_id, public_cert, financial_cert)

        if market == MarketType.D2B:
            d2b_id = account_get("d2b", "id")
            d2b_pw = account_get("d2b", "pw")
            d2b_cert = account_get("d2b", "cert")
            return D2B(drv, d2b_id, d2b_pw, d2b_cert)
        
        elif market == MarketType.KEPCO:
            kepco_id = account_get("kepco", "id")
            kepco_pw = account_get("kepco", "pw")
            kepco_cert = account_get("kepco", "cert")
            return Kepco(drv, kepco_id, kepco_pw, kepco_cert)

        return None
