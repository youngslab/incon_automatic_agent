
import os, sys, time, random
sys.path.insert(1, 'C:\\Users\\Jaeyoung\\dev\\incon_project')

import auto.windows
import pyautogui
import win32gui, win32con, win32api, win32process

def safeg2b_get_window_title():
    return "나라장터: 국가종합전자조달 - SafeG2B"

def safeg2b_get_executable_path():
    return "C:\\Windows\\pps\\SafeG2B\\"

def safeg2b_main_window_wait_until(timeout=30):
    window_title = safeg2b_get_window_title()
    return auto.windows.window_wait_until(window_title, timeout=timeout)

def safeg2b_launch():
    # Check it already runs
    title = safeg2b_get_window_title()
    hwnd = auto.windows.window_wait_until(title)
    print(f"hwnd={hwnd}")
    if hwnd:
        return

    # Run    
    os.chdir(safeg2b_get_executable_path())
    # TODO: Deal with UAC.
    os.system("START G2BLauncher.exe")

# ---------------------------
# Common APIs
# ---------------------------

def safeg2b_window_message_get_title():
    return "Message: 나라장터 - SafeG2B"

def safeg2b_window_message_confirm(resmgr):
    title = safeg2b_window_message_get_title()
    hwnd = auto.windows.window_wait_until(title, timeout=30)
    auto.windows.bring_window_to_top(hwnd)
    auto.windows.img_click(resmgr.get('safeg2b_message_confirm_button.png'), timeout=30)

# ---------------------------
# Log In APIs
# ---------------------------

def safeg2b_go_to_login_page(resmgr):
    try:
        auto.windows.img_click(resmgr.get('safeg2b_0_etc_homepage.png'))
    except Exception as _:
        pass

def safeg2b_is_login(resmgr):
    # Wait until 15sec to check the login state.
    pos = auto.windows.img_wait_until(resmgr.get('safeg2b_login_btn.png'), grayscale=False, confidence=0.8, timeout=15)
    return True if pos is None else False

def safeg2b_certificate_login(resmgr, pw):
    import certificate
    certificate.cert_login(resmgr, pw)
 
def safeg2b_login(resmgr, pw:str, id):
    handle = safeg2b_main_window_wait_until()
    auto.windows.bring_window_to_top(handle)

    # 1. check box
    auto.windows.img_click(resmgr.get('safeg2b_finger_print_exception_checkbox.png'), timeout=10)
    
    # 2. login button
    auto.windows.img_click(resmgr.get('safeg2b_login_btn.png'))

    # 3. waiting for the page movement and then click
    auto.windows.img_click(resmgr.get('safeg2b_finger_print_exception_confirm_button.png'), timeout=30)    
      
    # 4. 인증서 로그인
    safeg2b_certificate_login(resmgr, pw)

    # 6. Waiting for the id page
    auto.windows.bring_window_to_top(handle)

    # 7. Focus input for id and type
    auto.windows.img_type(resmgr.get('safeg2b_id_front_number_input.png'), f"{id.split('-')[0]}{id.split('-')[1]}" , timeout=30)
    # when second part got focused automatically, the image going to be changed so that it is hightlighted.
    # auto.windows.img_type(resmgr.get('safeg2b_id_back_number_input.png'), id.split('-')[1])
    auto.windows.img_click(resmgr.get('safeg2b_id_confirm_button.png'), timeout=5)
    
    # 9. 인증서 로그인(개인)
    safeg2b_certificate_login(resmgr, pw)

    # 10. 메세지 확인 - 예외 적용자 로그인
    safeg2b_window_message_confirm(resmgr)

# ---------------------------
# Participation APIs
# ---------------------------

def safeg2b_participate_2_4_bid_participate(resmgr):
    auto.windows.window_select("물품공고분류조회 - SafeG2B")
    auto.windows.img_click(resmgr.get("safeg2b_2_4_bid_button.png"), timeout=5)

def safeg2b_participate_2_5_bid_notice(resmgr):
    notice_hwnd = auto.windows.window_wait_until("투찰 공지사항 - SafeG2B")
    auto.windows.bring_window_to_top(notice_hwnd)

    pyautogui.press("end")
    auto.windows.wait_until_image(resmgr.get("safeg2b_2_5_bid_notice_yes_checkbox.png"), timeout=5)
    
    yes_buttons = auto.windows.img_find_all(resmgr.get("safeg2b_2_5_bid_notice_yes_checkbox.png"))
    for btn in yes_buttons:
        auto.windows.click(*btn)

    auto.windows.img_click(resmgr.get('safeg2b_2_5_bid_notice_confirm_button.png'))

def safeg2b_participate_2_6_bid_doc(resmgr, price):
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

