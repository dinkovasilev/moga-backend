from abc import ABC, abstractmethod
from enum import Enum



class Fields(Enum):
    @abstractmethod
    def names_list(): ...
    @abstractmethod
    def values_list(): ...
    @abstractmethod
    def as_dict(): ...