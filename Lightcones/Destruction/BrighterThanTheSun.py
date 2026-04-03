from Buff import *
from Lightcone import Lightcone
from Attributes import *


class BrighterThanTheSun(Lightcone):
    name = "Brighter Than the Sun"
    path = Path.DESTRUCTION
    baseHP = 1058
    baseATK = 635
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        crAmount = self.level * 0.03 + 0.15
        bl.append(Buff("BrighterThanTheSunCR", StatTypes.CR_PERCENT, crAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useBsc()
        atkAmount = self.level * 0.03 + 0.15
        errAmount = self.level * 0.01 + 0.05
        bl.append(Buff("BrighterThanTheSunATK", StatTypes.ATK_PERCENT, atkAmount, self.wearerRole, [AtkType.ALL], 2, 2, Role.SELF, TickDown.END))
        bl.append(Buff("BrighterThanTheSunERR", StatTypes.ERR_PERCENT, errAmount, self.wearerRole, [AtkType.ALL], 2, 2, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl