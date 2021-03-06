
from selenium.webdriver.common.by import By
import auto.selenium
import auto.windows

from org.g2b.safeg2b import *
from org.g2b import safeg2b


def logger():
    import logging
    return logging.getLogger(__name__)


def _go_mypage(driver):
    mypage = 'https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=/pt/menu/frameMypage.do'
    driver.get(mypage)


def _edit_mypage(driver):
    # Click the edit button in multile frames sub>main>btn
    with auto.selenium.Frame(driver, (By.ID, 'sub')):
        with auto.selenium.Frame(driver, (By.NAME, 'main')):
            edit_btn = (By.XPATH, '//*[@id="container"]/div[2]/div/a[1]')
            auto.selenium.click(driver, edit_btn)


def _open_item_find_window(driver):
    with auto.selenium.Frame(driver, (By.ID, 'sub')):
        with auto.selenium.Frame(driver, (By.NAME, 'main')):
            logger().info("click item find button")
            search_btn = (
                By.XPATH, '//*[@id="frm_addProd"]/div[3]/table/tbody/tr/td[1]/div/button')
            return auto.selenium.click(driver, search_btn)


def _find_product(driver, pn):
    with auto.selenium.Window(driver, "[팝업] 세부품명찾기: 나라장터"):

        logger().info(f"type a product number={pn}")
        pn_input = (By.ID, 'detailPrdnmNo')
        auto.selenium.send_keys(driver, pn_input, pn)

        search_btn = (By.ID, 'bt_search')
        auto.selenium.click(driver, search_btn)
        # select item
        first_item = (
            By.XPATH, '//*[@id="container"]/div[1]/table/tbody/tr/td[2]/a')
        auto.selenium.click(driver, first_item)


def _register_product(driver):
    # Move to frame
    with auto.selenium.Frame(driver, (By.ID, 'sub')):
        with auto.selenium.Frame(driver, (By.NAME, 'main')):
            register_btn = (By.XPATH, '//*[@id="frm_addProd"]/div[2]/a')
            logger().info("click register button")
            success = auto.selenium.click(driver, register_btn)
            if not success:
                return False

            alert = auto.selenium.wait_until_alert(driver)
            alert.accept()
            logger().info(f"Accepted alert.")

    with auto.selenium.Window(driver, "Message: 나라장터"):
        confirm_btn = (By.XPATH, '//*[@id="container3"]/div[2]/div/a')
        success = auto.selenium.click(driver, confirm_btn)
        logger().info(f"click confirm button.")


# Go to the homepage to login
def go_homepage(driver):
    g2b_website = 'https://www.g2b.go.kr'
    driver.get(g2b_website)

# Login


def login(driver, password):
    # click the login button
    with auto.selenium.Frame(driver, (By.ID, 'member_iframe')):
        login_btn = (By.XPATH, '//*[@id="logout"]/ul/li[1]/ul/li/a/img')
        success = auto.selenium.click(driver, login_btn)
        if not success:
            return False

    # try to login with certificate
    import org.g2b.certificate
    return org.g2b.certificate.cert_login(password)


# Go to the page where we can register a new product
def go_product_registration_page(driver):
    # go mypage
    _go_mypage(driver)

    # click edit button
    _edit_mypage(driver)


# Register a product
def register_product(driver, pn):
    # open the window by clicking search button
    _open_item_find_window(driver)

    # move to the windows and input the product number
    _find_product(driver, pn)

    # click register button and clear popup and confirm window
    _register_product(driver)


# Return items currently registered
def get_registered_products(driver):
    # TODO: how to check current pages
    with auto.selenium.Frame(driver, (By.ID, 'sub')):
        with auto.selenium.Frame(driver, (By.NAME, 'main')):
            items = driver.find_elements(
                By.XPATH, '//*[@id="frm_supProd"]/div[3]/table/tbody/tr/td[3]/div')
            return [item.text for item in items]


def g2b_register(driver, pns):
    go_product_registration_page(driver)
    registered_pns = get_registered_products(driver)
    for pn in pns:
        if pn in registered_pns:
            logger().info(f"{pn} is already registered.")
            continue
        register_product(driver, pn)
        logger().info(f"{pn} is registered.")
    return True


class G2B:
    def __init__(self, pw, close_windows=True, headless=True):
        self.__driver = auto.selenium.create_edge_driver(headless=headless)
        self.__close_windows = close_windows
        go_homepage(self.__driver)
        login(self.__driver, pw)
        self.__driver.minimize_window()

    def __del__(self):
        if self.__close_windows:
            self.__driver.close()

    def __register(self, pns):
        return g2b_register(self.__driver, pns)

    def register(self, pre):
        product_numbers = pre.number.split(",")
        product_numbers = [pn.strip() for pn in product_numbers]
        return self.__register(product_numbers)


class G2B__:
    def __init__(self, pw, rn, close_windows=True, headless=True):
        logger().debug("__init__")
        self.__driver = auto.selenium.create_edge_driver(headless=headless)
        self.__pw = pw
        self.__close_windows = close_windows
        go_homepage(self.__driver)
        login(self.__driver, pw)
        self.__driver.minimize_window()

        # safe g2b
        safeg2b_run()
        safeg2b_initialize()
        if not safeg2b._login_biotoken():
            raise Exception("Failed to login to safeg2b")

    def __del__(self):
        logger().debug("__del__")
        # if self.__close_windows:
        #     safeg2b_close()
        #     self.__driver.close()

    def __register(self, pns):
        return g2b_register(self.__driver, pns)

    def register(self, pre):
        product_numbers = pre.number.split(",")
        product_numbers = [pn.strip() for pn in product_numbers]
        return self.__register(product_numbers)

    def participate(self, bid):
        logger().info(f"participate in {bid.number} price={bid.price}")
        self.__driver.minimize_window()
        if not safeg2b_is_running():
            return False, "safeg2b instance is not running"
        safeg2b_participate(self.__pw, bid.number, str(bid.price))
        return True, None


if __name__ == "__main__":
    from account import account_get
    pw = account_get("g2b", "pw") 
    rn = account_get("g2b", "rn")
    obj = G2B(pw, rn)

    # Test Register Pre
    # class TestPre:
    #     def __init__(self):
    #         self.number = "1017150101"

    # obj.register(TestPre())
