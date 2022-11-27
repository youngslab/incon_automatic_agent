

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import os
import time
import random
import logging
import autoit
from integ_auto import *
from integ_auto.auto import wait


def log():
    return logging.getLogger("kogas")


def file_chooser(filepath):
    window = "[TITLE:열기; CLASS:#32770]"
    autoit.win_wait(window, timeout=60)
    autoit.win_activate(window)
    autoit.win_wait_active(window, timeout=60)

    # Needs some time to wait next steps.
    time.sleep(1)

    # fill the edit box with filepath
    edit_class = "Edit1"
    autoit.control_set_text(window, edit_class, f"\"{filepath}\"")
    log().info(f"Typed a filepath. filepath={filepath}")

    # click ok button
    button_class = "Button1"
    autoit.control_click(window, button_class)


def kogas_login(auto: Automatic):
    # 1. 홈페이지로 이동
    auto.go("https://bid.kogas.or.kr:9443/supplier/index.jsp")

    # 2. 공인인증서 로그인 버튼
    if not auto.click(By.XPATH, '//img[@alt="공동인증서로그인"]'):
        log().error("Error: Failed to find 로그인 button")
        return False

    # 3. 인증서 선택창
    # 3.1 지문보안토큰 클릭
    if not auto.click(By.ID, "NX_MEDIA_BIOHSM"):
        log().error("Error: Failed to find 지문보안토큰")
        return False

    if not auto.click(By.XPATH, '//*[@id="(주)유니온커뮤니티 BIO-SEAL|FP_HSM.dll|1.0.2.1|설치"]'):
        log().error("Error: Failed to find BIO-SEAL 보안 토큰")
        return False

    # 토큰 선택 확인
    if not auto.click(By.XPATH, '//*[@id="pki-extra-media-box-contents3"]/div[3]/button[1]'):
        log().error("Error: Failed to find 토큰 선택 확인")
        return False

    # User Interaction needed

    # 4. pin 번호 입력
    # pin번호 입력
    if not auto.type(By.ID, "nx_cert_pin", "00000000", timeout=120):
        log().error("Failed to find input field for the pin")
        return False

    # pin 번호 입력 확인 버튼
    if not auto.click(By.XPATH, '//*[@id="pki-extra-media-box-contents3"]/div[2]/button[1]'):
        log().error("핀 번호 입력 확인 버튼을 찾을 수 없습니다.")
        return False

    # 인증서 선택 확인 버튼
    if not auto.click(By.XPATH, '//*[@id="nx-cert-select"]/div[4]/button[1]'):
        log().error("인증서 선택 확인 버튼을 찾을 수 없습니다.")
        return False

    # validate
    body_frame = auto.get_element(
        By.XPATH, "//frame[@src='/supplier/bodyframe.jsp']")
    if not body_frame:
        print("Failed to find bodyframe frame")
        return False
    with auto.get_frame(body_frame):
        left = auto.get_element(By.XPATH, "//frame[@src='/supplier/left.jsp']")
        if not left:
            print("Failed to find body frame")
            return False
        with auto.get_frame(left):
            if not auto.get_element(By.XPATH, "//img[@alt='로그아웃']"):
                log().error("로그아웃 버튼을 확인할 수 없습니다.")
                return False

    return True

# # Precondition:
# #  - detail page
# def _is_registered():


def _go_detail_page(auto: Automatic, number):
    top_frame = auto.get_element(By.XPATH, "//frame[@src='/supplier/top.jsp']")
    if not top_frame:
        print("Failed to find top frame")
        return False
    with auto.get_frame(top_frame):
        # 1. 전자 입찰 버튼 클릭
        if not auto.click(By.ID, 'tm_01'):
            print("Failed to find 전자 입찰 버튼 클릭")
            return False

    body_frame = auto.get_element(
        By.XPATH, "//frame[@src='/supplier/bodyframe.jsp']")
    if not body_frame:
        print("Failed to find bodyframe frame")
        return False
    with auto.get_frame(body_frame):
        body = auto.get_element(By.XPATH, "//frame[@src='/supplier/body.jsp']")
        if not body:
            print("Failed to find body frame")
            return False
        with auto.get_frame(body):
            # 입찰번호 입력
            if not auto.type(By.XPATH, '//input[@title="입찰번호"]', number):
                return False

            # 검색 버튼 클릭
            if not auto.click(By.XPATH, '//img[@alt="검색"]'):
                return False

            # 검색 결과 확인
            num = auto.get_element(
                By.XPATH, '//td[text()="입찰번호"]/../../tr[2]/td[1]/a')
            if not num:
                print(f"Failed to find the item. number={number}")
                return False

            if num.text.find(number) < 0:
                print(
                    f"Faile to validate number. expected={number}, real={num.text}")
                return False

            # 첫번째 item 선택
            if not auto.click(By.XPATH, '//tbody/tr[2]/td[2]/a/span'):
                return False

    return True


def close_other_windows(driver: WebDriver):
    current = driver.current_window_handle
    handles = driver.window_handles
    handles.remove(current)
    for handle in handles:
        driver.switch_to.window(handle)
        driver.close()
    driver.switch_to.window(current)


