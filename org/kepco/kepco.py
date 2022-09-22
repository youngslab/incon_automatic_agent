

import os
import time
import logging

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
import account
from auto import *
import random

# MessageBox
import win32api
from win32con import MB_SYSTEMMODAL, MB_YESNO

# ------------------------
# Version 2
# ------------------------
# ID: Kepco - 모든 popup 창 닫기


def close_all_popup(driver, timeout=10):

    start = time.time()

    while True:
        # messagebox
        #  - 낙찰 후 미계약 건에 대한 공지         - 확인
        #  - 변경 미등록시 입찰무효처리에 대한 공지 - 확인
        messagebox = kepco_get_messagebox(driver, timeout=3)
        if messagebox:
            if kepco_messagebox_is_open(messagebox):
                confirm_btn = kepco_messagebox_get_button(messagebox, "확인")
                auto_click(driver, confirm_btn)

        # multiple notices
        notices = kepco_get_notices(driver)
        for notice in notices:
            if kepco_notice_is_open(notice):
                kepco_notice_close(driver, notice)

        curr = time.time() - start
        if curr > timeout:
            break

        time.sleep(0.5)


# ------------------------
# TAB APIs
# ------------------------

def wait_no_element(driver: WebDriver, locator, timeout: int = 10) -> bool:
    try:
        return WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located(locator))
    except Exception as e:
        return None

# ID: Kepco - 모든 탭 닫기
# Description: 항상


def close_all_tab(driver: WebDriver):

    driver.refresh()

    # wait unti
    try:
        WebDriverWait(driver, 3).until(
            EC.alert_is_present(), "Can not find an alert window")
        # accept alert
        driver.switch_to.alert.accept()
        log().info("Refresh")

    except Exception as e:
        log().info("No need to refresh")

    # # find close tab buttons
    # btns = wait_all_elements(
    #     driver, (By.XPATH, '//span[@class="x-tab-close-btn"]'))
    # for btn in btns:
    #     btn.click()

    # while True:
    #     if not wait_element(
    #             driver, (By.XPATH, '//span[@class="x-tab-close-btn"]')):
    #         break

    # TODO: not working...
    # Wait until tabs are closed
    # 탭에 있는 close button을 확인해 본다.
    # wait_no_element(
    #     driver, (By.XPATH, '//span[@class="x-tab-close-btn"]'), timeout=3)


# ID: 입찰(투찰진행) 탭 열기
# Precondition
#    - home tab이 있어야 한다.


def open_bid_tab(driver: WebDriver):
    # Wait home tab:
    if not wait_element(driver, (By.XPATH, '//span[text()="home"]')):
        log().error("Not found home tab. We should wait until it comes")
        return False

    # TODO: 입찰/계약 버튼의 위치가 변경 될 수 도 있다.
    # 입찰/계약 버튼
    btn = wait_clickable(driver, (By.XPATH, '//span[text()="입찰/계약"]'))
    if not btn:
        log().error("Not found 입찰/계약 button")
        return False
    btn.click()

    # 입찰(투찰진행) 버튼
    btn = wait_clickable(driver, (By.XPATH, '//h4[text()=" 입찰(투찰진행) "]'))
    if not btn:
        log().error("Not found 입찰참가신청 button")
        return False
    btn.click()

    # Wait until the tab created
    # 탭에 있는 close button을 확인해 본다.
    btn = wait_clickable(
        driver, (By.XPATH, '//span[@class="x-tab-close-btn"]'))
    return True if btn else False

# ID: 입찰(투찰진행) 탭 열기
# Precondition
#    - home tab이 있어야 한다.


