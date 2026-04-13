from Buff import *
from Lightcone import Lightcone
from Attributes import *

class IfTimeWereAFlower(Lightcone):
    name = "If Time Were a Flower"
    path = Path.HARMONY
    baseHP = 1270
    baseATK = 529
    baseDEF = 397

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        cdEquipAmount = self.level * 0.06 + 0.30
        cdAmount = self.level * 0.12 + 0.36
        bl.append(Buff("IfTimeWereAFlowerCD_equip", StatTypes.CD_PERCENT, cdEquipAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("IfTimeWereAFlowerERG", StatTypes.ERR_F, 21, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        bl.append(Buff("IfTimeWereAFlowerCD", StatTypes.CD_PERCENT, cdAmount, Role.ALL, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useFua(enemyID)
        cdAmount = self.level * 0.12 + 0.36
        bl.append(Buff("IfTimeWereAFlowerCD_FUA", StatTypes.CD_PERCENT, cdAmount, Role.ALL, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        bl.append(Buff("IfTimeWereAFlowerERG_FUA", StatTypes.ERR_F, 12, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        return bl, dbl, al, dl, hl