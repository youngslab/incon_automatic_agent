
from selenium.webdriver.common.by import By
from org.g2b.safeg2b import *
from org.g2b import safeg2b

from integ_auto import Automatic


def log():
    import logging
    return logging.getLogger(__name__)


def _go_mypage(auto: Automatic):
    auto.go(
        'https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=/pt/menu/frameMypage.do')


def _do_in_main_frame(auto: Automatic, action):
    sub_frame = auto.get_element(By.ID, 'sub')
    if not sub_frame:
        log().error("Failed to find sub frame")
        return False

    with auto.get_frame(sub_frame):
        main_frame = auto.get_element(By.NAME, 'main')
        if not main_frame:
            log().error("Failed to find main frame")
            return False

        with auto.get_frame(main_frame):
            return action()


def _edit_mypage(auto: Automatic):

    def click_edit_button():
        # Edit Button
        if not auto.click(By.XPATH, '//*[@id="container"]/div[2]/div/a[1]'):
            log().error("Failed to find edit button")
            return False
        return True

    return _do_in_main_frame(auto, lambda: click_edit_button())


def _open_item_find_window(auto: Automatic):
    def click_search_button():
        # 검색 버튼
        if not auto.click(
                By.XPATH, '//*[@id="frm_addProd"]/div[3]/table/tbody/tr/td[1]/div/button'):
            return False
        return True

    return _do_in_main_frame(auto, lambda: click_search_button())


def _find_product(auto: Automatic, pn):
    title = "[팝업] 세부품명찾기: 나라장터"
    handle = auto.get_window_handle(title)
    if not handle:
        log().error(f"Failed to find window handle. title={title}")
        return False

    with auto.get_window(handle):
        # Product Number 입력
        if not auto.type(By.ID, 'detailPrdnmNo', pn):
            log().error(f"Failed to type product number. pn={pn}")
            return False

        # 검색 버튼
        if not auto.click(By.ID, 'bt_search'):
            log().error("Failed to click search button")
            return False

        # select item(첫번째 Item 클릭)
        if not auto.click(By.XPATH, '//*[@id="container"]/div[1]/table/tbody/tr/td[2]/a'):
            log().error("Failed to click 첫번째 아이템")
            return False

    return True


def _register_product(auto: Automatic):

    def click_register_button():
        if not auto.click(By.XPATH, '//*[@id="frm_addProd"]/div[2]/a'):
            log().error("Failed to click register button")
            return False
        if not auto.accept_alert():
            log().error("Failed to accpet alert")
            return False
        return True

    if not _do_in_main_frame(auto, lambda: click_register_button()):
        return False

    handle = auto.get_window_handle("Message: 나라장터")
    with auto.get_window(handle):
        if not auto.click(By.XPATH, '//*[@id="container3"]/div[2]/div/a'):
            log().error("Failed to click 확인 버튼")
            return False

    return True

# Go to the homepage to login


def go_homepage(auto: Automatic):
    auto.go('https://www.g2b.go.kr')
    return True


# Go to the page where we can register a new product
def go_product_registration_page(auto: Automatic):
    # go mypage
    _go_mypage(auto)

    # click edit button
    if not _edit_mypage(auto):
        log().error("Failed to edit mypage")
        return False

    return True


# Register a product
def register_product(auto: Automatic, pn):
    # open the window by clicking search button
    if not _open_item_find_window(auto):
        log().error("Failed to open itme find window")
        return False

    # move to the windows and input the product number
    if not _find_product(auto, pn):
        log().error("Failed to find a product.")
        return False

    # click register button and clear popup and confirm window
    if not _register_product(auto):
        log().error("Failed to register product.")
        return False

    return True


def get_registered_products(auto: Automatic):
    def get_product_names():
        items = auto.get_elements(
            By.XPATH, '//*[@id="frm_supProd"]/div[3]/table/tbody/tr/td[3]/div')
        return [item.text for item in items]

    return _do_in_main_frame(auto, lambda: get_product_names())


# EXTERNAL INTERFACES

def register(auto: Automatic, pns):
    if not go_product_registration_page(auto):
        log().error("Failed to go product registration page.")
        return False

    registered_pns = get_registered_products(auto)
    for pn in pns:
        if pn in registered_pns:
            log().info(f"{pn} is already registered.")
            continue
        if not register_product(auto, pn):
            log().error(f"Failed to register a product. pn={pn}")

    return True


def login(auto: Automatic, password):
    go_homepage(auto)

    member_frame = auto.get_element(By.ID, 'member_iframe')
    if not member_frame:
        log().error("Failed to find member frame")
        return False

    # click the login button
    with auto.get_frame(member_frame):
        if not auto.click(By.XPATH, '//*[@id="logout"]/ul/li[1]/ul/li/a/img'):
            log().error("Failed to click Login Button")
            return False

    # try to login with certificate
    import org.g2b.certificate
    return org.g2b.certificate.cert_login(password)


class G2B:
    def __init__(self, pw, close_windows=True, headless=True):
        self.auto = Automatic.create(Automatic.DriverType.Edge)
        self.__close_windows = close_windows
        self.__pw = pw

    def login(self):
        if not login(self.auto, self.__pw):
            log().error("Failed to login")
            return False
        # prevent register as soon as login
        time.sleep(3)
        return True

    def __del__(self):
        if self.__close_windows:
            self.__driver.close()

    def register(self, code):
        codes = code.split(",")
        codes = [pn.strip() for pn in codes]
        return register(self.auto, codes)
