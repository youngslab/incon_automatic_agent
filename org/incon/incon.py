
from selenium.webdriver.edge.webdriver import WebDriver
import random
import logging

import auto.selenium
from selenium.webdriver.common.by import By

# ---------------------
# Utilities
# ---------------------


# ---------------------
# Incon Login Page
# ---------------------

def log():
    return logging.getLogger(__package__)

# Incon Homepage


def incon_go_homepage(driver):
    auto.selenium.go(driver, 'http://chodal.in-con.biz/bidmobile/login.jsp')

# Condition
# - Should be at the homepage
# - Mobile page: mepno, meppw


def incon_login(driver, id, pw):
    id_input = (By.ID, 'mepno')
    pw_input = (By.ID, 'meppw')
    success = auto.selenium.send_keys(driver, id_input, id) \
        | auto.selenium.send_keys(driver, pw_input, pw)
    if not success:
        return False

    submit_btn = (By.ID, 'submit')
    success = auto.selenium.click(driver, submit_btn)
    if not success:
        return False

    # wait until its url changes
    dest = 'https://chodal.in-con.biz/bidmobile/msg/list.do'
    return auto.selenium.wait_until_webpage(driver, dest)


# ---------------------
# List Item
# ---------------------

def incon_listitem_get_button(listitem):
    return listitem.find_element(By.XPATH, './/a[2]')


def incon_listitem_is_completed(listitem):
    completion_button = incon_listitem_get_button(listitem)
    return 'ui-icon-check' in completion_button.get_attribute("class")


def incon_listitem_complete(driver, listitem):
    completion_button = incon_listitem_get_button(listitem)
    return auto.selenium.click_element(driver, completion_button)


def incon_listitem_click(driver, listitem):
    body = listitem.find_element(By.XPATH, './/a[1]')
    return auto.selenium.click_element(driver, body)


# ---------------------
# Popup
# ---------------------

# Check the popup is opened
def incon_popup_is_open(webdriver):
    popup_layer = (By.ID, 'layer_popup')
    elem = auto.selenium.find_element_until(webdriver, popup_layer, 10)
    if not elem:
        raise Exception("Can not find layer_popup in this page")
    # try to find "display:none"in style
    return elem.get_attribute('style').find('display') < 0

# Click the popup close button.


def incon_popup_close(webdriver):
    close_btn = (By.XPATH, '//*[@id="close"]/a')
    elem = auto.selenium.find_element_until(webdriver, close_btn)
    auto.selenium.click_element(webdriver, elem)

# Click


def incon_popup_check_do_not_open_today(webdriver):
    todaycloseyn = (By.ID, 'todaycloseyn')
    elem = auto.selenium.find_element_until(webdriver, todaycloseyn)
    auto.selenium.click_element(webdriver, elem)


# ---------------------
# Preregistration
# ---------------------

def incon_pre_go_page(driver):
    auto.selenium.go(driver, 'http://chodal.in-con.biz/bidmobile/msg/list.do')


def incon_pre_close_popup(webdriver):
    if incon_popup_is_open(webdriver):
        incon_popup_check_do_not_open_today(webdriver)
        incon_popup_close(webdriver)


def incon_pre_get_listitems(webdriver):
    return webdriver.find_elements(By.XPATH, '//*[@id="demo-page"]/div[2]/ul/li')


def incon_pre_listitem_activate_all(webdriver):
    xs = webdriver.find_elements(
        By.XPATH, f'//*[@id="demo-page"]/div[2]/ul/li/a[1]/p')
    for x in xs:
        # get id
        id = x.get_attribute("id")
        if not id:
            continue
        if id.find("hide") < 0:
            continue
        log().debug("activate) found <p id=\"hidexxxx\"> element.")
        style = x.get_attribute("style")
        if style.find("display") >= 0:  # display:none
            log().debug("activate) skip <p id=\"hidexxxx\"> element. It's hidden")
            continue

        # 이걸 click해도 되나?
        # 이전까지는 .//a[1]을 현재는 .//a[1]/p를 click 하는 것이다.
        log().debug("activate) activate pre item.")
        auto.selenium.click_element(webdriver, x)


def incon_pre_listitem_get_data(webelement):
    res = dict()
    tokens = webelement.text.split('\n')
    for token in tokens:
        sep = token.find(":")
        if sep < 0 or token.find("**") >= 0:
            res['etc'] = f"{res.get('etc','')} \n{token}"
        else:
            res[token[:sep].strip()] = token[sep+1:].strip()
    return res


