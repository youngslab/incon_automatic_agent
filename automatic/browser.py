
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select


# wait elements
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# exception
from selenium.common.exceptions import StaleElementReferenceException

import random


# types
from enum import Enum
from typing import Tuple, Union, List

# wait
import time
from .utils import wait


class Context:
    def __init__(self, driver: WebDriver, home, default_timeout=60, default_differed=0):
        self.__driver = driver
        self.__current_frame = None
        self.__default_window_handle = driver.current_window_handle
        # move to the homepage
        self.set_url(home)
        self.default_timeout = default_timeout
        self.default_differed = default_differed

    def close_other_windows(self):
        """
        Close all windows exept for default one. 
        """
        current = self.__driver.current_window_handle
        handles = self.__driver.window_handles
        handles.remove(current)
        for handle in handles:
            self.__driver.switch_to.window(handle)
            self.__driver.close()
        self.__driver.switch_to.window(current)

    def get_clickable(self, by: str, path: str, timeout: int) -> Union[WebElement, None]:
        try:
            return WebDriverWait(self.__driver, timeout).until(
                EC.element_to_be_clickable((by, path)))
        except Exception as e:
            # print(f"ERROR: Failed to get a clickable element. {e}")
            return None

    def get_element(self, by: str, path: str, timeout: int) -> Union[WebElement, None]:
        try:
            return WebDriverWait(self.__driver, timeout).until(
                EC.presence_of_element_located((by, path)))
        except Exception as e:
            # print(f"ERROR: Failed to get an element. {e}")
            return None

    def get_elements(self, by: str, path: str, timeout: int) -> List[WebElement]:
        try:
            return WebDriverWait(self.__driver, timeout).until(
                EC.presence_of_all_elements_located((by, path)))
        except Exception as e:
            # print(f"ERROR: Failed to get elements. {e}")
            return []

    def get_alert(self, timeout: int):
        try:
            WebDriverWait(self.__driver, timeout).until(
                EC.alert_is_present(), "Can not find an alert window")
            return self.__driver.switch_to.alert
        except Exception as e:
            print(f"ERROR: Failed to get an alert. {e}")
            return None

    def get_default_window_handle(self):
        return self.__default_window_handle

    def get_window_handle_with_title(self, title, timeout):
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

    def get_window_handle_with_url(self, url, timeout):
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

    def click(self, element: WebElement):
        if not self.__driver or not element:
            return False
        try:
            element.click()
        except:
            self.__driver.execute_script("arguments[0].click();", element)
        return True

    def type(self, element: WebElement, text: str):
        element.clear()
        if element.get_attribute('value'):
            return False
        element.send_keys(text)
        return True

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

    def set_url(self, url):
        return self.__driver.get(url)

    def get_url(self):
        return self.__driver.current_url

    def set_window(self, handle):
        if self.__driver.current_window_handle == handle:
            return
        self.__driver.switch_to.window(handle)

    def set_current_frame(self, frame: WebElement):
        if frame:
            self.__current_frame = frame
            self.__driver.switch_to.frame(frame)
        else:
            self.__driver.switch_to.default_content()

    def get_current_frame(self):
        return self.__current_frame


class Window:
    # handle: default window doesn't need to have its title or url
    # title: search winddow handle based on title
    # ulr: search winddow handle based on url
    def __init__(self, context: Context, *, url: str = None, title: str = None, handle=None):
        self.__context = context
        self.__url = url
        self.__title = title
        self.__handle = handle

        # It's default window
        if not self.__handle and not self.__title and not self.__url:
            self.__handle = context.get_default_window_handle()

    def activate(self, *, timeout=None):
        if timeout is None:
            timeout = self.__context.default_timeout
        # Update handle
        if not self.__handle:
            if self.__title:
                self.__handle = self.__context.get_window_handle_with_title(
                    self.__title, timeout=timeout)
            elif self.__url:
                self.__handle = self.__context.get_window_handle_with_url(
                    self.__url, timeout=timeout)

        # Validate
        if not self.__handle:
            return False

        self.__context.set_window(self.__handle)
        return True

    def __str__(self):
        return f"[window, handle={self.__handle}]"


class Frame():
    def __init__(self, context: Context,  *, by: str = None, path: str = None, parent=None, id=None, desc=None):
        self.context = context
        self.element = None
        self.by = by
        self.path = path
        self.parent = parent
        self.is_default = True if by is None and path is None else False
        # setup default parent
        if not parent:
            self.parent = Frame(context, parent=Window(context))

        self.id = id
        self.desc = desc

    def __activate(self, *, timeout=None):
        if timeout is None:
            timeout = self.context.default_timeout

        if not self.parent.activate(timeout=timeout):
            print(f"ERROR: Can't activate parent={self.parent}")
            return False

        if self.is_default:
            self.context.set_current_frame(None)
            return True

        # if self.element is None:
        self.element = self.context.get_element(
            self.by, self.path, timeout=timeout)

        # Can't find a frame element.
        if self.element is None:
            print(f"ERROR: Cant' find frame element={self}.")
            return False

        self.context.set_current_frame(self.element)
        # print(f"INFO: Set a current fame. {self}")
        return True

    def activate(self, *, timeout=None):
        try:
            return self.__activate(timeout=timeout)
        except StaleElementReferenceException as e:
            print("ERROR: StaleElementRefereceException. Retry")
            self.element = None
            return self.__activate(timeout=timeout)

    def __str__(self):
        if self.desc:
            return f"[desc={self.desc}, by={self.by}, path={self.path}]"
        else:
            return f"[by={self.by}, path={self.path}]"

    def exist(self, *, timeout=None):
        if timeout is None:
            timeout = self.context.default_timeout

        # make parent activated
        if not self.parent.activate():
            print("ERROR: Can't activate parent")
            return False

        # if not self.element:
            # find an element
        self.element = self.context.get_clickable(
            self.by, self.path, timeout=timeout)

        return True if self.element else False


