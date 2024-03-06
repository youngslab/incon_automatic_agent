
from ..common import Descriptor
from typing import Union


# Element Descriptor
class Image(Descriptor):
    def __init__(self, desc, path, *, parent: 'Union[None, Descriptor]' =None,
                 timeout=None, confidence=None, grayscale=None):
        self.__confidence = confidence
        self.__grayscale = grayscale
        super().__init__(desc, path, parent=parent, timeout=timeout)


    def by(self) -> str:
        return "image"

    def grayscale(self):
        return self.__grayscale

    def confidence(self):
        return self.__confidence

class Control(Descriptor):
    def by(self) -> str:
        return "control"


class Title(Descriptor):
    def by(self) -> str:
        return "title"


def is_window(desc:Descriptor):
    return True if desc.by() in ["title"] else False

def is_image(desc:Descriptor):
    return True if desc.by() == "image" else False

def is_control(desc:Descriptor):
    return True if desc.by() == "control" else False