def work_in_frame(auto: Automatic, func):
    body_frame = auto.get_element(
        By.XPATH, "//frame[@src='/supplier/bodyframe.jsp']")
    if not body_frame:
        print("Failed to find bodyframe frame")
        return False
    with auto.get_frame(body_frame):
        body = auto.get_element(
            By.XPATH, "//frame[@src='/supplier/body.jsp']")
        if not body:
            print("Failed to find body frame")
            return False
        with auto.get_frame(body):
            return func()


def kogas_register(auto: Automatic, number, manager_name, manager_phone, manager_email):

    # go homepage
    auto.go("https://bid.kogas.or.kr:9443/supplier/index.jsp")

    close_other_windows(auto.driver)

    # number requirement: 뒤에 번호는 제거
    # 2022062215001-00 -> 2022062215001
    number = number.split('-')[0]

    if not _go_detail_page(auto, number):
        print(f"Failed to go to the detail page. number={number}")
        return False

    # validate - 입찰참가신청이 가능한지 확인.
    # 입찰참가신청 탭이 존재하는지 확인.
    elem = work_in_frame(auto, lambda: auto.get_element(
        By.XPATH, '//a[text()="입찰참가신청"]', timeout=3))
    if not elem:
        log().info("이미등록 되었습니다.")
        return True

    def register_lv1():
        # # 입찰 참가신청
        # 입찰참가신청 탭으로 이동
        if not auto.click(By.XPATH, '//a[text()="입찰참가신청"]'):
            return False

        # 입찰당당자 입력
        if not auto.type(By.XPATH, '//input[@name="ca_name"]', manager_name) or \
           not auto.type(By.XPATH, '//input[@name="ca_tel"]', manager_phone) or \
                not auto.type(By.XPATH, '//input[@name="ca_email"]', manager_email):
            log.error("입찰담당자입력에 실패하였습니다.")
            return False

        # 입찰참가신청 동의 버튼
        if not auto.click(By.XPATH, '//*[@id="registpanel"]/table[17]/tbody/tr/td/a[1]/img'):
            log.error("입창참가신청 동의 버튼을 찾을 수 없습니다.")
            return False

        # Alert 동의 - 약관에 동의하시겠습니까?
        if not auto.accept_alert_with_text("약관에 동의하시겠습니까?"):
            print("Error: Failed to accept alert. - 약관 동의")
            return False

        # 동의 버튼 클릭
        if not auto.click(By.XPATH, '//*[@id="registpanel"]/table[2]/tbody/tr[9]/td[3]/a/img'):
            log().error("동의버튼을 찾을 수 없습니다.")
            return False

        return True

    def register_lv2():
        # 입찰보증금지급각서 윈도우로 이동하여 동의 버튼
        handle = auto.get_window_handle("한국가스공사 전자조달시스템")
        if not handle:
            log().error("윈도우 핸들을 찾을 수 없습니다..")
            return False
        with auto.get_window(handle):
            if not auto.click(By.XPATH, '//img[@alt="동의"]'):
                log().error("동의 버튼을 확인할 수 없습니다.")
                return False

            # 입찰보증금 지급각서에 동의 하시겠습니까?
            if not auto.accept_alert():
                log().error("[동의 하시겠습니까?] 팝업이 생성되지 않았습니다.")
                return False
        return True

    def register_lv3():

        # # 파일 첨부
        # https://sqa.stackexchange.com/questions/43090/how-to-click-button-which-doesnt-have-button-tag-getting-invalidargumentexcept
        # input은 click method를 제공하지 않는다.
        # browser click기능을 사용해야한다고 ..
        elem = auto.get_element(By.NAME, 'FILENAME')
        if not elem:
            log().error("파일 선택 버튼을 찾을 수 없습니다.")
            return False
        ActionChains(auto.driver).move_to_element(elem).click().perform()

        if not auto.accept_alert_with_text("업로드 부탁드립니다."):
            log().error("업로드 확인 공지 팝을을 확인할 수 없습니다.")
            return False

        filepath = os.path.join(os.path.expanduser("~"),
                                ".iaa", "중소기업확인서.pdf")
        log().info(f"파일 첨부 - {filepath}")
        file_chooser(filepath)

        # XXX: 파일 첨부하는데는 약간의 시간이 필요하다. 바로 submit을 누르면 파일이 없는채 제출 되어 실패한다.
        time.sleep(3)

        # 제출 버튼 클릭
        # <img src="/images/b_submit4.gif" align="absmiddle" alt="제출">
        if not auto.click(By.XPATH, '//img[@alt="제출"]'):
            print("Error: Failed to find 제출 버튼")
            return False

        input("xxx")

        popup_title = "제출하시겠습니까?"
        if not auto.accept_alert_with_text(popup_title):
            log().error(f"[{popup_title}] 팝업이 생성되지 않았습니다.")
            return False

        return True

    if not work_in_frame(auto, lambda: register_lv1()):
        return False

    if not register_lv2():
        return False

    if not work_in_frame(auto, lambda: register_lv3()):
        return False

    return True


