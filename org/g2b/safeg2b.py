import elevate
import ctypes
import os
import sys
import time
import random
import subprocess
import auto.windows
import pyautogui
import win32gui
import win32con
import win32api
import win32process

import org.g2b.certificate
from org.g2b.res import resmgr

from auto import *
import auto.windows
import auto.selenium


__default_timeout = 60


def _log():
    import logging
    return logging.getLogger(__name__)


# -------------------
# VERSION 2
# --------------------

# ------------------------------
# Login - Biotoken Support
# -------------------------------
def _go_to_login_page():
    _log().info("try to go home.")
    if not auto_click(resmgr.get('safeg2b_0_etc_homepage.png')):
        _log().info("Can't go home. But it's ok. That means it's already at home")
        return False
    return True


# Verify its login state at the login page
# Precondition
# - Should be at login_page
def _is_login():
    # Wait until 15sec to check the login state.
    pos = wait_image(resmgr.get(
        'safeg2b_login_btn.png'), grayscale=False, confidence=0.8, timeout=15)
    return True if pos is None else False

# Precondition
#  - Only support a bio token - BIO-SEAL


def _login_biotoken_certificate(pw):

    # 1. 바이오토큰 click
    if not auto_click(resmgr.get('certificate_login_bio_token.png'), timeout=60):
        log().error("Failed to find 바이오토큰 image")
        return False

    # 2. 제조사/모델명 선택
    success = auto_click(resmgr.get('certificate_login_bio_token_bio_seal.png'), timeout=3) \
        or auto_click(resmgr.get('certificate_login_bio_token_bio_seal(selected).png'), timeout=3)
    if not success:
        log().error("Failed to find BIO-SEAL 바이오 보안토큰")
        return False

    # 3. 확인버튼
    if not auto_click(resmgr.get('certificate_login_bio_token_device_name_selection_confirm_button.png')):
        log().error("Failed to find 확인버튼")
        return False

    # BIO보안토큰 Window
    # 4. password 입력
    if not auto_type(resmgr.get('certificate_login_bio_token_password_input.png'), pw):
        log().error("Failed to find password input box")
        return False

    # 5. 확인버튼
    if not auto_click(resmgr.get('certificate_login_bio_token_password_confirm_button.png')):
        log().error("Failed to find 바이오토큰 확인 버튼")
        return False

     # "제조사/모델명 선택" 윈도우가 종료될때 까지 기다린다.
    if not wait_no_image(resmgr.get("certificate_bio_token_device_selection_program_installation_button.png"), timeout=60):
        log().error("Failed to wait 제조사/모델명 선택 closed.")
        return False

    # 인증서 확인 버튼
    if not auto_click(resmgr.get('certificate_password_confirm_button.png')):
        log().error("Failed to find confirm_button.")
        return False

    # "인증서 선택" 윈도우가 종료될때 까지 기다린다.
    if not wait_no_window("인증서 선택"):
        log().error("Failed to wait 인증서 선택.")
        return False

    return True

# Precondition
#  - login page
#  - biotoken's pin number is "00000000"


def _login_biotoken():
    pw = "00000000"

    if not auto_activate("나라장터: 국가종합전자조달 - SafeG2B", timeout=60):
        log().error("SAFEG2B Window is not Activated")
        return False

    if _is_login():
        log().info("Already logged in.")
        return True

    # 2. login button
    log().info("login) 2. 로그인 버튼 ")
    if not auto_click(resmgr.get('safeg2b_login_btn.png')):
        log().error("Failed to find 로그인 버튼")
        return False

    # 3. Certifiate Login
    if not _login_biotoken_certificate(pw):
        log().error("Failed to log in with a bio token.")
        return False

    # 7. Validate Login
    if not wait_image(resmgr.get('safeg2b_my_menu.png'), timeout=20):
        log().error("Failed to verify login result.")
        return False

    return True

# ----------------------------------------


# -------------------------------
# Execution APIs
# -------------------------------


def safeg2b_get_exe_filename():
    return "G2BLauncher.exe"


def safeg2b_get_exe_directory():
    return "C:\\WINDOWS\\pps\\SafeG2B"


def safeg2b_is_running():

    ss = str(subprocess.check_output('tasklist', shell=True))
    filename = safeg2b_get_exe_filename()
    return filename in ss


def safeg2b_run():
    if safeg2b_is_running():
        _log().info("SafeG2B is already running")
        return

    if not ctypes.windll.shell32.IsUserAnAdmin():
        _log().info("Need privileged permission. Elevate.")
        elevate.elevate(show_console=False)

    filename = safeg2b_get_exe_filename()
    directory = safeg2b_get_exe_directory()
    _log().info("Start SafeG2B.")
    os.system(f"cd {directory} && start {os.path.join(directory, filename)}")

# -------------------------------