def open_register_tab(driver: WebDriver):
    # Wait home tab:
    if not wait_element(driver, (By.XPATH, '//span[text()="home"]')):
        log().error("Not found home tab. We should wait until it comes")
        return False

    # TODO: 입찰/계약 버튼의 위치가 변경 될 수 도 있다.
    # 입찰/계약 버튼
    btn = wait_clickable(driver, (By.XPATH, '//span[text()="입찰/계약"]'))
    if not btn:
        log().error("Not found 입찰/계약 button")
        return False
    btn.click()

    # 입찰참가신청 버튼
    btn = wait_clickable(driver, (By.XPATH, '//h4[text()=" 입찰참가신청 "]'))
    if not btn:
        log().error("Not found 입찰참가신청 button")
        return False
    btn.click()

    # Wait until the tab created
    # 탭에 있는 close button을 확인해 본다.
    btn = wait_clickable(
        driver, (By.XPATH, '//span[@class="x-tab-close-btn"]'))
    return True if btn else False


def create_driver(headless=False):
    options = webdriver.EdgeOptions()
    options.add_argument('log-level=3')
    if headless:
        options.add_argument('headless')
        options.add_argument('disable-gpu')

    # add extension
    # SecuKit NX(edge://extensions/?id=hghadmnjlclmajeenogjjjefdecofpag)
    extension_path = os.path.join(os.path.expanduser(
        '~'), ".iaa", 'secukit_nx_1.0.1.12_0.crx')
    options.add_extension(extension_path)

    service = Service(EdgeChromiumDriverManager().install())
    return webdriver.Edge(options=options, service=service)


def login(driver: WebDriver, id, pw, cert):
    log().debug("login")
    kepco_go_homepage(driver)
    kepco_login(driver, id, pw, cert)


def _register_v2(driver: WebDriver, number, *, cert=None):

    # close_all_tab
    log().info("0. 모든 탭 닫기")
    close_all_tab(driver)

    # # 1. 공고번호 조회
    log().info("1. 공고번호 조회 tab 열기")
    if not open_register_tab(driver):
        log().error("Failed to open register tab.")
        return False

    # 1.2 조회
    log().info("1.2 search")
    # ID: Kepco - 입찰 - 공고번호 검색
    # 공고번호 입력
    num_input = wait_clickable(driver, (By.XPATH, '//input[@title="공고번호"]'))
    num_input.send_keys(number)

    # 조회 버튼 클릭
    search_btn = wait_clickable(driver, (By.XPATH, '//span[text()="조회"]'))
    search_btn.click()

    #  1.3
    log().info("1.3 validate")
    if kepco_pre_is_current_registered(driver):
        log().info("Already registered")
        return True

    log().info("1.4 apply")
    if not kepco_pre_apply_participation(driver):
        log().error("Failed to apply")
        return False

    # 2. Application Form
    # 2.1.  메세지등의 팝업을 처리한다.
    log().info("2.1 close popup")
    kepco_pre_close_popup(driver)

    # 2.2. 중소기업확인서 첨부
    log().info("2.2 attach a file")
    filepath = os.path.join(os.path.expanduser("~"), ".iaa", "AR_중소기업_확인서.pdf")
    kepco_attach_small_business_confirmation_document(driver, filepath)

    # XXX: 빠르게 진행하기 때문에 다시 제출하라는 문구가 뜨는 것 같음
    time.sleep(10)

    # 모든 조항에 동의
    log().info("2.3 aggreement")
    kepco_pre_agree_commitments(driver)

    # XXX: 빠르게 진행하기 때문에 다시 제출하라는 문구가 뜨는 것 같음
    time.sleep(10)

    # 2.3 제출 버튼 클릭
    log().info("2.4 submit")
    kepco_pre_submit_application_form(driver)

    # 3. 정리
    # 3.1 확인
    # XXX: 제출 버튼을 클릭한 후, popup이open될 때 까지 기다린다.
    log().info("3.1 confirm")
    if not kepco_pre_confirm_submission(driver):
        # "입찰참가신청등록 화면에 있는 닫기버튼을 눌러 다시 신청하세요."
        return False

    # 3.2 certificate login (Optional)
    if cert:
        log().info("3.2 certifiate")
        kepco_certificate_login(driver, cert)

    # 확인 버튼 클릭(알림: 제출 하였습니다.
    log().info("3.3 done")
    kepco_pre_confirm_done(driver)

    return True


