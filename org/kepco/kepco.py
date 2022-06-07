

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
from auto.auto import auto_is_visible


def log():
    return logging.getLogger(__package__)


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


def kepco_login(driver, id, pw, cert_pw):
    with Frame(driver, (By.ID, "mdiiframe-1010-iframeEl")) as f:
        auto_click(driver, By.ID, 'memberLogin')

    with Frame(driver, (By.ID, 'kepcoLoginPop')):
        auto_type(driver, By.ID, 'username', id)
        auto_type(driver, By.ID, 'password', pw)
        auto_click(driver, By.ID, 'certBtn')

    kepco_certificate_login(driver, cert_pw)


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
    btn = notice.find_element(By.XPATH, "./div[2]/div/div/a/span/span/span[2]")
    if not btn:
        log().error("Failed to find button.")
        return False
    auto_click(driver, btn)
    return True

# --------------------
# Message Box
# --------------------


def kepco_get_messagebox(driver: WebDriver):
    messagebox = auto_find_element(
        driver, By.XPATH, '//div[contains(@class,"x-window") and contains(@class,"x-message-box")]')
    auto_wait_until(lambda: kepco_messagebox_is_open(messagebox))
    return messagebox


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

    # Should wait until it shows.
    status = auto_find_element(
        panel, By.XPATH, ".//div[1]/div[1]/div[1]/div[2]/div[3]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/table[1]/tbody[1]/tr[1]/td[3]/div[1]")

    if not status:
        log().error("Failed to get status column.")
        return False

    if status.text == "심사완료":
        log().info("Already Registered")
        return True

    if status.text == "미제출":
        return False

    log().error(f"Failed. Unkown status. status={status.text}")
    raise Exception("Unkwon status")


def kepco_pre_apply_participation(driver: WebDriver):

    panel = kepco_pre_get_regigteration_panel(driver)

    # check button
    checkbox = auto_find_element(panel, By.XPATH,
                                 "./div/div/div/div[2]/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/table/tbody/tr/td/div/div")
    auto_click(driver, checkbox)

    # Click
    register_btn = panel.find_element(By.XPATH, './/span[text()="입찰참가신청"]')
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
        messagebox = kepco_get_messagebox(driver)
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
    panel.find_element(By.XPATH, './/span[text()="파일첨부"]').click()

    # select a file.
    auto_file_chooser(filepath)

    # validate file attachment
    filename = os.path.basename(filepath)
    if not auto_find_element(driver, By.XPATH, f'.//div[text()="{filename}"]'):
        raise Exception(f"Failed to attach a file. filename={filename}")


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

    # XXX: TEMP - wait
    input("press enter to continue")

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
    messagebox = kepco_get_messagebox(driver)
    button = kepco_messagebox_get_button(messagebox, "확인")
    if not button:
        raise Exception("Failed to find 확인 buttons")
    auto_click(driver, button)


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
    kepco_pre_apply_participation(driver)

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

    # 3.2 certificate login
    log().info("3.2 certifiate")
    kepco_certificate_login(driver, "GetLastError#2")

    log().info("3.3 done")
    kepco_pre_confirm_done(driver)

    return True


class Kepco:
    # headless: Do not allow with headless, It will fails to login.
    def __init__(self, id, pw, cert_pw, headless=False):
        log().debug("__init__")
        self.__cert_pw = cert_pw
        self.driver = kepco_create_driver(headless=headless)
        kepco_go_homepage(self.driver)
        kepco_login(self.driver, id, pw, cert_pw)

    def __del__(self):
        log().debug("__del__")
        # self.driver.close()

    def register(self, pre):
        return kepco_pre_register(self.driver, pre.number)

    def participate(self, bid):
        return False, "Kepco Not implemented yet"


if __name__ == "__main__":
    id = account.account_get("kepco", "id")
    pw = account.account_get("kepco", "pw")
    cert = account.account_get("kepco", "cert")
    kepco = Kepco(id, pw, cert)

    # print(kepco.register("G012202823"))
