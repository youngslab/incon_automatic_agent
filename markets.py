
# example of returning a variable from a process using a value
# from asyncore import ExitNow
from multiprocessing import Process, Pipe
from typing import List
from enum import Enum
from org.d2b import D2B
from org.kepco import Kepco
from org.g2b.g2b import G2B

from account import account_get
import logging
from logger import logger_init


def log():
    return logging.getLogger("markets")


class Commands(Enum):
    EXIT = 0
    LOGIN = 1
    REGISTER = 2
    PARTICIPATE = 3


class Request:
    def __init__(self, command: int, params: List = []):
        self.command = command
        self.params = params

    def __str__(self):
        return f"request: command={self.command}, params={self.params}"


class Response:
    def __init__(self, result: int, reason: str):
        self.result = result
        self.reason = reason

    def __str__(self):
        return f"response: result={self.result}, reason={self.reason}"


class Success(Response):
    def __init__(self):
        self.result = True
        self.reason = ""


class Fail(Response):
    def __init__(self, reason: str):
        self.result = False
        self.reason = reason


class Server:
    def __init__(self, market, conn):
        self.market = market
        self.conn = conn

    def run(self):

        while (1):
            if not self.conn.poll(10):
                continue

            req: Request = self.conn.recv()
            res: Response = None
            log().debug(f"server) request={req}")
            if req.command == Commands.EXIT:
                break

            elif req.command == Commands.LOGIN:
                if self.market.login():
                    res = Success()
                else:
                    res = Fail("Can not login")
            elif req.command == Commands.REGISTER:
                if self.market.register(*req.params):
                    res = Success()
                else:
                    res = Fail("Can not register")
            elif req.command == Commands.PARTICIPATE:
                if self.market.participate(*req.params):
                    res = Success()
                else:
                    res = Fail("Can not participate")
            else:
                res = Fail(f"Unkown command")

            log().debug(f"server) response={res}")
            self.conn.send(res)

        self.conn.send(Success())
        self.conn.close()


class MarketType(Enum):
    D2B = "국방전자조달"
    KEPCO = "한국전력"
    G2B = "나라장터"


class Proxy:
    def start_server(conn, market):
        # 다른 프로세스의 entry point이기 때문에 별도의 logger init이 필요하다.
        logger_init()
        log().info(f"Start a server. market={market.value}]")
        market = MarketFactory.create(market)
        server = Server(market, conn)
        server.run()

    def __init__(self, market: MarketType):
        log().info(f"Create a market={market.value}")
        self.market = market
        self.name = market.value
        parent_conn, child_conn = Pipe()
        self.conn = parent_conn
        self.child = Process(target=Proxy.start_server, args=(
            child_conn, market))
        self.child.start()

    def login(self, *, timeout=120):
        log().info(f"Login. market={self.name}")
        self.conn.send(Request(Commands.LOGIN))
        if self.conn.poll(timeout=timeout):
            res: Response = self.conn.recv()
            if not res.result:
                log().error(f"Failed to login. reason={res.reason}")
            return res.result
        else:
            log().error("Failed to login. reason=timeout.")
            return False

    def participate(self, bid, *, timeout=120):
        log().info(f"Participate. market={self.name}, bid={bid}")
        self.conn.send(Request(Commands.PARTICIPATE,
                       [bid.number, str(bid.price)]))
        if self.conn.poll(timeout=timeout):
            res: Response = self.conn.recv()
            if not res.result:
                log().error(f"Failed to participate. reason={res.reason}")
            return res.result
        else:
            log().error("Failed to participate. reason=timeout.")
            return False

    def register(self, prebid, *, timeout=60):
        log().info(f"Register. market={self.name}, pre={prebid}")
        self.conn.send(Request(Commands.REGISTER,
                       [prebid.number]))
        if self.conn.poll(timeout=timeout):
            res: Response = self.conn.recv()
            if not res.result:
                log().error(f"Failed to register. reason={res.reason}")
            return res.result
        else:
            log().error("Failed to register. reason=timeout.")
            return False

    def finish(self, timeout=60):
        log().info(f"Finish. market={self.name}")
        self.conn.send(Request(Commands.EXIT))
        if self.conn.poll(timeout=timeout):
            res: Response = self.conn.recv()
            return res.result
        else:
            return False


class MarketFactory:
    def create(market):
        if market == MarketType.D2B:
            d2b_id = account_get("d2b", "id")
            d2b_pw = account_get("d2b", "pw")
            d2b_user = account_get("d2b", "user")
            d2b_cert = account_get("d2b", "cert")
            return D2B(d2b_id, d2b_pw, d2b_user, d2b_cert, headless=False)
        elif market == MarketType.KEPCO:
            kepco_id = account_get("kepco", "id")
            kepco_pw = account_get("kepco", "pw")
            # login to support
            return Kepco(kepco_id, kepco_pw)
        elif market == MarketType.G2B:
            return G2B(headless=False)


def create_market(market_name):
    try:
        market_type = MarketType(market_name)
        return Proxy(market_type)
    except:
        return None