class Alert:
    def __init__(self, context: Context, *, parent=None):
        self.context = context
        self.parent = parent
        if self.parent is None:
            self.parent = Window(context)

    def accept(self, text: str, *, timeout=None, differed=None):
        if timeout is None:
            timeout = self.context.default_timeout

        if differed is None:
            differed = self.context.default_differed

        alert = self.context.get_alert(timeout=timeout)
        if not alert:
            print(f"ERROR: Can't find the alert.")
            return False

        if alert.text.find(text) < 0:
            print(
                f"ERROR: Can't find the text in the alert. expected:{text}, real:{alert.text}")
            return False

        if differed:
            time.sleep(differed)

        alert.accept()
        return True


class Element:

    def __init__(self, context: Context, by: str, path: str, *, parent=None, desc=None):
        self.context = context
        self.element = None
        self.by = by
        self.path = path
        self.parent = parent
        if self.parent is None:
            self.parent = Frame(context)

        # if parent is windows directly. Needs to wraps default Frames.
        if isinstance(self.parent, Window):
            self.parent = Frame(context, parent=self.parent)

        self.desc = desc

        #  각 element들 마다 element를 가져오는 방식 및 행동 방식이 각기 다르다.
        # 이에 대해 구현해 준다.

    def __str__(self):
        if self.desc:
            return f"[desc={self.desc}]"
        else:
            return f"[by={self.by}, path={self.path}]"

    def exist(self, *, timeout=None):
        if timeout is None:
            timeout = self.context.default_timeout

        # make parent activated
        if not self.parent.activate():
            print("ERROR: Can't activate parent")
            return False

        # if not self.element:
            # find an element
        self.element = self.context.get_clickable(
            self.by, self.path, timeout=timeout)

        return True if self.element else False


class SelectableElement(Element):

    def select(self, text: str, *, timeout=None, differed=None):
        if timeout is None:
            timeout = self.context.default_timeout

        if differed is None:
            differed = self.context.default_differed

        if not self.parent.activate():
            return False

        # if not self.element:
            # find an element
        self.element = self.context.get_clickable(
            self.by, self.path, timeout=timeout)

        # validate
        if not self.element:
            print(f"ERROR: Failed to find an element. {self}")
            return False

        if differed:
            time.sleep(differed)

        return self.context.select(self.element, text)


class ClickableElement(Element):

    # browser_click: input element doesn't have click method. But webpage
    #                require click events. In this case, we need to click
    #                element with browser feature.
    def click(self, *, timeout=None, differed=None, brower_click=False):
        if timeout is None:
            timeout = self.context.default_timeout

        if differed is None:
            differed = self.context.default_differed

        # make parent activated
        if not self.parent.activate():
            print(f"ERROR: Failed to activate parent. {self.parnet}")
            return False

        # if not self.element:
            # find an element
        self.element = self.context.get_clickable(
            self.by, self.path, timeout=timeout)

        # validate
        if not self.element:
            print(f"ERROR: Failed to find an element. {self}")
            return False

        if differed:
            time.sleep(differed)

        return self.context.click(self.element)


class ClickableElements(Element):
    def click(self, num_elements, *, timeout=None, differed=None, brower_click=False):
        if timeout is None:
            timeout = self.context.default_timeout

        if differed is None:
            differed = self.context.default_differed

        # make parent activated
        if not self.parent.activate():
            print(f"ERROR: Failed to find an element. {self}")
            return False

        # if not self.element:
            # find an element
        self.element = self.context.get_elements(
            self.by, self.path, timeout=timeout)

        if not self.element:
            print(f"ERROR: Can't find elements. {self}")
            return False

        # XXX: __element is the group object for this class.
        elements = self.element
        elements = random.sample(elements, k=num_elements)

        for element in elements:
            if differed:
                time.sleep(differed)
            if not self.context.click(element):
                return False
        return True


class TypeableElement(Element):
    def type(self, text, *, timeout=None, differed=None, force=False):
        if timeout is None:
            timeout = self.context.default_timeout

        if differed is None:
            differed = self.context.default_differed

        # make parent activated
        if not self.parent.activate():
            print(f"ERROR: Can't activate parent={self.parent}")
            return False

        # find an element
        self.element = self.context.get_clickable(
            self.by, self.path, timeout=timeout)

        # validate
        if not self.element:
            print(f"ERROR: Can't find an element. {self}")
            return False

        if differed:
            time.sleep(differed)

        if force:
            return self.context.execute_script(f'arguments[0].value = "{text}"', self.element)
        else:
            return self.context.type(self.element, text)


class TextableElement(Element):
    def text(self, *, timeout=None, differed=None):
        if timeout is None:
            timeout = self.context.default_timeout

        if differed is None:
            differed = self.context.default_differed

        # make parent activated
        if not self.parent.activate():
            print(f"ERROR: Can't activate parent={self.parent}")
            return False

        # find an element
        self.element = self.context.get_clickable(
            self.by, self.path, timeout=timeout)

        # validate
        if not self.element:
            print(f"ERROR: Can't find element={self}")
            return False

        if differed:
            time.sleep(differed)

        return self.element.text
