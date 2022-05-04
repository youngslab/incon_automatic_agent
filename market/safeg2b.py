
import os, sys, time, random
import auto.windows
import pyautogui
import win32gui, win32con, win32api, win32process

import market.certificate
from res.resource_manager import resource_manager as resmgr

def __logger():
    import logging
    return logging.getLogger(__name__)

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
    hwnd = auto.windows.window_wait_until(title, timeout=30)
    auto.windows.bring_window_to_top(hwnd)
    auto.windows.img_click(resmgr.get('safeg2b_message_confirm_button.png'), timeout=30)

# ---------------------------
# Log In APIs
# ---------------------------

def safeg2b_go_to_login_page():
    try:
        auto.windows.img_click(resmgr.get('safeg2b_0_etc_homepage.png'))
    except Exception as _:
        pass

def safeg2b_is_login():
    # Wait until 15sec to check the login state.
    pos = auto.windows.img_wait_until(resmgr.get('safeg2b_login_btn.png'), grayscale=False, confidence=0.8, timeout=15)
    return True if pos is None else False

def safeg2b_certificate_login( pw):    
    market.certificate.cert_login( pw)
 
def safeg2b_login( pw:str, id):
    if safeg2b_is_login():
        __logger().info("Already logged in.")
        return

    handle = safeg2b_get_main_window_until()
    auto.windows.bring_window_to_top(handle)

    # 1. check box
    __logger().info("1.1 지문 예외 check box ")
    auto.windows.img_click(resmgr.get('safeg2b_finger_print_exception_checkbox.png'), timeout=10)
    
    # 2. login button
    __logger().info("1.2 로그인 버튼 ")
    auto.windows.img_click(resmgr.get('safeg2b_login_btn.png'))

    # 3. waiting for the page movement and then click
    __logger().info("1.3 지문 예외 확인 ")
    auto.windows.img_click(resmgr.get('safeg2b_finger_print_exception_confirm_button.png'), timeout=30)
      
    # 4. 인증서 로그인
    __logger().info("1.4 인증서 로그인")
    safeg2b_certificate_login( pw)

    __logger().info("1.5 주민번호 입력")
    # 6. Waiting for the id page
    auto.windows.bring_window_to_top(handle)
    # 7. Focus input for id and type
    auto.windows.img_type(resmgr.get('safeg2b_id_front_number_input.png'), f"{id.split('-')[0]}{id.split('-')[1]}" , timeout=30)
    # when second part got focused automatically, the image going to be changed so that it is hightlighted.
    # auto.windows.img_type(resmgr.get('safeg2b_id_back_number_input.png'), id.split('-')[1])
    auto.windows.img_click(resmgr.get('safeg2b_id_confirm_button.png'), timeout=5)
    
    # 9. 인증서 로그인(개인)
    # market.certificate.cert_personal_user_login(pw)
    __logger().info("1.6 인증서 로그인")
    safeg2b_certificate_login( pw)

    # 10. 메세지 확인 - 예외 적용자 로그인
    __logger().info("1.7 메세지 확인 - 예외 적용자 로그인")
    safeg2b_window_message_confirm()

# ---------------------------
# Participation APIs
# ---------------------------

def safeg2b_participate_2_4_bid_participate():
    auto.windows.window_select("물품공고분류조회 - SafeG2B")
    auto.windows.img_click(resmgr.get("safeg2b_2_4_bid_button.png"), timeout=5)

def safeg2b_participate_2_5_bid_notice():
    notice_hwnd = auto.windows.window_wait_until("투찰 공지사항 - SafeG2B")
    auto.windows.bring_window_to_top(notice_hwnd)

    # After bring a window to top, It takes not niggrigible time. 
    auto.windows.wait_until_image(resmgr.get("safeg2b_2_5_bid_notice_title_image.png"), timeout=5)
    pyautogui.press("end")
    auto.windows.wait_until_image(resmgr.get("safeg2b_2_5_bid_notice_yes_checkbox.png"), timeout=5)
    
    yes_buttons = auto.windows.img_find_all(resmgr.get("safeg2b_2_5_bid_notice_yes_checkbox.png"))
    for btn in yes_buttons:
        auto.windows.click(*btn)

    auto.windows.img_click(resmgr.get('safeg2b_2_5_bid_notice_confirm_button.png'))

def safeg2b_participate_2_6_bid_doc( price):
    hwnd = auto.windows.window_select("물품구매입찰서:나라장터 - SafeG2B")

    # click buttons
    auto.windows.img_click(resmgr.get("safeg2b_2_6_bid_doc_checkbox.png"), timeout=5)
    auto.windows.img_type(resmgr.get("safeg2b_2_6_bid_doc_cost_input.png"), price,timeout=10)
    
    # make the input above out of focus - click center of the window.
    # TODO: Find more efficient or reasonable way    
    cp = auto.windows.window_get_center(hwnd)
    auto.windows.mouse_move(*cp)
    auto.windows.mouse_click()

    # scroll to the end
    pyautogui.press('end')    

    # click buttons
    auto.windows.img_click(resmgr.get("safeg2b_2_6_bid_doc_checkbox.png"), timeout=5)
    auto.windows.img_click(resmgr.get("safeg2b_2_6_bid_doc_send_button.png"))

