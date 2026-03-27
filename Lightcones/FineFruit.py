from Buff import *
from Lightcone import Lightcone
from Attributes import *
from math import floor

class FineFruit(Lightcone):
    name = "Fine Fruit"
    path = Path.ABUNDANCE
    baseHP = 953
    baseATK = 318
    baseDEF = 198

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        BuffAmount = floor(self.level * 1.5 + 4.5)
        bl.append(Buff("FineFruitERR_T", StatTypes.ERR_T, BuffAmount, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        return bl, dbl, al, dl, hl