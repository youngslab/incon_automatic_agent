
# pyautogui
import pyautogui
import pyperclip
import autoit

from .utils import wait

import time


class Context:
    def __init__(self, default_timeout=60, default_differed=0, default_confidence=.9, default_grayscale=True):
        self.default_timeout = default_timeout
        self.default_differed = default_differed
        self.default_confidence = default_confidence
        self.default_grayscale = default_grayscale

    def get_position(self, img, timeout, confidence, grayscale):
        """
        Get a center position of the image
        """
        return wait(lambda: pyautogui.locateCenterOnScreen(
            self.img, grayscale=grayscale, confidence=confidence), timeout=timeout)

    def wait_no_image(self, img, timeout, confidence, grayscale) -> bool:
        """
        Wait until the image disappears
        """
        return wait(lambda: pyautogui.locateCenterOnScreen(
            self.img, grayscale=grayscale, confidence=confidence) is None, timeout=timeout)

    def activate(self, window, timeout):
        """
        Using Autoit APIs, wait until a window activated.
        """
        try:
            autoit.win_wait(window, timeout=timeout)
        except Exception as e:
            print(f"ERROR: Failed to find a window. window={window}, e={e}")
            return False

        try:
            autoit.win_activate(window, timeout=timeout)
        except Exception as e:
            print(
                f"ERROR: Failed to activate a window. window={window}, e={e}")
            return False

        return autoit.win_active(window)

    def click(self, pos):
        if pos is None:
            print(f"Can't click a empty position")
            return False

        pyautogui.click(pos)
        return True

    def type(self, pos, text: str, differed=1):
        if self.click(pos):
            return False

        time.sleep(differed)
        pyautogui.typewrite(text)
        return True


class ControlElement:
    """
    autoit's wapper 
    """

    def __init__(self, context: Context, window, contorl):
        self.context = context
        self.window = window
        self.contorl = contorl

    def do(self, func, *, timeout=None, differed=None):
        if timeout is None:
            timeout = self.context.default_timeout

        if differed is None:
            differed = self.context.default_differed

        if self.context.activate(self.window, timeout=timeout):
            print(f"ERROR: Failed to activate window. {self.window}")
            return False

        if differed:
            time.sleep(differed)

        return func()

    def click(self, *, timeout=None, differed=None):
        if not self.do(lambda: autoit.control_click(self.window, self.contorl),
                       timeout=timeout, differed=differed):
            print(
                f"ERROR: Failed to click an element. window={self.window}, element={self.element}")
            return False
        return True

    def type(self, text, *, timeout=None, differed=None):
        if not self.do(lambda: autoit.control_set_text(self.window, self.contorl, text),
                       timeout=timeout, differed=differed):
            print(
                f"ERROR: Failed to type an element. window={self.window}, element={self.element}")
            return False
        return True


class ImageElement:

    def __init__(self, func, context: Context, window, image):
        self.context = context
        self.window = window
        self.image = image

    def do(self, func, *, timeout=None, differed=None, grayscale=None, confidence=None):
        if timeout is None:
            timeout = self.context.default_timeout

        if differed is None:
            differed = self.context.default_differed

        if grayscale is None:
            grayscale = self.context.default_grayscale

        if confidence is None:
            confidence = self.context.default_confidence

        if self.context.activate(self.window, timeout=timeout):
            print(f"ERROR: Failed to activate window. {self.window}")
            return False

        position = self.context.get_position(self.image)
        if not position:
            print(f"ERROR: Failed to find an image position. {self.image}")
            return False

        if differed:
            time.sleep(differed)

        return func(position)

    def click(self, *, timeout=None, differed=None, grayscale=None, confidence=None):
        if not self.do(lambda pos: self.context.click(pos),
                       timeout=timeout, differed=differed,
                       grayscale=grayscale, confidence=confidence):
            print(f"ERROR: Failed to click an element. img={self.image}")
            return False
        return True

    def type(self, text, *, timeout=None, differed=None, grayscale=None, confidence=None):
        if not self.do(lambda pos: self.context.type(pos, text),
                       timeout=timeout, differed=differed,
                       grayscale=grayscale, confidence=confidence):
            print(f"ERROR: Failed to type an element. img={self.image}")
            return False
        return True
