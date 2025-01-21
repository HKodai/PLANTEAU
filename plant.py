from abc import ABC, abstractmethod


class Plant(ABC): # 植物のクラス
    def __init__(self, height):
        self.height = height # 植物の高さ(単位:m)

    @abstractmethod
    def grow(self, sunlight):
        # sunlight: 1日の日照時間(単位:時間)
        # heightを更新する
        pass


class DeciduousTree(Plant): # 落葉樹のクラス
    @abstractmethod
    def color(self, month): # 月によって葉の色を返すメソッド
        pass

    @abstractmethod
    def fall(self, month): # 月によって葉が落ちる量を返すメソッド
        pass


class Gingko(DeciduousTree): # イチョウのクラス
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
    
# 植物のクラスを作る場合は、Plantクラスを継承して、growメソッドを実装する必要がある。
# また、落葉樹のクラスを作る場合は、DeciduousTreeクラスを継承して、colorメソッドとfallメソッドを実装する必要がある。