def safeg2b_get_window_title():
    return "나라장터: 국가종합전자조달 - SafeG2B"


def safeg2b_get_main_window_until(timeout=60):
    window_title = safeg2b_get_window_title()
    return auto.windows.window_wait_until(window_title, timeout=timeout)


# ---------------------------
# Common APIs
# ---------------------------

def safeg2b_window_message_get_title():
    return "Message: 나라장터 - SafeG2B"


def safeg2b_window_message_confirm():
    title = safeg2b_window_message_get_title()
    if not auto_activate(title, timeout=__default_timeout):
        raise Exception(f"{title} Window is not Activated")
    auto.windows.img_click(resmgr.get(
        'safeg2b_message_confirm_button.png'), timeout=__default_timeout)

# ---------------------------
# Log In APIs
# ---------------------------


# ---------------------------
# Participation APIs
# ---------------------------


def safeg2b_participate_2_4_bid_participate():
    auto.windows.window_select("물품공고분류조회 - SafeG2B")
    auto.windows.img_click(resmgr.get(
        "safeg2b_2_4_bid_button.png"), timeout=__default_timeout)


def safeg2b_participate_2_5_bid_notice():
    title = "투찰 공지사항 - SafeG2B"
    if not auto_activate(title, timeout=__default_timeout):
        log().error(f"A Window is not Activated. title={title}")
        return False

    # After bring a window to top, It takes not niggrigible time.
    auto.windows.wait_until_image(resmgr.get(
        "safeg2b_2_5_bid_notice_title_image.png"), timeout=__default_timeout)
    pyautogui.press("end")
    auto.windows.wait_until_image(resmgr.get(
        "safeg2b_2_5_bid_notice_yes_checkbox.png"), timeout=__default_timeout)

    yes_buttons = auto.windows.img_find_all(
        resmgr.get("safeg2b_2_5_bid_notice_yes_checkbox.png"))
    for btn in yes_buttons:
        auto.windows.click(*btn)

    auto.windows.img_click(resmgr.get(
        'safeg2b_2_5_bid_notice_confirm_button.png'))

    return True


def safeg2b_participate_2_6_bid_doc(price):
    title = "물품구매입찰서:나라장터 - SafeG2B"
    auto_activate(title)

    # click buttons
    auto.windows.img_click(resmgr.get(
        "safeg2b_2_6_bid_doc_checkbox.png"), timeout=__default_timeout)
    auto.windows.img_type(resmgr.get(
        "safeg2b_2_6_bid_doc_cost_input.png"), price, timeout=__default_timeout)

    # scroll down to end
    auto_go_bottom(title)

    # click buttons
    auto.windows.img_click(resmgr.get(
        "safeg2b_2_6_bid_doc_checkbox.png"), timeout=__default_timeout)
    auto.windows.img_click(resmgr.get("safeg2b_2_6_bid_doc_send_button.png"))


def safeg2b_participate_2_7_bid_price_confirmation():
    auto_activate("투찰금액 확인 - SafeG2B", timeout=__default_timeout)

    auto.windows.img_click(resmgr.get(
        'safeg2b_2_7_cost_confirm_checkbox.png'), timeout=__default_timeout)

    auto.windows.img_click(resmgr.get(
        'safeg2b_2_7_cost_confirm_button.png'), timeout=__default_timeout)


def safeg2b_participate_2_8_bid_lottery_number():
    # 추첨번호 선택
    auto_activate("추첨번호 선택 - SafeG2B", timeout=__default_timeout)

    # wait for checkboxes
    auto.windows.img_wait_until(resmgr.get(
        "safeg2b_2_8_lottery_number_checkbox.png"), timeout=__default_timeout)

    # find all checkboxes
    boxes = auto.windows.img_find_all(resmgr.get(
        "safeg2b_2_8_lottery_number_checkbox.png"))
    boxes = random.sample(boxes, 2)
    for box in boxes:
        _log().debug(f"click a check button. box id={box}")
        auto.windows.click(*box)

    # click buttons
    auto.windows.img_click(resmgr.get(
        'safeg2b_2_8_lottery_number_send_button.png'))
    # Issue: 아래 2개의 img가 비슷하여 2번 click되는 효과가 생긴다. 중간에 잠시 시간을 준다.
    auto.windows.img_click(resmgr.get(
        'safeg2b_2_8_lottery_number_confirm_button.png'), timeout=__default_timeout)
    # TODO: 특징있는 image를 기다리도록 변경하자.
    auto.windows.img_wait_until(resmgr.get(
        'safeg2b_2_8_lottery_number_popup_characteristic.png'), timeout=__default_timeout)
    auto.windows.img_click(resmgr.get(
        'safeg2b_2_8_lottery_number_certi_confrim_button.png'), confidence=0.8)


def safeg2b_participate_2_9_certificate(pw):
    org.g2b.certificate.cert_personal_user_login(pw)


