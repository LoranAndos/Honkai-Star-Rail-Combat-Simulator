from Buff import *
from Lightcone import Lightcone
from Attributes import *
from math import floor

class IndeliblePromise(Lightcone):
    name = "Indelible Promise"
    path = Path.DESTRUCTION
    baseHP = 953
    baseATK = 476
    baseDEF = 331

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        beAmount = self.level * 0.07 + 0.21
        bl.append(Buff("IndeliblePromiseBE", StatTypes.BE_PERCENT, beAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt()
        crAmount = floor(self.level*3.75 +11.25)
        bl.append(Buff("IndeliblePromiseCR", StatTypes.CR_PERCENT, crAmount/100, self.wearerRole, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl