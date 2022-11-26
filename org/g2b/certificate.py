

from multiprocessing.connection import wait
from auto.windows import *

from org.g2b.res import resmgr
from auto import *


def cert_login(pw: str) -> bool:
    cert_hwnd = window_wait_until("인증서 선택", timeout=30)
    if cert_hwnd is None:
        return False
    bring_window_to_top(cert_hwnd)
    img_type(resmgr.get('certificate_password_input.png'), pw, timeout=10)
    img_click(resmgr.get('certificate_password_confirm_button.png'))
    return True


def cert_is_personal_user_enabled():
    img = img_wait_until(resmgr.get('certificate_personal_user_enabled.png'))
    return True if img else False


def cert_personal_user_login(pw: str):
    try:
        img_click(resmgr.get('certificate_personal_user_disabled.png'), timeout=1)
    except:
        pass
    cert_login(pw)

def cert_login_with_biotoken(pw):

    # 1. 바이오토큰 click
    # XXX: 바이오토큰과 유사한 보안토큰이 선택되는 경우가 있다. 이에 confidence를 변경 0.9->0.95.
    if not auto_click(resmgr.get('certificate_login_bio_token.png'), timeout=60, confidence=0.95):
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
    autoit.win_wait("BIO보안토큰")

    if not auto_type(resmgr.get('certificate_login_bio_token_password_input.png'), pw):
        log().error("Failed to find password input box")
        return False

    # 5. 확인버튼
    if not auto_click(resmgr.get('certificate_login_bio_token_password_confirm_button.png')):
        log().error("Failed to find 바이오토큰 확인 버튼")
        return False

    # XX -> "제조사/모델명 선택" 윈도우가 종료될때 까지 기다린다.
    # 이 창은 닫힌 상태에도 계속 존재하는 것을 나온다.
    # if not wait_no_window("제조사/모델명 선택", timeout=120):
        # if not wait_no_image(resmgr.get("certificate_bio_token_device_selection_program_installation_button.png"), timeout=60):
        # log().error("Failed to wait 제조사/모델명 선택 closed.")
        # return False
    try:
        autoit.win_wait_active("인증서 선택")
    except:
        log().error("Failed to login with finger print.")
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

if __name__ == "__main__":
    print(cert_is_personal_user_enabled())
    # img_click(resmgr.get('certificate_personal_user_disabled.png'))
    # cert_personal_user_login(resmgr.get_account("g2b","pw"))