def safeg2b_participate_2_10_alert_confirm():
    auto_activate("나라장터")
    # auto.windows.window_select("나라장터")
    auto.windows.img_click(resmgr.get(
        'safeg2b_2_9_confirm_button.png'), timeout=__default_timeout)


def safeg2b_participate_2_11_history_check():
    auto_activate("전자입찰 송수신상세이력조회 - SafeG2B", timeout=__default_timeout)
    auto.windows.img_click(resmgr.get(
        'safeg2b_2_10_close_button.png'), timeout=__default_timeout)


def safeg2b_participate_2_12_survery():
    # 2.11 나라장터 행정정보 제3자 제공서비스 수요조사 - SafeG2B
    auto_activate("나라장터 행정정보 제3자 제공서비스 수요조사 - SafeG2B",
                  timeout=__default_timeout)
    auto.windows.img_click(resmgr.get(
        'safeg2b_2_11_survey_close_button.png'), timeout=__default_timeout)


def safeg2b_participate(notice_no: str, price: str):
    if not auto_activate(safeg2b_get_window_title(), timeout=__default_timeout):
        _log().error("SAFEG2B Window is not Activated")
        return False

    _log().info("2.1 bid_info (New Page)")
    auto.windows.img_click(resmgr.get(
        'safeg2b_bid_bid_info_button.png'), timeout=__default_timeout)

    _log().info("2.2 search ")
    auto.windows.img_type(resmgr.get(
        'safeg2b_bid_search_input.png'), notice_no, timeout=__default_timeout)
    auto.windows.img_click(resmgr.get(
        'safeg2b_bid_search_button.png'), timeout=__default_timeout)

    _log().info("2.3 bid participate")
    if not auto_activate(safeg2b_get_window_title()):
        _log().error("SAFEG2B Window is not Activated")
        return False

    auto.windows.img_click(resmgr.get(
        "safeg2b_2_3_bid_finger_print_button.png"), timeout=__default_timeout)

    _log().info("2.4 bid participate(2)")
    safeg2b_participate_2_4_bid_participate()

    _log().info("2.5 투찰 공지사항")
    if not safeg2b_participate_2_5_bid_notice():
        _log().error("Failed to proceed 투찰 공지사항. 물품등록이 안되었거나, 등록기한이 지난경우일 가능성이 있습니다.")
        return False

    _log().info("2.6 물품구매입찰서")
    safeg2b_participate_2_6_bid_doc(price)

    _log().info("2.7 투찰금액확인")
    safeg2b_participate_2_7_bid_price_confirmation()

    _log().info("2.8 추첨번호 선택")
    safeg2b_participate_2_8_bid_lottery_number()

    # _log().info("2.9 인증서 ")
    # safeg2b_participate_2_9_certificate(pw)

    _log().info("2.10 알림 확인")
    safeg2b_participate_2_10_alert_confirm()

    _log().info("2.11 전자입찰 송수신상세이력조회 - SafeG2B")
    safeg2b_participate_2_11_history_check()

    # Optional
    # _log().info("2.11 나라장터 행정정보 제3자 제공서비스 수요조사 - SafeG2B")
    # safeg2b_participate_2_12_survery()


def safeg2b_initialize():
    if not auto_activate(safeg2b_get_window_title(), timeout=100):
        raise Exception("SAFEG2B Window is not Activated")
    _go_to_login_page()


def safeg2b_close() -> bool:
    title = safeg2b_get_window_title()
    hwnd = auto.windows.window_find_exact(title)
    _log().info(f"Close SafeG2B window={hwnd}")
    return auto.windows.window_close(hwnd)


def safeg2b_login_validate():
    pos = auto.windows.img_wait_until(resmgr.get(
        "safeg2b_login_my_bid_center.png"), timeout=__default_timeout)
    return False if pos is None else True


class SafeG2B:
    def __init__(self, *, close_windows=True):
        self.__close_windows = close_windows

        # safe g2b
        safeg2b_run()
        safeg2b_initialize()
        if not _login_biotoken():
            raise Exception("Failed to login to safeg2b")

    def __del__(self):
        if self.__close_windows:
            safeg2b_close()

    def participate(self, bid):
        _log().info(f"participate in {bid.number} price={bid.price}")
        if not safeg2b_is_running():
            return False, "safeg2b instance is not running"
        return safeg2b_participate(bid.number, str(bid.price)), None


if __name__ == '__main__':
    # from account import account_get
    # pw = account_get("g2b", "pw")
    # rn = account_get("g2b", "rn")

    # notice_number = "20220435053"
    # price = "10083150"

    # safeg2b_initialize()
    # safeg2b_login( pw, rn)

    # # TODO: Too fast to participate in
    # time.sleep(5)
    # safeg2b_participate( pw, notice_number, price)

    # test_validate_login()
    pass