class Preregistration:
    def __init__(self, driver, pre_listitem):
        self.__driver = driver
        self.__element = pre_listitem
        self.__data = incon_pre_listitem_get_data(pre_listitem)
        self.market = self.__data['조달사이트']
        self.number = self.__get_number()
        self.title = self.__get_title()
        self.deadline = self.__get_deadline()

    def __get_number(self):
        if self.__data.get("세부품명번호"):
            return self.__data.get("세부품명번호")
        elif self.__data.get("공고번호"):
            return self.__data.get("공고번호")
        raise Exception(f"Not found Notice Numboer: {self.__data}")

    def __get_title(self):
        if self.__data.get("세부품명"):
            return self.__data.get("세부품명")
        elif self.__data.get("공고명"):
            return self.__data.get("공고명")
        raise Exception(f"Not found title: {self.__data}")

    def __get_deadline(self):
        if self.__data.get('입찰신청마감일시'):
            return self.__data.get('입찰신청마감일시')
        elif self.__data.get('등록마감일시'):
            return self.__data.get('등록마감일시')
        raise Exception(f"Not found deadline: {self.__data}")

    def is_completed(self):
        return incon_listitem_is_completed(self.__element)

    def complete(self):
        log().info("click item completion")
        return incon_listitem_complete(self.__driver, self.__element)

    def __str__(self):
        return f"{self.market}) {self.number}({self.title})"


# ---------------------
# Biding
# ---------------------
def incon_bid_go_page(driver: WebDriver):
    auto.selenium.go(driver, 'http://chodal.in-con.biz/bidmobile/bid/list.do')


def incon_bid_listitem_is_activated(listitem):
    # items = listitem.find_elements(By.XPATH, \
    #     './/a[1]/h2[contains(@id, "first") and not(contains(@style,"display"))]')
    # if len(items) == 0:
    #     return True
    # else:
    # return False
    try:
        elem = listitem.find_element(By.CSS_SELECTOR, 'h2[id^="first"]')
        style = elem.get_attribute("style")
        if style.find("display") >= 0:
            return True
    except Exception:
        return True

    return False


def incon_bid_get_listitem(webdriver, idx):
    return webdriver.find_element(By.XPATH, f'//*[@id="bid_list"]/li[{idx + 1}]')


def incon_bid_get_listitems(webdriver):
    # check one item which has been shown
    locator = (By.XPATH, '//*[@id="bid_list"]/li')
    item = auto.selenium.find_element_until(webdriver, locator, timeout=5)
    if item == None:
        raise Exception(
            f"Need to check current pages. {webdriver.current_url}")
    return webdriver.find_elements(*locator)


def incon_bid_activate_all(webdriver):
    xs = webdriver.find_elements(By.XPATH, '//*[@id="bid_list"]/li/a[1]/h2')
    for x in xs:
        # get id
        id = x.get_attribute("id")
        if not id:
            continue
        if id.find("first") < 0:
            continue
        log().debug("activate) found <h2 id=\"firstxxxx\"> element.")
        style = x.get_attribute("style")
        if style.find("display") >= 0:  # display:none
            log().debug("activate) skip <h2 id=\"firstxxxx\"> element. It's hidden")
            continue
        log().debug("activate) activate bid item.")
        auto.selenium.click_element(webdriver, x)


def incon_bid_listitem_get_data(listitem):
    res = dict()
    tokens = listitem.text.split('\n')
    for token in tokens:
        sep = token.find(":")
        if sep < 0 or token.find("**") >= 0:
            res['etc'] = f"{res.get('etc','')} \n{token}"
        else:
            res[token[:sep].strip()] = token[sep+1:].strip()
    return res


def incon_bid_listitem_get_market(listitem):
    market_img = listitem.find_element(By.XPATH, './/a[1]/img[1]')
    img_src = market_img.get_attribute("src")
    if img_src.find("bid_title_icon1.png") >= 0:
        return "나라장터"
    elif img_src.find("bid_title_icon2.png") >= 0:
        return "국방전자조달"
    elif img_src.find("bid_title_icon3.png") >= 0:
        return "LH"
    elif img_src.find("bid_title_icon4.png") >= 0:
        return "도로공사"
    elif img_src.find("bid_title_icon5.png") >= 0:
        return "한국전력"
    elif img_src.find("bid_title_icon6.png") >= 0:
        return "수자원공사"
    elif img_src.find("bid_title_icon7.png") >= 0:
        return "마사회"
    # icon 8 in not presents
    elif img_src.find("bid_title_icon9.png") >= 0:
        return "학교장터"
    elif img_src.find("bid_title_icon10.png") >= 0:
        return "인천공항"
    elif img_src.find("bid_title_icon11.png") >= 0:
        return "한수원"
    elif img_src.find("bid_title_icon12.png") >= 0:
        return "가스공사"
    elif img_src.find("bid_title_icon13.png") >= 0:
        return "철도공사"
    elif img_src.find("bid_title_icon14.png") >= 0:
        return "석유공사"
    else:
        raise Exception(f"Unkown market of {img_src}")


def incon_bid_listitem_is_ready(listitem) -> bool:
    status_img = listitem.find_element(By.XPATH, './/a[1]/img[2]')
    status_src = status_img.get_attribute('src')
    return status_src.find("ing.png") >= 0


def incon_bid_listitem_get_price(listitem) -> int:
    price = listitem.find_element(By.XPATH, './/a[1]/div/font')
    numbers = "".join(char for char in price.text if char.isdigit())
    if numbers:
        return int(numbers)
    else:
        return 0


def incon_bid_listitem_has_price(listitem) -> bool:
    if incon_bid_listitem_get_price(listitem) > 0:
        return True
    else:
        return False


