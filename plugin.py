from abc import ABCMeta, abstractmethod
from enum import Enum, unique

@unique
class MsgLevel(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2

class Plugin(metaclass=ABCMeta): 
    @abstractmethod
    def load(self): pass

    @abstractmethod
    def destroy(self): pass
