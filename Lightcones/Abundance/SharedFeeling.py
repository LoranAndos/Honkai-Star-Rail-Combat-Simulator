from Buff import *
from Lightcone import Lightcone
from Attributes import *
from math import floor

class SharedFeeling(Lightcone):
    name = "Shared Feeling"
    path = Path.ABUNDANCE
    baseHP = 953
    baseATK = 423
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        oghAmount = floor(self.level * 2.5 + 7.5)
        bl.append(Buff("SharedFeelingOGH", StatTypes.OGH_PERCENT, oghAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useSkl(enemyID)
        ERRAmount = self.level * 0.5 + 1.5
        bl.append(Buff("SharedFeeling_SKL", StatTypes.ERR_T, ERRAmount, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        return bl, dbl, al, dl, hl