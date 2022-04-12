
import sys, time
from selenium.webdriver.common.by import By
import auto.selenium, auto.windows


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
            search_btn = (By.XPATH, '//*[@id="frm_addProd"]/div[3]/table/tbody/tr/td[1]/div/button')
            return auto.selenium.click(driver, search_btn)

def _find_product(driver, pn):
    with auto.selenium.Window(driver, "[팝업] 세부품명찾기: 나라장터"):
        pn_input = (By.ID, 'detailPrdnmNo')
        auto.selenium.send_keys(driver, pn_input, pn)

        search_btn = (By.ID, 'bt_search')
        auto.selenium.click(driver, search_btn)
        # select item
        first_item = (By.XPATH, '//*[@id="container"]/div[1]/table/tbody/tr/td[2]/a')    
        auto.selenium.click(driver, first_item)

def _register_product(driver):
    with auto.selenium.Frame(driver, (By.ID, 'sub')):
        with auto.selenium.Frame(driver, (By.NAME, 'main')):
            register_btn = (By.XPATH,'//*[@id="frm_addProd"]/div[2]/a')
            success = auto.selenium.click(driver, register_btn)
            if not success:
                return False
            time.sleep(1)
            alert = driver.switch_to.alert
            alert.accept()
    time.sleep(1)
    with auto.selenium.Window(driver, "Message: 나라장터"):
        confirm_btn = ( By.XPATH, '//*[@id="container3"]/div[2]/div/a')
        auto.selenium.click(driver, confirm_btn)


def _login_with_certificate(password):
    
     # TODO: wait until exisiting the window handle for "인증서 선택"
    i = 0
    hwnd = None
    while not hwnd:
        hwnd = auto.windows.find_window_handle("인증서 선택")
        i += 1
        if i >= 10: 
            return False        
        time.sleep(1)

    # make it foreground
    auto.windows.bring_window_to_top(hwnd)

    # click password input box to focus on
    auto.windows.click(hwnd, 242, 478 + 30)
    time.sleep(1)

    # put password
    auto.windows.type(password)

    # click ok button
    auto.windows.click(hwnd, 152, 516 + 30)    

    # TODO: Wait until reload the logout panel.    
    time.sleep(1)
    return True

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
    return _login_with_certificate(password)
    

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
            items = driver.find_elements(By.XPATH, '//*[@id="frm_supProd"]/div[3]/table/tbody/tr/td[3]/div')
            return [ item.text for item in items ]


class G2B:
    def __init__(self, driver, pw):
        self.driver = driver
        go_homepage(driver)
        login(driver, pw)
    
    def preregister(self, pns):        
        go_product_registration_page(self.driver)
        registered_pns = get_registered_products(self.driver)
        for pn in pns:
            if pn in registered_pns:
                continue
            register_product(self.driver, pn)
        return True
            

