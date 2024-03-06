from abc import ABC, abstractmethod
from typing import Union

class Descriptor(ABC):
    def __init__(self, desc, path, *, parent: 'Union[None, Descriptor]' =None,
                 timeout=None, differ=0):
        self.__path= path
        self.__desc = desc
        self.__parent = parent
        self.__timeout = timeout
        self.__differ = differ

    @abstractmethod
    def by(self) -> str:
        pass

    def path(self) -> str:
        return self.__path

    def desc(self) -> str:
        return self.__desc

    def parent(self) -> 'Union[None, Descriptor]':
        return self.__parent

    def timeout(self):
        return self.__timeout

    def differ(self):
        return self.__differ

    def __str__(self):
        return self.desc()

