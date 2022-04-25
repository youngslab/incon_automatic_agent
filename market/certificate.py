

from auto.windows import *

def cert_login(resmgr, pw:str) -> bool:
    cert_hwnd = window_wait_until("인증서 선택", timeout=30)
    if cert_hwnd is None:
        return False
    bring_window_to_top(cert_hwnd)
    img_type(resmgr.get('certificate_password_input.png'), pw, timeout=10)
    img_click(resmgr.get('certificate_password_confirm_button.png'))
    return True