def safeg2b_participate_2_7_bid_price_confirmation(): 
    auto.windows.window_select("투찰금액 확인 - SafeG2B")
    auto.windows.img_click(resmgr.get('safeg2b_2_7_cost_confirm_checkbox.png'), timeout=5)
    auto.windows.img_click(resmgr.get('safeg2b_2_7_cost_confirm_button.png'))

def safeg2b_participate_2_8_bid_lottery_number():
    # 추첨번호 선택
    auto.windows.window_select("추첨번호 선택 - SafeG2B")

    # wait for checkboxes
    auto.windows.img_wait_until(resmgr.get("safeg2b_2_8_lottery_number_checkbox.png"), timeout=10)

    # find all checkboxes
    boxes = auto.windows.img_find_all(resmgr.get("safeg2b_2_8_lottery_number_checkbox.png"))    
    boxes = random.choices(boxes, k=2)
    for box in boxes:
        auto.windows.click(*box)

    # click buttons
    auto.windows.img_click(resmgr.get('safeg2b_2_8_lottery_number_send_button.png'))
    # Issue: 아래 2개의 img가 비슷하여 2번 click되는 효과가 생긴다. 중간에 잠시 시간을 준다.
    auto.windows.img_click(resmgr.get('safeg2b_2_8_lottery_number_confirm_button.png'), timeout=5)
    # TODO: 특징있는 image를 기다리도록 변경하자.
    auto.windows.img_wait_until(resmgr.get('safeg2b_2_8_lottery_number_popup_characteristic.png'), timeout=5)
    auto.windows.img_click(resmgr.get('safeg2b_2_8_lottery_number_certi_confrim_button.png'), confidence=0.8)

def safeg2b_participate_2_9_certificate( pw):
    market.certificate.cert_personal_user_login( pw)

def safeg2b_participate_2_10_alert_confirm():
    auto.windows.window_select("나라장터")
    auto.windows.img_click(resmgr.get('safeg2b_2_9_confirm_button.png'),timeout=5)

def safeg2b_participate_2_11_history_check():
    auto.windows.window_select("전자입찰 송수신상세이력조회 - SafeG2B")
    auto.windows.img_click(resmgr.get('safeg2b_2_10_close_button.png'), timeout=5)

def safeg2b_participate_2_12_survery():
    # 2.11 나라장터 행정정보 제3자 제공서비스 수요조사 - SafeG2B
    auto.windows.window_select("나라장터 행정정보 제3자 제공서비스 수요조사 - SafeG2B")
    auto.windows.img_click(resmgr.get('safeg2b_2_11_survey_close_button.png'), timeout=5)

def safeg2b_participate(  pw, notice_no:str, price:str):
    handle = safeg2b_get_main_window_until()
    auto.windows.bring_window_to_top(handle)
    
    __logger().info("2.1 bid_info (New Page)")
    auto.windows.img_click(resmgr.get('safeg2b_bid_bid_info_button.png'), timeout=30)

    __logger().info("2.2 search ")
    auto.windows.img_type(resmgr.get('safeg2b_bid_search_input.png'), notice_no, timeout=30)
    auto.windows.img_click(resmgr.get('safeg2b_bid_search_button.png'), timeout=5)

    __logger().info("2.3 bid participate")
    auto.windows.bring_window_to_top(handle)
    auto.windows.img_click(resmgr.get("safeg2b_2_3_bid_finger_print_button.png"), timeout=30)

    __logger().info("2.4 bid participate(2)")
    safeg2b_participate_2_4_bid_participate()

    __logger().info("2.5 투찰 공지사항")
    safeg2b_participate_2_5_bid_notice()

    __logger().info("2.6 물품구매입찰서")
    safeg2b_participate_2_6_bid_doc( price)

    __logger().info("2.7 투찰금액확인")
    safeg2b_participate_2_7_bid_price_confirmation()

    __logger().info("2.8 추첨번호 선택")
    safeg2b_participate_2_8_bid_lottery_number()

    __logger().info("2.9 인증서 ")
    safeg2b_participate_2_9_certificate( pw)

    __logger().info("2.10 알림 확인")
    safeg2b_participate_2_10_alert_confirm()

    __logger().info("2.11 전자입찰 송수신상세이력조회 - SafeG2B")
    safeg2b_participate_2_11_history_check()

    # Optional 
    # __logger().info("2.11 나라장터 행정정보 제3자 제공서비스 수요조사 - SafeG2B")
    # safeg2b_participate_2_12_survery()

def safeg2b_initialize():    
    handle = safeg2b_get_main_window_until()
    auto.windows.bring_window_to_top(handle)

    safeg2b_go_to_login_page()


def safeg2b_close() -> bool:
    title = safeg2b_get_window_title()
    hwnd = auto.windows.window_find_exact(title)
    __logger().info(f"Close SafeG2B window={hwnd}")
    return auto.windows.window_close(hwnd)

if __name__  == '__main__':

    # load account info of the Incon
    pw = ''
    resident_number = ''
    import json
    path = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(path, ".g2b.json")
    with open(filepath, 'r')  as f:
        x = json.loads(f.read())
        pw = x['pw']
        resident_number = x['rn']

    print(f"pw={pw}, rn={resident_number}")

    notice_number = "20220435053"
    price = "10083150"

    safeg2b_initialize()
    safeg2b_login( pw, resident_number)

    # TODO: Too fast to participate in
    time.sleep(5)
    safeg2b_participate( pw, notice_number, price)

   