# --------------------------

# ID: Kepco - 입찰 - 검색결과 검증
# Description: 투찰진행상태를 확인한다. - 미제출
def can_participate(driver: WebDriver) -> bool:
    elem = auto_find_element(
        driver, By.XPATH, "//div[2]/div/div[2]/table/tbody/tr/td[2]/div")
    if elem.text == "미제출":
        return True
    else:
        return False


# ID: Kepco - 입찰 - 검색결과 검증
def validate_bid_search_result(driver: WebDriver, number):
    es = auto_find_all_elements(
        driver, By.XPATH, '//div[@class="x-grid-row-checker"]')
    if len(es) != 1:
        log().error(
            f"Failed to validate the result. Item should be only one. found={len(es)} ")
        return False

    # validate number
    e = auto_find_element(
        driver, By.XPATH, '//div[2]/table[1]/tbody/tr/td[5]/div[contains(@class,"x-grid-cell-inner")]')
    bid_num = e.text
    if number.find(bid_num) < 0:
        log().error(
            f"Failed to validate the result. Bid number missmatch. found={bid_num}, expected={number} ")
        return False

    return True


def _participate_v2(driver, number, cost):
    # close all tabs
    close_all_tab(driver)

    # open bid tab
    if not open_bid_tab(driver):
        log().error("Failed to open bind tab.")
        return False

    # ID: Kepco - 입찰 - 공고번호 검색
    # 공고번호 입력
    num_input = wait_clickable(driver, (By.XPATH, '//input[@title="공고번호"]'))
    num_input.send_keys(number)

    # 조회 버튼 클릭
    # XXX: 가끔 click이 안되는 경우가 있다. - ElementClickInterceptedException
    # auto_click(driver, By.XPATH, '//span[text()="조회"]')
    search_btn = wait_clickable(driver, (By.XPATH, '//span[text()="조회"]'))
    try:
        search_btn.click()
    except:
        driver.execute_script("arguments[0].click();", search_btn)

    # messagebox : 공고일자의 최대 검색일자는 6개월 입니다. "확인"
    msgbox = kepco_get_messagebox(driver, timeout=5)
    if msgbox:
        log().info(f"messagebox: text={msgbox.text}")
        okbtn = kepco_messagebox_get_button(msgbox, "확인")
        okbtn.click()

    # ID: Kepco - 입찰 - 검색결과 검증
    if not validate_bid_search_result(driver, number):
        log().error("Validation Failed.")
        return False

    # Description: 투찰진행상태 가져오기
    if not can_participate(driver):
        log().info("Already Registered.")
        return True

    # ID: Kepco - 입찰 - 입찰참여 버튼
    # checkbox click
    log().info(f"Kepco - 입찰 - 입찰참여 버튼")
    auto_click(driver, By.XPATH, '//div[@class="x-grid-row-checker"]')
    # TODO: 안눌리는 경우가 생긴다.
    if not auto_click(driver, By.XPATH, '//span[text()="입찰참여"]'):
        log().error("Failed to click 입찰참여 button.")
        return False

    # messagebox - 입찰 창여 하시겠습니까?
    msgbox = kepco_get_messagebox(driver)
    log().info(f"messagebox: text={msgbox.text}")
    yesbtn = kepco_messagebox_get_button(msgbox, "예")
    yesbtn.click()

    # ID: Kepco - 입찰 - 입찰서 작성 - 지문인식 투찰 버튼
    log().info(f"Kepco - 입찰 - 입찰서 작성 - 지문인식 투찰 버튼")
    fp_bid_btn = wait_element(driver, (By.XPATH, '//td[5]/div/img'))
    fp_bid_btn.click()

    # TODO: 시간이 오래된 경우 공인인증서 확인 창이 생성된다.

    # messagebox - 지문인식투찰을 진행하시겠습니까?
    msgbox = kepco_get_messagebox(driver)
    log().info(f"messagebox: text={msgbox.text}")
    okbtn = kepco_messagebox_get_button(msgbox, "예")
    okbtn.click()

    # close all popup
    log().info(f"Kepco - Common - 모든 팝업창 닫기")
    close_all_popup(driver, timeout=15)

    # ID: Kepco - 입찰 - 추첨
    log().info(f"Kepco - Common - 추첨번호 선택")
    boxes = auto_find_all_elements(
        driver, By.XPATH, '//span[contains(text(),"예정가격추첨갯수")]/../../div/div/table/tbody/tr/td/a/span/span/span[2]')
    if len(boxes) != 15:
        log().error(f"Failed to find 추첨갯수. expected:15, found:{len(boxes)}")
        input("Press any keys to move on.")
        return False

    boxes = random.sample(boxes, k=4)
    for box in boxes:
        # 4개가 모두 click이 안되는 경우가 있다.
        # 중복된 개체가 있는 것으로 보인다.
        time.sleep(1)
        auto_click(driver, box)

    # ID: Kepco - 입찰 - 가격입력
    # ---------------------------
    cost_box = wait_element(
        driver, (By.XPATH, "//tbody/tr[4]/td/div[1]/div/div/table/tbody/tr/td/div[1]/label/span[text()='숫자']/../.."))

    # input layer
    input_layer = cost_box.find_element(By.XPATH, './/input')
    driver.execute_script(f'arguments[0].value = "{cost}"', input_layer)

    # focus
    text_layer = cost_box.find_element(
        By.XPATH, './/div[@class="x-form-field-inputcover-displayEl"]')
    text_layer.click()

    valid_box = wait_element(
        driver, (By.XPATH, "//tbody/tr[4]/td/div[1]/div/div/table/tbody/tr/td/div[1]/label/span[text()='확인']/../.."))

    # input layer
    input_layer = valid_box.find_element(By.XPATH, './/input')
    driver.execute_script(f'arguments[0].value = "{cost}"', input_layer)

    # focus
    text_layer = valid_box.find_element(
        By.XPATH, './/div[@class="x-form-field-inputcover-displayEl"]')
    text_layer.click()

    # focus out to temp element.
    cost_box.click()

    # 입력값 확인 버튼
    auto_click(driver, By.XPATH, '//span[text()="입력값확인"]')

    # ---------------------------
    # ID: Kepco - 입찰 - 제출
    # ---------------------------
    auto_click(driver, By.XPATH, '//span[text()="제출"]')
    msgbox = kepco_get_messagebox(driver)
    yesbtn = kepco_messagebox_get_button(msgbox, "예")
    yesbtn.click()

    # message box - 제출되었습니다.
    msgbox = kepco_get_messagebox(driver)
    btn = kepco_messagebox_get_button(msgbox, "확인")
    btn.click()

    return True
