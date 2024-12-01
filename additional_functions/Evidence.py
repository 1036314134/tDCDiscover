class Evidences:
    """
    证据的结构体
    """
    def __init__(self, num, sat):
        """
        :param num: 相同证据的数量
        :param sat: 满足谓词集
        """
        self.num = num
        self.sat = sat
        self.canhit = True
        self.btips = set()

    def addtime(self, time):
        self.num = self.num + time

    def addpres(self, pres):
        self.sat.add(pres)

    def addevi(self, evi):
        self.sat = evi

    def num(self):
        return self.num

    def sat(self):
        return self.sat

    def btips(self):
        return self.btips

    def addbtip(self, i):
        self.btips.add(i)

    def addbtips(self, set):
        self.btips = set

    def removebtip(self, i):
        self.btips.remove(i)

    def changenum(self):
        self.num = len(self.btips)