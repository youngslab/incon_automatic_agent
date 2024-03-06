
from abc import ABC, abstractmethod

class Clickable(ABC):
    @abstractmethod
    def click(self,*,timeout=0, differ=0) -> bool:
        # [timout and differ]'s default value will be redefined from children
        pass