# -----------------------------


def log():
    return logging.getLogger("kepco")


def kepco_create_driver(headless=False):
    options = webdriver.EdgeOptions()
    options.add_argument('log-level=3')
    if headless:
        options.add_argument('headless')
        options.add_argument('disable-gpu')

    # add extension
    # SecuKit NX(edge://extensions/?id=hghadmnjlclmajeenogjjjefdecofpag)
    extension_path = os.path.join(os.path.expanduser(
        '~'), ".iaa", 'secukit_nx_1.0.1.12_0.crx')
    options.add_extension(extension_path)

    service = Service(EdgeChromiumDriverManager().install())
    return webdriver.Edge(options=options, service=service)


def kepco_go_homepage(driver):
    driver.get("https://srm.kepco.net/index.do")


def kepco_certificate_login(driver, pw):
    with Frame(driver, (By.XPATH, '//iframe[contains(@src,"kica/WebUI/kepco_html/kicaCert.jsp")]'), timeout=30):
        auto_click(driver, By.XPATH, '//div[text()="사업자(범용)"]', timeout=60)
        auto_type(driver, By.ID, "certPwd", pw)
        auto_click(driver, By.XPATH, '//img[@src="../img/btn_confirm.png"]')


# fp_login(finger_print)
# XXX: input token - BIO-SEAL could be changed
def kepco_certificate_fp_login(driver):

    with Frame(driver, (By.XPATH, '//iframe[contains(@src,"kica/WebUI/kepco_html/kicaCert.jsp")]'), timeout=30):
        # XXX: 바로 바이오 토큰을 선택하면 인증서가 남아 있는 현상이 있는데 이를
        # 제거하기 위해 잠시 시간을 갖는다.
        time.sleep(1.5)

        # select certificate location: bio-token
        auto_click(driver, By.XPATH, '//button[text()="바이오토큰"]')
        auto_click(driver, By.XPATH,
                   '//*[@id="js-seltab"]/li[5]/div/ul/li/a[contains(text(), "BIO-SEAL")]')
    # login as usual
    return kepco_certificate_login(driver, "00000000")


