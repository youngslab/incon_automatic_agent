
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

# wait elements
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from typing import List, Tuple, Optional

# WebDriver Manager (selenium 4)
# https://pypi.org/project/webdriver-manager/#use-with-edge
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def __logger():
    import logging
    return logging.getLogger(__name__)

# options.add_argument('headless')
    # options.add_argument('dSisable-gpu')
    # options.use_chromium = True
    # options.binary_location = r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    # driver = webdriver.Edge(options=options)


def create_edge_driver(headless=False):
    options = webdriver.EdgeOptions()
    # level 3 is lowest value for log-level
    options.add_argument('log-level=3')
    if headless:
        options.add_argument('headless')
        options.add_argument('disable-gpu')

    service = Service(EdgeChromiumDriverManager().install())
    import time
    time.sleep(1)
    return webdriver.Edge(options=options, service=service)


# Return an alert object
def wait_until_alert(driver, timeout=3):
    WebDriverWait(driver, timeout).until(
        EC.alert_is_present(), "Can not find an alert window")
    return driver.switch_to.alert


def wait_unttil_window(driver, title: str, timeout=3):
    wait = WebDriverWait(driver, timeout)
    return wait.until(lambda x: get_window_handle(x, title), f"Can not find a window({title})")


def wait_until_webpage(driver, url: str, timeout=10):
    wait = WebDriverWait(driver, timeout)
    return wait.until(lambda x: x.current_url == url, f"Can not reach to ({url})")

# locator: (By.ID, "myDynamicElement")
# timemout: maximum time to wait until locator exists
# return True if success otherwise False


def wait_until(driver, locator, timeout):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator))
        return True
    except:
        return False


def find_element_until(driver, locator, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator))
    except:
        return None


def click_element(driver, e) -> bool:
    try:
        driver.execute_script("arguments[0].click();", e)
        driver.implicitly_wait(1)
    except Exception as e:
        __logger().error(
            f"selenium) Failed to execute click script. reason={e}")
        return False
    return True


def click(driver, locator) -> bool:
    elem = find_element_until(driver, locator)
    if not elem:
        return False

    try:
        driver.execute_script("arguments[0].click();", elem)
        driver.implicitly_wait(1)
    except Exception as e:
        __logger().error(
            f"selenium) Failed to execute click script. reason={e}")
        return False

    return True


def send_keys(driver, locator, text):
    elem = find_element_until(driver, locator)
    if not elem:
        return False
    elem.send_keys(text)
    driver.implicitly_wait(1)
    return True


def send_keys_element(driver, elem, text):
    elem.send_keys(text)
    driver.implicitly_wait(1)
    return True


def go(driver, page):
    driver.get(page)
    driver.implicitly_wait(5)


# WINDOW(TAB) API

def get_window_handle(driver, title):
    # __logger().info(("get_window_handle - title={}".format(driver.title))
    current = driver.current_window_handle
    result = None
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        # __logger().info((driver.title)
        if title == driver.title:
            result = handle
            break
    driver.switch_to.window(current)
    return result


def selenium_close_other_windows(driver, whitelist=[]):
    current = driver.current_window_handle

    for handle in driver.window_handles:
        if handle == current:
            continue

        driver.switch_to.window(handle)
        if driver.title in whitelist:
            continue

        driver.close()

    driver.switch_to.window(current)


def get_window_handle_until(driver, title, maxtry=10):
    import time
    for i in range(maxtry):
        time.sleep(1)
        handle = get_window_handle(driver, title)
        if handle:
            return handle


def go_window(driver, title):
    handle = get_window_handle(driver, title)
    if not handle:
        return False
    driver.switch_to.window(handle)
    return True


def go_frmae(driver, locator):
    _frame = find_element_until(driver, locator)
    if not _frame:
        return None
    driver.switch_to.frame(_frame)


class Window:
    def __init__(self, driver, title):
        self.driver = driver
        self.prev_window_handle = driver.current_window_handle
        self.next_window_handle = wait_unttil_window(driver, title)

    def __enter__(self):
        self.driver.switch_to.window(self.next_window_handle)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.switch_to.window(self.prev_window_handle)
        # __logger().info(("exited: {}".format(self.driver.title))


class Frame:
    def __init__(self, driver, locator, timeout=10):
        self.driver = driver
        self.frame = find_element_until(driver, locator, timeout=timeout)
        if not self.frame:
            raise Exception(f"Failed to find frame. locator={locator}")

    def __enter__(self):
        self.driver.switch_to.frame(self.frame)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.switch_to.parent_frame()


class Page:
    def __init__(self, driver, page):
        self.driver = driver
        self.prev = driver.current_url
        self.page = page

    def __enter__(self):
        self.driver.get(self.page)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.get(self.prev)
