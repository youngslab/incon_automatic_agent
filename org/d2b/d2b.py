

import os
import time
import logging


from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By


from auto import *


def log():
    return logging.getLogger(__package__)


def d2b_create_driver(headless=False):
    options = webdriver.EdgeOptions()
    options.add_argument('log-level=3')
    if headless:
        options.add_argument('headless')
        options.add_argument('disable-gpu')

    # add extension
    # SecuKit NX(edge://extensions/?id=hghadmnjlclmajeenogjjjefdecofpag)
    # extension_path = os.path.join(os.path.expanduser(
    #     '~'), ".iaa", 'secukit_nx_1.0.1.12_0.crx')
    # options.add_extension(extension_path)

    service = Service(EdgeChromiumDriverManager().install())
    return webdriver.Edge(options=options, service=service)


def d2b_cert_login(driver: WebDriver, user, cert_pw):
    # Certificate
    # 1. HDD선택
    auto_click(driver, By.ID, "NX_MEDIA_HDD")

    # 2. 사업자 인증서 선택
    auto_click(driver, By.XPATH,
               f'//*[@id="NXcertList"]/tr/td[2]/div[text()="{user}"]')

    # XXX: 인증서 선택과정이 아래 type의 결과를 reset한다.
    #      따라서 충분한 간격을 준다.
    time.sleep(3)

    # 3. password
    auto_type(driver, By.ID, "certPwd", cert_pw)

    # 4. ok button
    auto_click(driver, By.XPATH, '//*[@id="nx-cert-select"]/div[4]/button[1]')


def d2b_login(driver: WebDriver, user, id, pw, cert):
    auto_click(driver, By.ID, "_mLogin")
    # login form page로 이동
    auto_type(driver, By.ID, "_id", id)
    auto_type(driver, By.ID, "_pw", pw)
    auto_click(driver, By.ID, "_loginBtn")

    # Certificate
    d2b_cert_login(driver, user, cert)

    # XXX: certificates 로그인 후 바로 다른 페이지로 이동하면 로그인 되지 않는다.
    #      따라서 충분한 시간을 준다.
    time.sleep(3)


def d2b_register(driver: WebDriver, number, user, cert_pw):
    # move to the page to register
    driver.get('https://www.d2b.go.kr/index.do')
    # type number and click search button
    auto_type(driver, By.ID, "numb_divs", number)
    auto_click(driver, By.ID, 'btn_search')

    # 검색된 결과 중 첫번째 element를 선택한다.
    notice = auto_find_element(
        driver, By.XPATH, '//*[@id="SBHE_DATAGRID_WHOLE_TBODY_datagrid1"]/tr[2]/td[8]/div/span/a')
    log().info(
        f"Found notice from number. notice={notice.text}, number={number}")
    # auto_click(driver, notice) -> 안됨...
    notice.click()

    # 입찰참가신청서 작성
    auto_click(driver, By.ID, 'btn_join')

    # 신청서 작성후 popup이 생성 된다면.. 이미 신청이 된 상태이다.
    alert = auto_find_alert(driver, timeout=3)
    if alert:
        log().info(f"Already registered. text={alert.text}")
        alert.accept()
        return True

    # 서약서 작성
    auto_click(driver, By.ID, 'c_box1')
    auto_click(driver, By.ID, 'c_box2')
    auto_click(driver, By.ID, 'subcont_dir_pay_yn1')
    # XXX: Need to wait the above result?
    # time.sleep(3)
    auto_click(driver, By.ID, 'btn_confirm')

    # 보증금납부 방법
    sel = Select(auto_find_element(driver, By.ID, 'grnt_mthd'))
    sel.select_by_visible_text('보증금면제')

    # 보증금납부에 대한 서약서 확인
    auto_click(driver, By.ID, 'c_box2')
    auto_click(driver, By.ID, 'c_box3')
    auto_click(driver, By.XPATH,
               '//*[@id="layer"]/div[2]/div/div/div[3]/button[1]')

    # 약관 동의 체크
    auto_click(driver, By.ID, 'bidAttention_check')

    # 신청 버튼
    auto_click(driver, By.ID, 'btn_wrt')
    alert = auto_find_alert(driver)
    log().info(f"Accept alert! text={alert.text}")
    alert.accept()

    # 인증서 로그인
    d2b_cert_login(driver, user, cert_pw)

    # 팝업 확인
    alert = auto_find_alert(driver)
    log().info(f"Accept alert! text={alert.text}")
    alert.accept()

    return True


class D2B:
    def __init__(self, id, pw, user, cert_pw, *, headless=True):
        log().debug("__init__")

        self.__user = user
        self.__cert_pw = cert_pw

        self.driver = d2b_create_driver(headless=headless)

        # go homepage
        self.driver.get("https://www.d2b.go.kr/index.do")

        d2b_login(self.driver, user, id, pw, cert_pw)

    def register(self, pre):
        return d2b_register(self.driver,  pre.number, self.__user, self.__cert_pw)

    def participate(self, bid):
        return False, "D2B Not implemented yet"


if __name__ == "__main__":
    import account
    import logger
    logger.logger_init()

    driver = d2b_create_driver()
    driver.get("https://www.d2b.go.kr/index.do")

    user = "에이알(AR)"
    cert = account.account_get("d2b", "cert")
    pw = account.account_get("d2b", "pw")
    id = account.account_get("d2b", "id")

    d2b_login(driver, user, id, pw, cert)

    number = "2022SCF025417670-01"
    print(d2b_register(driver, number, user, cert))