def incon_bid_listitem_price(webdriver, listitem) -> bool:
    # page moved.
    success = incon_listitem_click(webdriver, listitem)
    if not success:
        log().warning("failed to click bid listitem.")
        return False

    # detail page
    price_button = auto.selenium.find_element_until(
        webdriver, (By.XPATH, '//*[@id="detail-page"]/div[2]/div/div[7]/a[1]'))
    success = auto.selenium.click_element(webdriver, price_button)
    if not success:
        log().warning("failed to click price_button.")
        return False

    # Input page
    # input percentage
    input = auto.selenium.find_element_until(
        webdriver, (By.XPATH, '//*[@id="point"]'))
    min = webdriver.find_element(By.XPATH, '//*[@id="sRange"]')
    min = float(min.text)
    max = webdriver.find_element(By.XPATH, '//*[@id="eRange"]')
    max = float(max.text)

    # 4 decimal places
    target = round(random.uniform(min, max), 4)

    log().info(
        f"randomly select price rate. rate={target}, min={min}, max={max}")
    # BE CAREFUL: Target should be in the range from min to max.
    if target < min or target > max:
        raise Exception(
            f"Price Rate is out of bound. rate={target}, min={min}, max={max}")

    success = auto.selenium.send_keys_element(webdriver, input, f"{target}")
    if not success:
        log().warning("failed to type price.")
        return False

    save_button = webdriver.find_element(
        By.XPATH, '//*[@id="detail-page"]/div[2]/a')
    success = auto.selenium.click_element(webdriver, save_button)
    if not success:
        log().warning("failed to click save_button.")
        return False

    return True


def incon_bid_price_all(webdriver):
    items = incon_bid_get_listitems(webdriver)
    log().debug(f"pricing) get all bid items. len={len(items)}")
    counts = len(items)
    for idx in range(counts):
        item = incon_bid_get_listitem(webdriver, idx)
        if not incon_bid_listitem_has_price(item):
            temp = Bid(webdriver, item)
            log().info(
                f"pricing) price the bid item. idx={idx}, nubmer={temp.number}, title={temp.title}")
            incon_bid_listitem_price(webdriver, item)


class Bid:
    def __init__(self, webdriver, listitem):
        self.__driver = webdriver
        self.__listitem = listitem
        self.__data = incon_bid_listitem_get_data(self.__listitem)
        self.title = self.__data['공고명']
        self.number = self.__data['공고번호']
        self.deadline = self.__data['입찰마감']
        self.market = incon_bid_listitem_get_market(self.__listitem)
        self.is_ready = incon_bid_listitem_is_ready(self.__listitem)
        self.price = incon_bid_listitem_get_price(self.__listitem)

    def __str__(self):
        return f"{self.market:6s}) {self.number:20s}[{self.title:.6s}]  @ {self.price} won"

    def is_completed(self):
        return incon_listitem_is_completed(self.__listitem)

    def complete(self):
        return incon_listitem_complete(self.__driver, self.__listitem)

# ---------------------
# Incon
# ---------------------


def incon_get_pres(webdriver) -> list[Preregistration]:
    log().info("go to the preregistration list page")
    incon_pre_go_page(webdriver)

    # cleanup
    log().info("close popup")
    incon_pre_close_popup(webdriver)
    log().info("activate all items")
    incon_pre_listitem_activate_all(webdriver)

    # convert
    log().info("create items of Pre class")
    items = incon_pre_get_listitems(webdriver)
    return [Preregistration(webdriver, item) for item in items]


def incon_get_bids(webdriver) -> list[Bid]:
    log().info("go to the bid list page")
    incon_bid_go_page(webdriver)

    # cleanup
    log().info("activate all bid items")
    incon_bid_activate_all(webdriver)

    log().info("price all items")
    incon_bid_price_all(webdriver)

    # convert
    log().info("create items of Bid")
    items = incon_bid_get_listitems(webdriver)
    return [Bid(webdriver, item) for item in items]

# STATE MACHINE


class Incon:
    def __init__(self, id, pw, headless=True):
        self.driver = None
        self.driver = auto.selenium.create_edge_driver(headless=headless)
        incon_go_homepage(self.driver)
        incon_login(self.driver, id, pw)

    def __del__(self):
        if self.driver:
            self.driver.close()

    def get_pre_data(self):
        return incon_get_pres(self.driver)

    def get_bid_data(self):
        return incon_get_bids(self.driver)


def test_execution_time():
    from account import account_get
    id = account_get("incon", "id")
    pw = account_get("incon", "pw")

    ic = Incon(id, pw)

    import time
    start = time.time()
    pres = ic.get_pre_data()
    end = time.time()
    print(f"getting pre items takes {end - start}")
    for pre in pres:
        print(pre)

    start = time.time()
    bids = ic.get_bid_data()
    end = time.time()
    print(f"getting pre items takes {end - start}")
    for bid in bids:
        print(bid)


# ---------------------
# Test
# ---------------------
if __name__ == "__main__":
    import logger
    logger.logger_init()

    test_execution_time()
