from Buff import *
from Lightcone import Lightcone
from Attributes import *

class DayOneOfMyNewLife(Lightcone):
    name = "Day One of My New Life"
    path = Path.PRESERVATION
    baseHP = 953
    baseATK = 370
    baseDEF = 463

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        defAmount = self.level * 0.02 + 0.14
        penAmount = self.level * 0.01 + 0.07
        bl.append(Buff("DayOneDEF", StatTypes.DEF_PERCENT, defAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("DayOnePEN", StatTypes.PEN, penAmount, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl