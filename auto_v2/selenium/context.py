
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select


# wait elements
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# exception
# from selenium.common.exceptions import StaleElementReferenceException

# types
from typing import Union, List

from .elements import Descriptor, is_alert, is_element, is_window, is_default_frame
from ..common import wait

import time

def get_or(a, b) -> int:
    return a if a else b

class Context:
    def __init__(self, driver: WebDriver, *, timeout, differ):
        self.__driver = driver
        self.__current_frame = None
        self.__default_window_handle = driver.current_window_handle
        self.__timeout = timeout
        self.__differ = differ


    def activate(self, desc: Descriptor):
        if not desc:
            return False

        if is_default_frame(desc):
            return self.set_default_frame()

        elem = self.get(desc)
        if not elem:
            return False

        if is_window(desc):
            return self.set_current_window(elem)
        elif isinstance(elem, WebElement) and elem.tag_name.lower() in ["frame", "iframe"]:
            return self.set_current_frame(elem)
        else:
            # NotSupportedOperation
            return True



    def get(self, desc:Descriptor) :
        if is_element(desc):
            return self.get_element(desc)
        elif is_window(desc):
            return self.get_window_handle(desc)
        elif is_alert(desc):
            return self.get_alert(desc)
        else:
            # TODO: exception
            return None


    def get_all(self, desc:Descriptor) :
        if is_element(desc):
            return self.get_elements(desc)
        else:
            # NotSupportedOperation
            return None

    def get_element(self, desc: Descriptor) -> Union[WebElement, None]:
        timeout = get_or(desc.timeout(), self.__timeout)
        try:
            return WebDriverWait(self.__driver, timeout).until(
                EC.element_to_be_clickable((desc.by(), desc.path())))
        except Exception as e:
            # print(f"ERROR: Failed to get an element. {e}")
            return None

    def get_elements(self, desc: Descriptor) -> List[WebElement]:
        timeout = get_or(desc.timeout(), self.__timeout)
        try:
            return WebDriverWait(self.__driver, timeout).until(
                                lambda d: [element for element in
                                           d.find_elements(desc.by(), desc.path()) 
                                if element.is_displayed() and element.is_enabled()])
        except Exception as e:
            # print(f"ERROR: Failed to get elements. {e}")
            return []

    def get_window_handle(self, desc: Descriptor):
        timeout = get_or(desc.timeout(), self.__timeout)
        if desc.by() == "title":
            return self.__get_window_handle_with_title(desc.path(), timeout)
        elif desc.by() == "url":
            return self.__get_window_handle_with_url(desc.path(), timeout)
        else:
            # TODO: report failure
            return None

    def __get_window_handle_with_title(self, title, timeout):
        def _get_window_handle(driver: WebDriver, title: str):
            current = driver.current_window_handle
            result = None
            handles = driver.window_handles
            handles.remove(current)
            for handle in handles:
                driver.switch_to.window(handle)
                if driver.title.find(title) >= 0:
                    result = handle
                    break
            driver.switch_to.window(current)
            return result
        return wait(lambda: _get_window_handle(self.__driver, title), timeout=timeout)

    def __get_window_handle_with_url(self, url, timeout):
        def _get_window_handle(driver: WebDriver, title: str):
            current = driver.current_window_handle
            result = None
            handles = driver.window_handles
            handles.remove(current)
            for handle in handles:
                driver.switch_to.window(handle)
                if driver.current_url.find(url) >= 0:
                    result = handle
                    break
            driver.switch_to.window(current)
            return result

        return wait(lambda: _get_window_handle(self.__driver, url), timeout=timeout)

    def close_other_windows(self):
        """
        Close all windows exept for default one. 
        """
        current = self.__driver.current_window_handle
        handles = self.__driver.window_handles
        handles.remove(current)
        for handle in handles:
            if current == handle:
                continue
            self.__driver.switch_to.window(handle)
            self.__driver.close()
        self.__driver.switch_to.window(current)


    def get_alert(self, desc:Descriptor):
        timeout = get_or(desc.timeout(), self.__timeout)
        try:
            WebDriverWait(self.__driver, timeout).until(
                EC.alert_is_present(), "Can not find an alert window")

            alert = self.__driver.switch_to.alert
            if not desc.path() in alert.text:
                return None
            return alert
        except Exception:
            # print(f"ERROR: Failed to get an alert. {e}")
            return None


    def get_default_window_handle(self):
        return self.__default_window_handle


    def get_text(self, element) -> str:
        if isinstance(element, WebElement):
            return element.text
        else:
            # TODO: report error
            return ""


    def __click(self, element: WebElement):
        if not self.__driver or not element:
            return False
        try:
            element.click()
        except:
            self.__driver.execute_script("arguments[0].click();", element)
        return True


    def click(self, descriptor:Descriptor):
        elem = self.get(descriptor)
        if not elem:
            return False

        if not isinstance(elem, WebElement):
            return False

        differ = get_or(descriptor.differ, self.__differ)

        if differ:
            time.sleep(differ)

        return self.__click(elem)


    def clicks(self, descriptor:Descriptor, num_samples):
        elems = self.get_all(descriptor)
        if not elems:
            return False

        differ = get_or(descriptor.differ(), self.__differ)
        success = True
        for elem in elems:
            if differ:
                time.sleep(differ)
            if not self.__click(elem):
                success = False

        return success


    def __type(self, element: WebElement, text: str):
        element.clear()
        if element.get_attribute('value'):
            return False
        element.send_keys(text)
        return True

    def type(self, desc:Descriptor, text):
        elem = self.get(desc)
        if not elem:
            return False
        if not isinstance(elem, WebElement):
            return False

        differ = get_or(desc.differ(), self.__differ)
        if differ:
            time.sleep(differ)

        return self.__type(elem, text)


    def execute_script(self, script, element):
        if not (script and element):
            return False
        self.__driver.execute_script(script, element)
        return True

    def select(self, element: WebElement, text: str):
        select = Select(element)
        if not select:
            return False
        select.select_by_visible_text(text)
        return True

    def accept(self, element):
        if not element:
            return False
        else:
            element.accept()
            return True

    def go(self, target):
        if target.by() is "url": 
            self.__driver.get(target.path())
            return True
        else:
            # NotSupportedDescriptor
            return False

    def get_url(self):
        return self.__driver.current_url

    def set_current_window(self, handle):
        if self.__driver.current_window_handle == handle:
            return
        self.__driver.switch_to.window(handle)

    def set_current_frame(self, frame: WebElement):
        if frame:
            self.__current_frame = frame
            self.__driver.switch_to.frame(frame)
        else:
            self.__driver.switch_to.default_content()

    def set_default_frame(self):
        self.__driver.switch_to.default_content()


    def get_current_frame(self):
        return self.__current_frame





