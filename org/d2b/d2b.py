

import os
import random
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

#################
# VERSION 2
#################

# ID: D2B - 서약서동의(2)


def _agree_oath_2(driver: WebDriver):

    # - 조세포탈 없음을 확약하는 서약서
    if not auto_click(driver, By.ID, 'c_box1'):
        return False

    # - 청렴 계약 이행 서약서
    if not auto_click(driver, By.ID, 'c_box2'):
        return False

    # - 행정정보 공동이용 사전동의서
    if not auto_click(driver, By.ID, 'c_box3'):
        return False

    # 확인 버튼
    if not auto_click(driver, By.ID, 'btn_oath_confirm'):
        return False

    return True


def _go_bid_detail_page(driver: WebDriver, number):
    # move to the page to register
    driver.get('https://www.d2b.go.kr/index.do')
    # type number and click search button
    auto_type(driver, By.ID, "numb_divs", number)
    auto_click(driver, By.ID, 'btn_search')

    # 검색된 결과 중 첫번째 element를 선택한다.
    notice = auto_find_element(
        driver, By.XPATH, '//*[@id="SBHE_DATAGRID_WHOLE_TBODY_datagrid1"]/tr[2]/td[8]/div/span/a')
    if not notice:
        log().error(f"Failed to search bid item. number={number}")
        return False

    log().info(
        f"Found notice from number. notice={notice.text}, number={number}")
    # auto_click(driver, notice) -> 안됨...
    notice.click()
    return True


# ID: D2B - 견적서 작성(w/o 참가신청)
# Precondition: 견적서작성 페이지여야 한다.
def _write_estimate(driver: WebDriver, cost) -> bool:
    # 1. 견적금액 작성
    if not auto_type(driver, By.ID, "input_amount", cost):
        log().error("Failed to find 견적금액 input")
        return False

    # 2. 복수예비가격 선택: 2개
    check_boxes = auto_find_all_elements(
        driver, By.XPATH, '//input[@name="check_multi_price"]')
    check_boxes = random.choices(check_boxes, k=2)
    for box in check_boxes:
        print(box)
        box.click()

    time.sleep(3)

    # 3. 제출 버튼 click
    if not auto_click(driver, By.ID, "btn_submit"):
        log().error("Failed to find 제출 button")
        return False

    # 4. 견적서 제출 확인 popup
    alert = auto_find_alert(driver)
    if not alert:
        log().error("Failed to find 제출 확인 메세지")
        return False

    log().debug(f"Accept. text={alert.text}")
    alert.accept()

    return True


def _need_registration(driver: WebDriver, number) -> bool:
    # 1. 상세 페이지로 이동
    _go_bid_detail_page(driver, number)

    # 2. "견적서작성" vs. "입찰참가신청" 버튼
    # 견적서작성 버튼이 있으면 입찰참가가 필요 없다.
    btn = auto_find_element(
        driver, By.XPATH, '//button[@id="btn_estimate_write"]', timeout=5)
    return True if not btn else False

# ID: D2B - 입찰참가 불필요건에 대한 견적서 작성
# Condition: 입찰건 detail page에서 "견적서작성" 버튼이 있어야 한다.


def _participate_without_registration(driver: WebDriver, number, cost) -> bool:

    # 1. 아이템을 검색한다.
    _go_bid_detail_page(driver, number)

    # 2. 견적서 작성 버튼을 찾는다.
    estimate_write_btn = auto_find_element(
        driver, By.XPATH, '//button[@id="btn_estimate_write"]', timeout=5)
    if not estimate_write_btn:
        log().debug("Failed to find 견적서작성 button.")
        return False
    estimate_write_btn.click()

    # 3. 서약서 작성
    if not _agree_oath_2(driver):
        log().error("Failed to write oath(2).")
        return False

    # check popup ..
    #

    # 4. 견적서 작성
    if not _write_estimate(driver, cost):
        log().error("Failed to write estimate.")
        return False

    # 5. 견적서 제출 확인 - 견적서를 성공적으로 제출하였습니다.
    alert = auto_find_alert(driver)
    alert.accept()

    return True


