

from multiprocessing.connection import wait
from auto.windows import *
from res.resource_manager import resource_manager as resmgr

def cert_login(pw:str) -> bool:
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

def cert_personal_user_login(pw:str):
    try:
        img_click(resmgr.get('certificate_personal_user_disabled.png'), timeout=1)
    except:
        pass
    cert_login(pw)
        
if __name__ == "__main__":
    print(cert_is_personal_user_enabled())
    # img_click(resmgr.get('certificate_personal_user_disabled.png'))
    # cert_personal_user_login(resmgr.get_account("g2b","pw"))
