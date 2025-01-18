from abc import ABC, abstractmethod


class Plant(ABC):
    def __init__(self, height):
        self.height = height

    @abstractmethod
    def grow(self, sunlight):
        pass


class DeciduousTree(Plant):
    @abstractmethod
    def color(self, month):
        pass

    @abstractmethod
    def fall(self, month):
        pass


class Gingko(DeciduousTree):
    def __init__(self, height):
        super().__init__(height)

    def grow(self, sunlight):
        self.height = min(self.height + sunlight * 0.0001, 30)

    def color(self, month):
        if month == 11 or month == 12:
            return "yellow"
        return "green"

    def fall(self, month):
        if month == 12:
            return 1700
        return 0
