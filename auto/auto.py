
import autoit
import logging
import time
import pyautogui

from auto import selenium
from plum import dispatch  # mulitple dispatch

from typing import Tuple, Union, List

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

# wait elements
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException

# WebDriver = selenium.webdriver.remote.webdriver.WebDriver
# By = selenium.webdriver.common.by.By


def log():
    return logging.getLogger(__package__)


__default_timeout = 10

# -----------------------
# wait element variation
# -----------------------


@dispatch
def wait_clickable(driver: WebDriver, locator: Tuple[str, str], timeout: int = __default_timeout) -> WebElement:
    try:
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator))
    except Exception as e:
        return None


@dispatch
def wait_alert(driver: WebDriver, timeout: int = __default_timeout):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.alert_is_present())
    except Exception as e:
        return None


@dispatch
def wait_no_element(driver: WebDriver, locator: Tuple[str, str], timeout: int = __default_timeout) -> bool:
    try:
        return WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located(locator))
    except Exception as e:
        return None


@dispatch
def wait_element(driver: WebDriver, locator: Tuple[str, str], timeout: int = __default_timeout) -> WebElement:
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator))
    except Exception as e:
        return None


@dispatch
def wait_all_elements(driver: WebDriver, locator: Tuple[str, str], timeout: int = __default_timeout):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located(locator))
    except:
        log().error(
            f"Failed to find an element. locator={locator}, timeout={timeout}")
        return []


@dispatch
def wait_image(img: str, *, timeout: int = __default_timeout, grayscale: bool = True, confidence: float = .9):
    def find_image(): return pyautogui.locateCenterOnScreen(
        img, grayscale=grayscale, confidence=confidence)
    return auto_wait_until(lambda: find_image(), timeout=timeout)


@dispatch
def wait_no_image(img: str, *, timeout: int = __default_timeout, grayscale: bool = True, confidence: float = .9):
    def find_no_image(): return True if pyautogui.locateCenterOnScreen(
        img, grayscale=grayscale, confidence=confidence) == None else False
    return auto_wait_until(lambda: find_no_image(), timeout=timeout)


@dispatch
def wait_no_window(title: str, *, timeout=__default_timeout):
    window = f"[TITLE:{title}]"
    try:
        autoit.win_wait_close(window, timeout=timeout)
        return True
    except:
        log().error(f"Failed to wait a window closed. title={title}")
        return False


# -----------------------
# -----------------------


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


# Return an alert object
def auto_find_alert(driver: WebDriver, timeout=__default_timeout):
    try:
        WebDriverWait(driver, timeout).until(
            EC.alert_is_present(), "Can not find an alert window")
        return driver.switch_to.alert
    except TimeoutException:
        return None


@dispatch
def auto_find_element(driver: WebDriver, locator: tuple, timeout: int = __default_timeout) -> Union[WebElement, None]:
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator))
    except Exception as e:
        # log().error(
        #     f"Failed to find an element. locator={locator}, timeout={timeout}, excpetion={e}")
        return None


@dispatch
def auto_find_element(driver: WebDriver, by: str, path: str, timeout: int = __default_timeout) -> Union[WebElement, None]:
    return auto_find_element(driver, (by, path), timeout)


@dispatch
def auto_find_element(element: WebElement, by: str, path: str, timeout: int = __default_timeout) -> WebElement:
    def _find():
        xs = element.find_elements(by, path)
        return xs[0] if len(xs) > 0 else None
    try:
        return auto_wait_until(lambda: _find(), timeout=timeout)
    except:
        return None


@dispatch
def auto_find_all_elements(driver: WebDriver, by: str, path: str, timeout: int = __default_timeout):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((by, path)))
    except:
        log().error(
            f"Failed to find an element. locator={(by, path)}, timeout={timeout}")
        return []


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
    wait = WebDriverWait(driver, timeout)
    element = wait.until(EC.element_to_be_clickable(locator))
    # element = auto_find_element(driver, locator, timeout)
    return auto_click(driver, element)


@dispatch
def auto_click(img: str, *, timeout: int = __default_timeout, confidence: float = .9, grayscale=True):
    center = wait_image(img, timeout=timeout,
                        grayscale=grayscale, confidence=confidence)
    if center is None:
        log().error(f"Failed to find an image on the screen. img={img}")
        return False

    pyautogui.click(center)
    return True


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


@dispatch
def auto_type(img: str, text: str, *, timeout: int = __default_timeout, confidence: float = .9, grayscale=True):
    if not auto_click(img, timeout=timeout, grayscale=grayscale, confidence=confidence):
        return False
    time.sleep(1)
    pyautogui.typewrite(text)
    time.sleep(1)
    return True


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


def auto_activate(title, *, timeout=30) -> bool:
    window = f"[TITLE:{title}]"
    try:
        autoit.win_wait(window, timeout=timeout)
    except Exception as e:
        log().error(f"Failed to find a window. title={title}, e={e}")
        return False

    try:
        autoit.win_activate(window, timeout=timeout)
        return True
    except Exception as e:
        log().error(f"Failed to activate a window. title={title}, e={e}")
        return False


def auto_go_bottom(title, *, timeout=30):
    auto_activate(title, timeout=timeout)
    autoit.send("{F6}")
    autoit.send("{END}")
