


from abc import ABC, abstractmethod
from .descriptor import Descriptor

class Context(ABC):
    @abstractmethod
    def activate(self, elem):
        pass


    @abstractmethod
    def click(self, elem):
        pass

    @abstractmethod
    def type(self, elem, text:str):
        pass