def safeg2b_participate_2_7_bid_price_confirmation(resmgr): 
    auto.windows.window_select("투찰금액 확인 - SafeG2B")
    auto.windows.img_click(resmgr.get('safeg2b_2_7_cost_confirm_checkbox.png'), timeout=5)
    auto.windows.img_click(resmgr.get('safeg2b_2_7_cost_confirm_button.png'))

def safeg2b_participate_2_8_bid_lottery_number(resmgr):
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
    auto.windows.img_click(resmgr.get('safeg2b_2_8_lottery_number_confirm_button.png'), timeout=5)
    auto.windows.img_click(resmgr.get('safeg2b_2_8_lottery_number_certi_confrim_button.png'), timeout=5)

def safeg2b_participate_2_9_certificate(resmgr, pw):
    safeg2b_certificate_login(resmgr, pw)

def safeg2b_participate_2_10_alert_confirm(resmgr):
    auto.windows.window_select("나라장터")
    auto.windows.img_click(resmgr.get('safeg2b_2_9_confirm_button.png'),timeout=5)

def safeg2b_participate_2_11_history_check(resmgr):
    auto.windows.window_select("전자입찰 송수신상세이력조회 - SafeG2B")
    auto.windows.img_click(resmgr.get('safeg2b_2_10_close_button.png'), timeout=5)

def safeg2b_participate_2_12_survery(resmgr):
    # 2.11 나라장터 행정정보 제3자 제공서비스 수요조사 - SafeG2B
    auto.windows.window_select("나라장터 행정정보 제3자 제공서비스 수요조사 - SafeG2B")
    auto.windows.img_click(resmgr.get('safeg2b_2_11_survey_close_button.png'), timeout=5)

def safeg2b_participate( resmgr, pw, notice_no, price):
    handle = safeg2b_main_window_wait_until()
    auto.windows.bring_window_to_top(handle)
    
    print("2.1 bid_info (New Page)")
    auto.windows.img_click(resmgr.get('safeg2b_bid_bid_info_button.png'), timeout=30)

    print("2.2 search ")
    auto.windows.img_type(resmgr.get('safeg2b_bid_search_input.png'), notice_no, timeout=30)
    auto.windows.img_click(resmgr.get('safeg2b_bid_search_button.png'), timeout=5)

    print("2.3 bid participate")
    auto.windows.bring_window_to_top(handle)
    auto.windows.img_click(resmgr.get("safeg2b_2_3_bid_finger_print_button.png"), timeout=30)

    print("2.4 bid participate(2)")
    safeg2b_participate_2_4_bid_participate(resmgr)

    print("2.5 투찰 공지사항")
    safeg2b_participate_2_5_bid_notice(resmgr)

    print("2.6 물품구매입찰서")
    safeg2b_participate_2_6_bid_doc(resmgr, price)

    print("2.7 투찰금액확인")
    safeg2b_participate_2_7_bid_price_confirmation(resmgr)

    print("2.8 추첨번호 선택")
    safeg2b_participate_2_8_bid_lottery_number(resmgr)

    print("2.9 인증서 ")
    safeg2b_participate_2_9_certificate(resmgr, pw)

    print("2.10 알림 확인")
    safeg2b_participate_2_10_alert_confirm(resmgr)

    print("2.11 전자입찰 송수신상세이력조회 - SafeG2B")
    safeg2b_participate_2_11_history_check(resmgr)

    # Optional 
    # print("2.11 나라장터 행정정보 제3자 제공서비스 수요조사 - SafeG2B")
    # safeg2b_participate_2_12_survery(resmgr)


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


    from incon_automatic_agent.res.resource_manager import resource_manager
    resmgr = resource_manager()

    notice_number = "20220435053"
    price = "10083150"

    # TODO: check window handle exsis, if not, download it.    

    handle = safeg2b_main_window_wait_until()
    auto.windows.bring_window_to_top(handle)

    # timeout... just go to loging page if possible
    safeg2b_go_to_login_page(resmgr)

    if not safeg2b_is_login(resmgr):
        safeg2b_login(resmgr, pw, resident_number)

    # TODO: Too fast to participate in
    time.sleep(5)
    safeg2b_participate(resmgr, pw, notice_number, price)

    # Normalize window size 
    # safeg2b_make_window_size()

    # Login
    # safeg2b_login()
  


    # launch_safeg2b()
    # handle = wait_until_safeg2b_handle(60)

    # need to elevate
    # from elevate import elevate
    # elevate()

    # print('before')
    # print(win32gui.GetWindowRect(handle))

    # 이상적인 size: (0,0, 1000, xxx)

    

    # x0, y0, x1, y1 = win32gui.GetWindowRect(handle)
    # w = x1 - x0
    # h = y1 - y0
    # win32gui.MoveWindow(handle, x0, y0, w+100, h+100, True)

    # print('after')
    # print(win32gui.GetWindowRect(handle))