def kepco_login(driver, id, pw, *, cert_pw=None):
    with Frame(driver, (By.ID, "mdiiframe-1010-iframeEl")) as f:
        auto_click(driver, By.ID, 'memberLogin')

    with Frame(driver, (By.ID, 'kepcoLoginPop')):
        auto_type(driver, By.ID, 'username', id)
        auto_type(driver, By.ID, 'password', pw)
        auto_click(driver, By.ID, 'certBtn')

    if cert_pw:
        kepco_certificate_login(driver, cert_pw)
    else:
        kepco_certificate_fp_login(driver)

    # validate login
    # 로그인 버튼이 안보이는 상태로 전환될 때 까지 기다린다.
    # XXX: 지문 로그인 이후 시간이 좀 걸린다.
    if not wait_element(driver, (By.XPATH,
                                 '//a[contains(@style, "display: none;")]/span/span/span[2 and text()="로그인"]'), timeout=200):
        log.error("실패 - 로그인 버튼이 200초 동안 사라지지 않았음")
        return False

    return True

# --------------------
# Notice
# --------------------


def kepco_get_notices(driver: WebDriver):
    return driver.find_elements(By.XPATH, '//div[contains(@class,"x-panel") and contains(@class,"x-panel-popup")]')


def kepco_notice_is_open(notice: WebElement):
    return True if notice.get_attribute("style").find("display: none") < 0 else False


def kepco_notice_get_title(notice: WebElement):
    return notice.find_element('./div[1]/div/div/div/div/div[1]/h1').text


def kepco_notice_close(driver: WebDriver, notice: WebElement):
    if not notice:
        log().error("Notice is none")
        return False

    # 닫기
    # - 일반     : /html/body/div[18]/div[2]/div/div/a/span/span/span[2]
    # - 서부발전 : /html/body/div[24]/div[3]/div/div/a/span/span/span[2]

    btn = notice.find_element(By.XPATH, "./div/div/div/a/span/span/span[2]")
    if not btn:
        log().error("Failed to find button.")
        return False
    auto_click(driver, btn)
    return True

# --------------------
# Message Box
# --------------------


def kepco_get_messagebox(driver: WebDriver, timeout=60) -> WebElement:
    messagebox = auto_find_element(
        driver, By.XPATH, '//div[contains(@class,"x-window") and contains(@class,"x-message-box")]', timeout=timeout)
    found = auto_wait_until(
        lambda: kepco_messagebox_is_open(messagebox), timeout=timeout)
    return messagebox if found else None


def kepco_messagebox_is_open(msgbox: WebElement):
    if not msgbox:
        log().error("Message box is none")
        return False
    return True if msgbox.get_attribute("class").find("x-hidden-offsets") < 0 else False


def kepco_messagebox_button_get_text(button: WebElement):
    if not button:
        log().error("Button is none")
        return False
    return button.find_element(By.XPATH, "./span/span/span[2]").text


def kepco_messagebox_get_buttons(messagebox: WebElement):
    if not messagebox:
        log().error("Message box is none")
        return None
    return messagebox.find_elements(By.XPATH, "./div[3]/div/div/a")


