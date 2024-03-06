

from abc import ABC, abstractmethod

# Abstract Base Class
class Parent(ABC):
    @abstractmethod
    def activate(self,*,timeout=0):
        # timout's default value will be redefined from children
        pass