def get_window_handle_with_url(driver: WebDriver, url):
    current = driver.current_window_handle
    result = None
    handles = driver.window_handles
    handles.remove(current)
    for handle in handles:
        driver.switch_to.window(handle)
        if driver.current_url.find(url) >= 0:
            result = handle
            break
    driver.switch_to.window(current)
    return result


def kogas_participate(auto: Automatic, number, cost):
    # go homepage
    auto.go("https://bid.kogas.or.kr:9443/supplier/index.jsp")

    close_other_windows(auto.driver)

    # number requirement: 뒤에 번호는 제거
    # 2022062215001-00 -> 2022062215001
    number = number.split('-')[0]

    log().info("입찰금액 입력 화면으로 이동")
    if not _go_detail_page(auto, number):
        print(f"Failed to go to the detail page. number={number}")
        return False

    # validation - 이미 참여를 했는지 여부 확인

    def already_participated():
        if auto.get_element(By.XPATH, '//*[contains(text()[2], "투찰하였습니다.")]', timeout=3):
            log().info("이미참여 하였습니다.")
            return True
        return False

    if work_in_frame(auto, lambda: already_participated()):
        return True

    # 참여 시작
    def participate_lv1():
        if not auto.click(By.NAME, 'vat_ck_box'):
            log().error("확인후체크 체크버튼을 찾을 수 없습니다.")
            return False

        boxes = auto.get_elements(By.NAME, 'choice')
        boxes = random.sample(boxes, k=4)
        for box in boxes:
            auto.click(box)

        if not auto.type(By.NAME, 'tot_amt', cost):
            log().error("입찰금액을 입력할 수 없습니다.")
            return False

        if not auto.click(By.XPATH, '//img[@alt="입찰서제출"]'):
            log().error("입찰서제출 버튼을 찾을 수 업습니다. ")
            return False
        return True

    log().info("입찰금액 입력")
    if not work_in_frame(auto, lambda: participate_lv1()):
        return False

    log().info("입찰금액 재확인")
    hwnd = wait(lambda: get_window_handle_with_url(
        auto.driver, "bid_detail_write_bid_popup.jsp"))
    if not hwnd:
        log().error("입찰금액 재확인 윈도우를 찾을 수 없습니다.")
        return False

    with auto.get_window(hwnd):
        e: WebElement = auto.get_element(By.NAME, "confirm_tot_amt")
        auto.driver.execute_script(f'arguments[0].value = "{cost}"', e)

        if not auto.click(By.XPATH, '//img[@alt="제출"]'):
            log().error("입찰금액 재확인: 제출 버튼을 찾을 수 업습니다. ")
            return False

        popup_title = "제출하시겠습니까?"
        if not auto.accept_alert_with_text(popup_title):
            log().error(f"[{popup_title}] 팝업이 생성되지 않았습니다.")
            return False

        time.sleep(3)
        # 지문인증
        if not auto.click(By.ID, "NX_MEDIA_BIOHSM"):
            log().error(f"지문보안토큰 버튼을 찾을 수 없습니다.")
            return False

        if not auto.click(By.ID, "(주)유니온커뮤니티 BIO-SEAL|FP_HSM.dll|1.0.2.1|설치"):
            log().error("토큰을 선택 할 수 없습니다. ")
            return False

        if not auto.click(By.XPATH, '//button[@onclick="NX_Issue_pubUi.moreSaveMediaHide2();return false;"]'):
            log().error("확인 버튼을 찾을 수 없습니다.")
            return False

        #유저입력 (지문검증)

        if not auto.type(By.ID, "nx_cert_pin", "00000000", timeout=120):
            log().error("핀번호를 입력할 수 없습니다. ")
            return False

        if not auto.click(By.XPATH, '//button[@onclick="NX_Issue_pubUi.moreSaveMediaHide7();return false;"]'):
            log().error("핀번호 확인버튼을 찾을 수 없습니다. ")
            return False

        if not auto.click(By.XPATH, '//button[@onclick="NX_Issue_pubUi.selectCertConfirm();"]'):
            log().error("마지막 인증 확인버튼을 찾을 수 없습니다. ")
            return False

        if not auto.accept_alert_with_text("완료되었습니다."):
            log().error("[완료되었습니다.] 팝업이 생성되지 않았습니다.")
            return False

    # TODO: implements
    return True


class Kogas:
    def __init__(self, manager_name, manager_phone, manager_email):
        driver = Automatic.create_edge_driver()
        self.auto = Automatic(driver)
        self.manager_name = manager_name
        self.manager_phone = manager_phone
        self.manager_email = manager_email

    def __del__(self):
        log().debug("__del__")
        self.auto.driver.close()

    def login(self):
        return kogas_login(self.auto)

    def register(self, code):
        return kogas_register(self.auto, code, self.manager_name,
                              self.manager_phone, self.manager_email)

    def participate(self, code, cost):
        return kogas_participate(self.auto, code, cost)

    # def participate(self, code, price):
    #     log().info(f"participate in {code} price={price}")
    #     return _participate_v2(self.driver, code, price)
