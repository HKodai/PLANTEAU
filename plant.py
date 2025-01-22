from abc import ABC, abstractmethod


class Plant(ABC): # 植物のクラス
    def __init__(self, height):
        self.height = height # 植物の高さ(単位:m)

    @abstractmethod
    def grow(self, sunlight):
        # sunlight: 1日の日照時間(単位:時間)
        # heightを更新する
        pass

    @abstractmethod
    def state(self, month):
        # 植物の状態を返す
        pass


class Gingko(Plant): # イチョウのクラス
    def __init__(self, height):
        super().__init__(height)

    def grow(self, sunlight):
        self.height = min(self.height + sunlight * 0.0001, 30)

    def state(self, month):
        if 4 <= month <= 9:
            return "green"
        elif 10 <= month <= 11:
            return "yellow"
        else:
            return "noleaves"

class Cherry(Plant):  # 桜のクラス
    def __init__(self, height):
        super().__init__(height)

    def grow(self, sunlight):
        self.height = min(self.height + sunlight * 0.0002, 20)  # 桜はイチョウより成長が早い設定

    def state(self, month):
        if 3 <= month <= 4:  # 3月から4月は開花
            return "pink"
        elif 5 <= month <= 9:  # 5月から9月は緑葉
            return "green"
        elif 10 <= month <= 11:  # 10月から11月は紅葉
            return "orange"
        else:  # 12月から2月は葉がない状態
            return "noleaves"
