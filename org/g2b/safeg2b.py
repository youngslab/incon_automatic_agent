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


def _logger():
    import logging
    return logging.getLogger(__name__)

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
        _logger().info("SafeG2B is already running")
        return

    if not ctypes.windll.shell32.IsUserAnAdmin():
        _logger().info("Need privileged permission. Elevate.")
        elevate.elevate(show_console=False)

    filename = safeg2b_get_exe_filename()
    directory = safeg2b_get_exe_directory()
    _logger().info("Start SafeG2B.")
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


def safeg2b_go_to_login_page():
    try:
        _logger().info("try to go home.")
        auto.windows.img_click(resmgr.get('safeg2b_0_etc_homepage.png'))
    except Exception as _:
        _logger().info("Can't go home. But it's ok. That means it's already at home")
        pass


def safeg2b_is_login():
    # Wait until 15sec to check the login state.
    pos = auto.windows.img_wait_until(resmgr.get(
        'safeg2b_login_btn.png'), grayscale=False, confidence=0.8, timeout=15)
    return True if pos is None else False


def safeg2b_certificate_login(pw):
    org.g2b.certificate.cert_login(pw)


def safeg2b_login(pw: str, id):
    if safeg2b_is_login():
        _logger().info("Already logged in.")
        return

    if not auto_activate(safeg2b_get_window_title()):
        raise Exception("SAFEG2B Window is not Activated")

    # login)  check box
    _logger().info("login) 1. 지문 예외 check box ")
    auto.windows.img_click(resmgr.get(
        'safeg2b_finger_print_exception_checkbox.png'), timeout=__default_timeout)

    # 2. login button
    _logger().info("login) 2. 로그인 버튼 ")
    auto.windows.img_click(resmgr.get('safeg2b_login_btn.png'))

    # 3. waiting for the page movement and then click
    _logger().info("login) 3. 지문 예외 확인 ")
    auto.windows.img_click(resmgr.get(
        'safeg2b_finger_print_exception_confirm_button.png'), timeout=__default_timeout)

    # 4. 인증서 로그인
    _logger().info("login) 4. 인증서 로그인")
    safeg2b_certificate_login(pw)

    _logger().info("login) 5. 주민번호 입력")

    # 6. Waiting for the id page
    # auto.windows.bring_window_to_top(handle)
    if not auto_activate(safeg2b_get_window_title()):
        raise Exception("SAFEG2B Window is not Activated")

    # 7. Focus input for id and type
    auto.windows.img_type(resmgr.get('safeg2b_id_front_number_input.png'),
                          f"{id.split('-')[0]}{id.split('-')[1]}", timeout=__default_timeout)
    # when second part got focused automatically, the image going to be changed so that it is hightlighted.
    # auto.windows.img_type(resmgr.get('safeg2b_id_back_number_input.png'), id.split('-')[1])
    auto.windows.img_click(resmgr.get(
        'safeg2b_id_confirm_button.png'), timeout=__default_timeout)

    # 9. 인증서 로그인(개인)
    # market.certificate.cert_personal_user_login(pw)
    _logger().info("login) 6. 인증서 로그인")
    safeg2b_certificate_login(pw)

    # 10. 메세지 확인 - 예외 적용자 로그인
    _logger().info("login) 7. 메세지 확인 - 예외 적용자 로그인")
    safeg2b_window_message_confirm()

    _logger().info("login) 8. 로그인 확인 - MY BID CENTER")
    success = safeg2b_login_validate()
    if not success:
        _logger().error("Failed to login safeg2b")
    return success

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
        raise Exception(f"A Window is not Activated. title={title}")

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
        _logger().debug(f"click a check button. box id={box}")
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
    auto.windows.window_select("나라장터")
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
        raise Exception("SAFEG2B Window is not Activated")

    _logger().info("2.1 bid_info (New Page)")
    auto.windows.img_click(resmgr.get(
        'safeg2b_bid_bid_info_button.png'), timeout=__default_timeout)

    _logger().info("2.2 search ")
    auto.windows.img_type(resmgr.get(
        'safeg2b_bid_search_input.png'), notice_no, timeout=__default_timeout)
    auto.windows.img_click(resmgr.get(
        'safeg2b_bid_search_button.png'), timeout=__default_timeout)

    _logger().info("2.3 bid participate")
    if not auto_activate(safeg2b_get_window_title()):
        raise Exception("SAFEG2B Window is not Activated")
    auto.windows.img_click(resmgr.get(
        "safeg2b_2_3_bid_finger_print_button.png"), timeout=__default_timeout)

    _logger().info("2.4 bid participate(2)")
    safeg2b_participate_2_4_bid_participate()

    _logger().info("2.5 투찰 공지사항")
    safeg2b_participate_2_5_bid_notice()

    _logger().info("2.6 물품구매입찰서")
    safeg2b_participate_2_6_bid_doc(price)

    _logger().info("2.7 투찰금액확인")
    safeg2b_participate_2_7_bid_price_confirmation()

    _logger().info("2.8 추첨번호 선택")
    safeg2b_participate_2_8_bid_lottery_number()

    # _logger().info("2.9 인증서 ")
    # safeg2b_participate_2_9_certificate(pw)

    _logger().info("2.10 알림 확인")
    safeg2b_participate_2_10_alert_confirm()

    _logger().info("2.11 전자입찰 송수신상세이력조회 - SafeG2B")
    safeg2b_participate_2_11_history_check()

    # Optional
    # _logger().info("2.11 나라장터 행정정보 제3자 제공서비스 수요조사 - SafeG2B")
    # safeg2b_participate_2_12_survery()


def safeg2b_initialize():
    if not auto_activate(safeg2b_get_window_title(), timeout=100):
        raise Exception("SAFEG2B Window is not Activated")
    safeg2b_go_to_login_page()


def safeg2b_close() -> bool:
    title = safeg2b_get_window_title()
    hwnd = auto.windows.window_find_exact(title)
    _logger().info(f"Close SafeG2B window={hwnd}")
    return auto.windows.window_close(hwnd)


def safeg2b_login_validate():
    pos = auto.windows.img_wait_until(resmgr.get(
        "safeg2b_login_my_bid_center.png"), timeout=__default_timeout)
    return False if pos is None else True


def test_validate_login():

    print(safeg2b_login_validate())


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

    test_validate_login()
