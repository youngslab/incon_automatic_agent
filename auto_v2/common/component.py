

from .descriptor import Descriptor

class Component:
    def __init__(self, desc:Descriptor, data):
        self.__descriptor = desc
        self.__data = data

    def data(self):
        return self.__data

    def desc(self):
        return self.__descriptor