# ID: D2b - 입찰(참가신청) - 참가가능 검증
# number form example: "MDR0033-1", "UMM0424-1", "UMM0483-1"
def _can_participate(driver, number):
    x = auto_find_element(driver, By.XPATH, '//a[text()="물품"]/../div')
    driver.execute_script(
        "arguments[0].setAttribute('style',arguments[1])", x, "display: block;")

    auto_click(driver, By.XPATH, '//a[text()="입찰"]')
    auto_click(driver, By.XPATH, '//h5/a[text()="참가신청서 조회"]')

    notices = auto_find_all_elements(
        driver, By.XPATH, '//tbody[@id="SBHE_DATAGRID_WHOLE_TBODY_datagrid1"]/tr')
    notices = notices[1:]

    for notice in notices:
        if not notice or notice.find_element(By.XPATH, './/td[2]/div/span').text.find(number) < 0:
            continue

        status = notice.find_element(By.XPATH, './/td[7]/div/span').text
        if status.find("투찰가능") < 0:
            log().error(
                f"Can not participate. number={number}, status={status}")
            return False

        return True

    log().error(f"Can not find notice. number={number}")
    return False

# private


def _write_bid(driver, cost):
    # 1. cost 입력
    auto_type(driver, By.ID, "bid_amnt_1", cost)

    # 2. 추첨 checkbox 선택(2개)
    boxes = auto_find_all_elements(
        driver, By.XPATH, '//td/input[@type="checkbox"]')
    if len(boxes) != 15:
        log().error(f"Can not find all 추첨확인 checkbox.len={len(boxes)}")
        return False
    boxes = random.sample(boxes, 2)
    for box in boxes:
        box.click()

    if not auto_click(driver, By.ID, "c_box"):
        log().error(f"Can not find 동의 checkbox.")
        return False

    return True


def _sumbit_bid(driver):
    if not auto_click(driver, By.ID, "btn_bid_submit"):
        log().error(f"Can not find 제출 버튼.")
        return False

    alert = wait_alert(driver)
    log().info(f"accpet. alert={alert.text}")
    alert.accept()

    alert = wait_alert(driver)
    log().info(f"accpet. alert={alert.text}")
    alert.accept()

    return True

# Precondition:
#  - 입찰서제출 및 조회(경쟁입찰) 페이지 내에서 실행 되어야 한다.
# WARNING: number format is different


def choose_bid_in_list(driver: WebDriver, number):
    # 공고번호 선택
    notices = auto_find_all_elements(
        driver, By.XPATH, '//tbody[@id="SBHE_DATAGRID_WHOLE_TBODY_datagrid1"]/tr')
    notice = next(filter(lambda x: x.find_element(
        By.XPATH, ".//td[1]/div").text.find(number) >= 0, notices[1:]), None)
    if not notice:
        print(f"Can not find the bid. number={number}")
        return False
    notice.click()

    # validate - Selected?
    if notice.find_element(By.XPATH, './/td[1]').get_attribute("sbgrid_select") != "true":
        log().error(f"Can not find the bid. number={number}")
        return False

    # validate - can participate?
    status = notice.find_element(By.XPATH, './/td[6]/div/span').text
    if status != "미제출":
        log().error(
            f"Fail to verify its status. number= {number}, status={status}")
        return False

    return True

# ID: D2b - 입찰(참가신청) - 입찰서 작성 페이지 이동


def _go_to_bid_write_page(driver, number):
    # ID: D2b - 입찰(참가신청) - 입찰서 작성 페이지이동
    # 페이지 이동
    if not auto_click(driver, By.XPATH, '//h5/a[text()="입찰서제출 및 조회(경쟁입찰)"]'):
        log().error(f"Failed to find 입찰서제출 및 조회(경쟁입찰) button")
        return False

    # 페이지내 관련 공고 선택
    if not choose_bid_in_list(driver, number):
        log().error(f"Failed to go to the bid page")
        return False

    # 입찰서 작성 버튼 클릭
    if not auto_click(driver, By.ID, 'btn_bid_regi'):
        log().error(f"Failed to find 입찰서 작성 button")
        return False

    return True


def _participate_with_registration(driver, number, cost):
    # validate it's ready
    # WARNING: number format is different
    # ID: D2b - 입찰(참가신청) - 참가가능 검증
    if not _can_participate(driver, number):
        log().error(
            f"Failed to validate the bid. number={number}, cost={cost}")
        return False

    # ID: D2b - 입찰(참가신청) - 입찰서 작성 페이지 이동
    if not _go_to_bid_write_page(driver, number):
        log().error(f". number={number}, cost={cost}")
        return False

    # ID: D2b - 입찰(참가신청) - 입찰서 작성

    # 입찰서 작성
    if not _write_bid(driver, cost):
        log().error(
            f"Failed to write a bid form. number={number}, cost={cost}")
        return False

    # 입찰서 제출
    if not _sumbit_bid(driver):
        log().error(f"Failed to submit a bid. number={number}, cost={cost}")
        return False

    return True


# INTERFACE

