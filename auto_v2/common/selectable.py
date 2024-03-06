

from abc import ABC, abstractmethod

# Abstract Base Class
class Selectable(ABC):
    @abstractmethod
    def select(self) -> bool:
        pass
