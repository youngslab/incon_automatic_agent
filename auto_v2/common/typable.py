
from abc import ABC, abstractmethod

class Typeable(ABC):
    @abstractmethod
    def type(self, str) -> bool:
        pass
