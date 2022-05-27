
import autoit
import logging
import time
from auto import selenium
from plum import dispatch  # mulitple dispatch

from typing import Tuple, Union, List

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

# wait elements
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# WebDriver = selenium.webdriver.remote.webdriver.WebDriver
# By = selenium.webdriver.common.by.By


def log():
    return logging.getLogger(__package__)


__default_timeout = 10


def auto_wait_until(func, *, timeout=__default_timeout, interval=0.5):
    start = time.time()
    curr = 0
    retry = 0
    while True:
        curr = time.time() - start
        retry = retry + 1
        res = func()
        if res != None and res != 0:
            return res

        if curr > timeout:
            log().error(
                f"Timeout! wait_until takes {curr}. timeout={timeout}, interval={interval}, retry={retry}")
            break

        # every 500ms
        time.sleep(interval)

    return res


@dispatch
def auto_find_element(driver: WebDriver, locator: tuple, timeout: int = __default_timeout) -> Union[WebElement, None]:
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator))
    except:
        log().error(
            f"Failed to find an element. locator={locator}, timeout={timeout}")
        return None


@dispatch
def auto_find_element(driver: WebDriver, by: str, path: str, timeout: int = __default_timeout) -> Union[WebElement, None]:
    return auto_find_element(driver, (by, path), timeout)


@dispatch
def auto_find_element(element: WebElement, by: str, path: str, timeout: int = __default_timeout) -> WebElement:
    def _find():
        xs = element.find_elements(by, path)
        return xs[0] if len(xs) > 0 else None
    return auto_wait_until(lambda: _find())


@dispatch
def auto_find_all_elements(driver: WebDriver, by: str, path: str, timeout: int = __default_timeout) -> List[WebElement]:
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((by, path)))
    except:
        log().error(
            f"Failed to find an element. locator={(by, path)}, timeout={timeout}")
        return None


@dispatch
def auto_click(driver: WebDriver, element: WebElement) -> bool:
    if not element:
        log().error(f"Failed to click. element={element}")
        return False
    try:
        driver.execute_script("arguments[0].click();", element)
    except Exception as e:
        log().error(f"Failed to click. element={element}, reason={e}")
        return False
    return True


@dispatch
def auto_click(driver: WebDriver, locator: Tuple[str, str], timeout: int = __default_timeout) -> bool:
    element = auto_find_element(driver, locator, timeout)
    return auto_click(driver, element)


@dispatch
def auto_click(driver: WebDriver, by: str, path: str, timeout: int = __default_timeout) -> bool:
    return auto_click(driver, (by, path), timeout)


@dispatch
def auto_type(element: WebElement, text: str) -> bool:
    if not element:
        log().error(f"Failed to type. element={element}, text={text}")
        return False
    element.send_keys(text)
    return True


@dispatch
def auto_type(driver: WebDriver, locator: Tuple[str, str], text: str, timeout: int = __default_timeout) -> bool:
    element = auto_find_element(driver, locator, timeout)
    return auto_type(element, text)


@dispatch
def auto_type(driver: WebDriver, by: str, path: str, text: str, timeout: int = __default_timeout) -> bool:
    return auto_type(driver, (by, path), text, timeout)


def auto_file_chooser(filepath):
    window = "[TITLE:열기; CLASS:#32770]"
    autoit.win_wait(window, timeout=10)
    autoit.win_activate(window)
    autoit.win_wait_active(window, timeout=10)

    # Needs some time to wait next steps.
    time.sleep(1)

    # fill the edit box with filepath
    edit_class = "Edit1"
    autoit.control_set_text(window, edit_class, f"\"{filepath}\"")
    log().info(f"Typed a filepath. filepath={filepath}")

    # click ok button
    button_class = "Button1"
    autoit.control_click(window, button_class)


def contains(a: str, b: str) -> bool:
    return True if a.find(b) >= 0 else False


def auto_is_visible(element: WebElement):
    style = element.get_attribute("style")
    return not contains(style, "display:none") and not contains(style, "display: none")