def kepco_messagebox_get_button(messagebox: WebElement, text: str):
    buttons = kepco_messagebox_get_buttons(messagebox)
    for button in buttons:
        if kepco_messagebox_button_get_text(button) != text:
            continue
        return button
    return None


def kepco_messagebox_get_text(messagebox: WebElement):
    if not messagebox:
        log().error("Message box is none")
        return None
    return messagebox.find_element(By.XPATH, "./div[2]/div/div/div[1]/div/div/div[2]/div/div/div[1]/div/div").text


# --------------------
# PANELS
# --------------------

def kepco_get_active_panel(driver: WebDriver) -> WebElement:
    es = driver.find_elements(By.XPATH, '//body[1]/div[4]/div[2]/div')
    for e in es:
        style = e.get_attribute("style")
        if style.find('display: none') > 0:  # if not visible
            continue
        return e
    return None


def kepco_get_active_panel_title(driver: WebDriver):
    es = driver.find_elements(
        By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div/div/div/div/div/div/div/a')
    return es[-1].text


def kepco_pre_get_regigteration_panel(driver: WebDriver):
    current_title = kepco_get_active_panel_title(driver)
    if current_title != "입찰참가신청":
        raise Exception("Current title is not 입찰참가신청")

    active_panel = kepco_get_active_panel(driver)

    # find subpanel from active main panel
    return active_panel.find_element(By.XPATH, './/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]')


def kepco_pre_go_register_page(driver: WebDriver):

    # Wait home: 입찰참가신청중에 갑자기 홈이 생겨버려 순서가 엉망이 될 수 있다.
    if not auto_find_element(driver, By.XPATH, '/html/body/div[4]/div[1]/div[1]/div[2]/div/a[1]/span/span/span[2 and text()="home"]'):
        raise Exception("Not found home tab. We should wait until it comes")

    # TODO: 입찰/계약 버튼의 위치가 변경 될 수 도 있다.
    # 입찰/계약 버튼
    auto_click(driver, By.XPATH,
               "/html/body/div[1]/div/div/div[2]/div[2]/div/a[3]")
    # 입찰참가신청 버튼
    auto_click(driver, By.XPATH,
               "/html/body/div[2]/div[3]/div/div[2]/table[1]/tbody/tr/td")


def kepco_pre_search_notice_number(driver: WebDriver, number):
    # 공고번호 input
    bid_number = auto_find_element(driver, By.XPATH, '//input[@title="공고번호"]')

    bid_number.clear()
    time.sleep(0.5)
    bid_number.send_keys(number)

    # 조회버튼
    panel = kepco_pre_get_regigteration_panel(driver)
    search_btn = panel.find_element(By.XPATH, './/span[text()="조회"]')
    auto_click(driver, search_btn)


def kepco_pre_is_current_registered(driver: WebDriver):
    # Validate the result
    panel = kepco_pre_get_regigteration_panel(driver)
    if not panel:
        log().error("Failed to find registration panel.")
        return False

    # Should wait until it shows.
    status = auto_find_element(
        panel, By.XPATH, ".//div[1]/div[1]/div[1]/div[2]/div[3]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/table[1]/tbody[1]/tr[1]/td[3]/div[1]")
    if not status:
        log().error("Failed to get status column.")
        return False

    if status.text == "심사완료":
        log().info(f"Already Registered. status={status.text}")
        return True

    if status.text == "제출":
        log().info(f"Already Registered. status={status.text}")
        return True

    if status.text == "미제출":
        return False

    log().error(f"Failed. Unkown status. status={status.text}")
    return False


def kepco_pre_apply_participation(driver: WebDriver):

    panel = kepco_pre_get_regigteration_panel(driver)
    if not panel:
        log().error("Failed to find a registration panel")
        return False

    # check button
    checkbox = auto_find_element(
        panel, By.XPATH, '//div[@class="x-grid-row-checker"]')
    if not checkbox:
        log().error("Failed to find a checkbox of the item")
        return False
    auto_click(driver, checkbox)

    # TODO: validate

    # Click
    register_btn = panel.find_element(By.XPATH, './/span[text()="입찰참가신청"]')
    if not checkbox:
        log().error("Failed to find a button of 입찰참가신청")
        return False

    auto_click(driver, register_btn)
    return True


# every 0.5 sec, try to close message boxes and notices for 10 sec
# 계약건마다 다른 공지 내용과 메세지박스가 생성되기 때문에 모든 경우에
# 해당하는 처리를 할 수 없기 때문에 특정 기간동안 등장하는 모든 popup
# window들을 종료 시키는 방식을 택했다.
def kepco_pre_close_popup(driver, timeout=10):

    start = time.time()

    while True:
        # messagebox
        #  - 낙찰 후 미계약 건에 대한 공지         - 확인
        #  - 변경 미등록시 입찰무효처리에 대한 공지 - 확인
        messagebox = kepco_get_messagebox(driver, timeout=1)
        if kepco_messagebox_is_open(messagebox):
            confirm_btn = kepco_messagebox_get_button(messagebox, "확인")
            auto_click(driver, confirm_btn)

        # multiple notices
        notices = kepco_get_notices(driver)  # no wait Apis
        for notice in notices:
            if kepco_notice_is_open(notice):
                kepco_notice_close(driver, notice)

        curr = time.time() - start
        if curr > timeout:
            break

        time.sleep(0.5)


# Find file attachment_panel
def kepco_pre_get_file_attachment_panel(driver):
    # validate current page
    current_title = kepco_get_active_panel_title(driver)
    if current_title != "입찰참가신청":
        raise Exception("Current title is not 입찰참가신청")

    # active panel
    active_panel = kepco_get_active_panel(driver)

    # find file attachment subpanel from main active panel
    return auto_find_element(active_panel, By.XPATH, './/div/div[2]/div[3]/div/div/div[5]')


def kepco_attach_small_business_confirmation_document(driver: WebDriver, filepath):
    panel = kepco_pre_get_file_attachment_panel(driver)
    # XXX: file chooser should be clicked not by javascript

    # 파일첨부
    try:
        panel.find_element(By.XPATH, './/span[text()="파일첨부"]').click()
    except:
        # XXX: If popup are not cleared by previous process("close_all_popup")
        #      Then, Exception(ElementClickInterceptedException) would occur.
        log().error("Failed to click 파일첨부. Some of Popups might be not cleared and hides button. ")
        return False

    # select a file.
    auto_file_chooser(filepath)

    # validate file attachment
    filename = os.path.basename(filepath)
    if not auto_find_element(driver, By.XPATH, f'.//div[text()="{filename}"]'):
        log().error(f"Failed to validate the attachment. filename={filename}")
        return False

    return True


def kepco_pre_get_application_form(driver: WebDriver) -> WebElement:
    panel = kepco_get_active_panel(driver)
    return panel.find_element(By.XPATH, './div/div[2]/div[3]/div')


# 약정들에 동의함
def kepco_pre_agree_commitments(driver):
    application_form = kepco_pre_get_application_form(driver)
    # find all check boxes of each commitments to agree
    check_btns = application_form.find_elements(
        By.XPATH, './div/div[not(contains(@style,"display: none"))]/div[3]/div/div/div[2]/div/div/input')
    for btn in check_btns:
        # aggree
        auto_click(driver, btn)


def kepco_pre_submit_application_form(driver):
    panel = kepco_get_active_panel(driver)
    submit_btn = panel.find_element(By.XPATH, './/span[text()="제출"]')
    auto_click(driver, submit_btn)


def kepco_pre_confirm_submission(driver: WebDriver):
    messagebox = kepco_get_messagebox(driver)

    auto_wait_until(lambda: kepco_messagebox_is_open(messagebox))

    print(f'messagebox: {kepco_messagebox_get_text(messagebox)}')

    button = kepco_messagebox_get_button(messagebox, "예")
    if button:
        auto_click(driver, button)
        return True

    button = kepco_messagebox_get_button(messagebox, "확인")
    if button:
        auto_click(driver, button)
        return False

    return False


def kepco_pre_confirm_done(driver: WebDriver):
    # message box 생성되는데 시간이 오래 걸린다.
    #     => 60초 정도 대기하는 것으로 변경.
    messagebox = kepco_get_messagebox(driver, timeout=60)
    if not messagebox:
        log().error("Failed to find Message Box")
        return False

    button = kepco_messagebox_get_button(messagebox, "확인")
    if not button:
        log().error("Failed to find 확인 buttons")
        return False

    if not auto_click(driver, button):
        log().error("Failed to click 확인 buttons")
        return False

    return True


def kepco_pre_register(driver: WebDriver, number):

    # 1. 공고번호 조회

    # 1.1 입찰 참가신청 페이지로 이동
    kepco_pre_go_register_page(driver)

    # 1.2 조회
    log().info("1.2 search")
    kepco_pre_search_notice_number(driver, number)

    #  1.3
    log().info("1.3 validate")
    if kepco_pre_is_current_registered(driver):
        log().info("Already registered")
        return True

    log().info("1.4 apply")
    if not kepco_pre_apply_participation(driver):
        log().error("Failed to apply")
        return False

    # 2. Application Form
    # 2.1.  메세지등의 팝업을 처리한다.
    log().info("2.1 close popup")
    kepco_pre_close_popup(driver)

    # 2.2. 중소기업확인서 첨부
    log().info("2.2 attach a file")
    filepath = os.path.join(os.path.expanduser("~"), ".iaa", "AR_중소기업_확인서.pdf")
    if not kepco_attach_small_business_confirmation_document(driver, filepath):
        log().error("failed to attach a file for small busineess.")
        return False

    # XXX: 빠르게 진행하기 때문에 다시 제출하라는 문구가 뜨는 것 같음
    time.sleep(10)

    # 모든 조항에 동의
    log().info("2.3 aggreement")
    kepco_pre_agree_commitments(driver)

    # XXX: 빠르게 진행하기 때문에 다시 제출하라는 문구가 뜨는 것 같음
    time.sleep(10)

    # 2.3 제출 버튼 클릭
    log().info("2.4 submit")
    kepco_pre_submit_application_form(driver)

    # 3. 정리
    # 3.1 확인
    # XXX: 제출 버튼을 클릭한 후, popup이open될 때 까지 기다린다.
    log().info("3.1 confirm")
    if not kepco_pre_confirm_submission(driver):
        # "입찰참가신청등록 화면에 있는 닫기버튼을 눌러 다시 신청하세요."
        return False

    # 3.2 certificate login
    log().info("3.2 certifiate")
    kepco_certificate_login(driver, "GetLastError#2")

    log().info("3.3 done")
    kepco_pre_confirm_done(driver)

    return True


# -----------------------
# Object Version
# -----------------------

class Kepco:
    # headless: Do not allow with headless, It will fails to login.
    def __init__(self, id, pw, *, cert_pw=None, headless=False):
        log().debug("__init__")
        self.id = id
        self.pw = pw
        self.__cert_pw = cert_pw
        self.driver = kepco_create_driver(headless=headless)
        kepco_go_homepage(self.driver)

    def __del__(self):
        log().debug("__del__")
        self.driver.close()

    def login(self):
        return kepco_login(self.driver, self.id, self.pw, cert_pw=self.__cert_pw)

    def register(self, code):
        return _register_v2(self.driver, code)

    def participate(self, code, price):
        log().info(f"participate in {code} price={price}")
        return _participate_v2(self.driver, code, price)


if __name__ == "__main__":
    id = account.account_get("kepco", "id")
    pw = account.account_get("kepco", "pw")
    cert = account.account_get("kepco", "cert")
    kepco = Kepco(id, pw)

    print(kepco.participate("G012204203"))
