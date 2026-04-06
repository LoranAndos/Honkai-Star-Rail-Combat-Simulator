from Buff import *
from Lightcone import Lightcone
from Attributes import *


class IntoTheUnreachableVeil(Lightcone):
    name = "Into the Unreachable Veil"
    path = Path.ERUDITION
    baseHP = 953
    baseATK = 635
    baseDEF = 463

    def __init__(self, wearerRole, level=5, ultCost=220):
        super().__init__(wearerRole, level)
        self.ultCost = ultCost

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        crAmount = self.level * 0.02 + 0.10
        bl.append(Buff("UnreachableVeilCR", StatTypes.CR_PERCENT, crAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt()
        buffAmount = self.level * 0.10 + 0.50
        bl.append(Buff("UnreachableVeilDB_SKL", StatTypes.DMG_PERCENT, buffAmount, self.wearerRole, [AtkType.SKL], 3, 1, Role.SELF, TickDown.END))
        bl.append(Buff("UnreachableVeilDB_ULT", StatTypes.DMG_PERCENT, buffAmount, self.wearerRole, [AtkType.ULT], 3, 1, Role.SELF, TickDown.END))
        if self.ultCost >= 140:
            bl.append(Buff("UnreachableVeilSP", StatTypes.SKLPT, 1, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        return bl, dbl, al, dl, hl