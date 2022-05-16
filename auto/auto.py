
import logging
from auto import selenium
from plum import dispatch

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
    print(f"Type. element={element}")
    return auto_type(element, text)


@dispatch
def auto_type(driver: WebDriver, by: str, path: str, text: str, timeout: int = __default_timeout) -> bool:
    return auto_type(driver, (by, path), text, timeout)
