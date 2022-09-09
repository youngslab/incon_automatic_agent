
# example of returning a variable from a process using a value
# from asyncore import ExitNow
from multiprocessing import Process, Pipe
from random import random
from time import sleep
from multiprocessing import Array
from multiprocessing import Process
from venv import create

# function to execute in a child process
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from enum import Enum
from typing import Tuple, Union, List

import os

from org.d2b import D2B
from org.kepco import Kepco
from org.g2b.g2b import G2B
from org.g2b.g2b import SafeG2B

from account import account_get


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

        while(1):
            if not self.conn.poll(10):
                continue

            req: Request = self.conn.recv()

            if req.command == Commands.EXIT:
                self.conn.send(Success())
                return
            elif req.command == Commands.LOGIN:
                if self.market.login():
                    self.conn.send(Success())
                else:
                    self.conn.send(Fail("Can not log in"))
            elif req.command == Commands.REGISTER:
                if self.market.register(*req.params):
                    self.conn.send(Success())
                else:
                    self.conn.send(Fail("Can not register"))
            elif req.command == Commands.PARTICIPATE:
                if self.market.participate(*req.params):
                    self.conn.send(Success())
                else:
                    self.conn.send(Fail("Can not participate"))
            else:
                self.conn.send(Fail(f"Unkown command."))

        self.conn.close()


class MarketType(Enum):
    D2B = "국방전자조달"
    KEPCO = "한국전력"
    G2B = "나라장터"
    SAFEG2B = "나라장터(안전입찰)"


class Proxy:

    def start_server(conn, market):
        print(f"[{market}] PROXY::task")
        market = MarketFactory.create(market)
        server = Server(market, conn)
        server.run()

    def __init__(self, market: MarketType):
        print(f"[{market}] PROXY::init")
        self.market = market
        self.name = market.value
        parent_conn, child_conn = Pipe()
        self.conn = parent_conn
        self.child = Process(target=Proxy.start_server, args=(
            child_conn, market))
        self.child.start()

    def login(self, timeout=60):
        print(f"[{self.market}] PROXY::login")
        self.conn.send(Request(Commands.LOGIN))
        if self.conn.poll(timeout=timeout):
            res: Response = self.conn.recv()
            print(f"res={res}")
            if not res.result:
                print(f"Failed. reason={res.reason}")
            return res.result
        else:
            print("Failed. timeout.")
            return False

    def participate(self, bid, *, timeout=60):
        print(f"[{self.market}] PROXY::participate")
        self.conn.send(Request(Commands.PARTICIPATE,
                       [bid.number, str(bid.price)]))
        if self.conn.poll(timeout=timeout):
            res: Response = self.conn.recv()
            print(f"res={res}")
            if not res.result:
                print(f"Failed. reason={res.reason}")
            return res.result
        else:
            print("Failed. timeout.")
            return False

    def register(self, prebid, *, timeout=60):
        print(f"[{self.market}] PROXY::participate")
        self.conn.send(Request(Commands.REGISTER,
                       [prebid.number]))
        if self.conn.poll(timeout=timeout):
            res: Response = self.conn.recv()
            print(f"res={res}")
            if not res.result:
                print(f"Failed. reason={res.reason}")
            return res.result
        else:
            print("Failed. timeout.")
            return False

    def finish(self, timeout=60):
        print(f"[{self.market}] PROXY::finish")
        self.conn.send(Request(Commands.EXIT))
        if self.conn.poll(timeout=timeout):
            res: Response = self.conn.recv()
            print(f"res={res}")
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
            pw = account_get("g2b", "pw")
            return G2B(pw, headless=False)
        elif market == MarketType.SAFEG2B:
            return SafeG2B()


def create_market(market_name):
    try:
        market_type = MarketType(market_name)
        return Proxy(market_type)
    except:
        return None