def _login(driver: WebDriver, token='BIO-SEAL') -> bool:
    driver.get("https://www.d2b.go.kr/index.do")

    if _is_login(driver):
        return True

    # login button
    auto_click(driver, By.ID, "_mLogin")

    # 지문인식 로그인 버튼
    # XXX: 너무 빨리 click이 되면 문제가 발생한다.
    #       인증 프로그램 실행 준비가 안되었습니다. 설치가 안된 경우 제품을 설치 후 진행해 주시기 바랍니다
    # TODO: 적절한 수준 찾기
    # 3초: 가끔씩 메세지가 나오는 경우가 있다.
    # 5초로 변경
    fp_login_btn = auto_find_element(driver, By.ID, "_fingerLoginBtn")
    time.sleep(5)
    auto_click(driver, fp_login_btn)

    # alert 창 확인 버튼
    alert = auto_find_alert(driver, timeout=3)
    alert.accept()

    # 지문 토큰
    auto_click(driver, By.ID, "NX_MEDIA_BIOHSM")

    # 지문 토큰 종류 선택 - BIO
    selection = auto_find_element(
        driver, By.XPATH, '//*[@id="nx-cert-select"]/div[3]/div[1]/div[3]')
    res = auto_wait_until(lambda: selection.is_displayed())
    if not res:
        print("failed")
    else:
        # XXX: 로딩된 이후 디폴트 값이 선택되기 까지 기다린다. 바로 선택하게 되면 디폴트 값으로 돌아가 버린다.
        time.sleep(1)

    # 사용자로 부터 전달 받은 token을 선택
    auto_click(driver, By.XPATH,
               f'//div[@id="cert-select-area3"]/table/tbody/tr/td[contains(text(), "{token}")]')

    # 확인버튼
    auto_click(driver, By.XPATH,
               '//*[@id="pki-extra-media-box-contents3"]/div[3]/button')

    #####################
    # 사용자의 지문 입력 #
    #####################

    # Pin 번호 입력 - display될 때까지 기다린다.
    pin_input = auto_find_element(driver, By.ID, 'nx_cert_pin')
    auto_wait_until(lambda: pin_input.is_displayed(), timeout=120)
    auto_type(pin_input, "00000000")
    auto_click(driver, By.XPATH,
               '//*[@id="pki-extra-media-box-contents3"]/div[2]/button')

    # 확인 버튼
    auto_click(driver, By.XPATH, '//*[@id="nx-cert-select"]/div[4]/button[1]')

    # popup 입찰서 작성안내 (optional)
    button = auto_find_element(driver, By.ID, '_closeBtn1')
    if button:
        auto_click(driver, button)


def _register_v2(driver: WebDriver, number, user, cert_pw):
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
        if alert.text.find("입찰참가등록이 미완료된 건") >= 0:
            alert.accept()
        else:
            print(f"Already registered. text={alert.text}")
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

    # ID: D2b - reg - 보증금 동의문
    # 보증금납부에 대한 서약서 확인
    auto_click(driver, By.ID, 'c_box2')
    auto_click(driver, By.ID, 'c_box3')
    auto_click(driver, By.XPATH,
               '//div[5]/div[2]/div[2]/div/div/div[3]/button[1]')

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

    # ID: D2B - 사후심사대상 입찰안내
    # Not Always
    # ACTION: "닫기" 버튼이 있고, 보인다면 클릭.
    close_btn = auto_find_element(
        driver, By.XPATH, '//*[@id="layer"]/div[2]/div/div/div[2]/button[3]')
    if close_btn and close_btn.is_displayed():
        close_btn.click()

    return True


def _participate_v2(driver, number, cost):
    def is_alpha(c):
        try:
            return c.encode('ascii').isalpha()
        except:
            return False

    def remove_prefix(number):
        while not is_alpha(number[0]):
            number = number[1:]
        return number

    # clear pre/postfix
    number = remove_prefix(number)
    number = number[:7]

    if not _need_registration(driver, number):
        return _participate_without_registration(driver, number, cost)
    else:
        return _participate_with_registration(driver, number, cost)


#################
# HELPER


def _is_login(driver: WebDriver):
    # Logout button 이 있으면 login된 상태
    logout_btn = auto_find_element(driver, By.ID, '_logoutBtn')
    return True if logout_btn else False


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

        _login(self.driver)
        # d2b_login(self.driver, user, id, pw, cert_pw)

    def register(self, pre):

        # return d2b_register(self.driver,  pre.number, self.__user, self.__cert_pw)
        return _register_v2(self.driver, pre.number, self.__user, self.__cert_pw)
        # return _register(driver, number, user)

    def participate(self, bid):
        return _participate_v2(self.driver, bid.number, str(bid.price))


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
