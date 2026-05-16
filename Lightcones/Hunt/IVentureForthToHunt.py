from Lightcone import Lightcone
from Buff import Buff
from Attributes import *


class IVentureForthToHunt(Lightcone):
    name = "I Venture Forth to Hunt"
    path = Path.HUNT
    baseHP = 952.6
    baseATK = 635.04
    baseDEF = 463.05

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        crBuff = self.level * 0.025 + 0.125
        bl.append(
            Buff("VentureCR", StatTypes.CR_PERCENT, crBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useFua(enemyID)
        shredBuff = self.level * 0.03 + 0.24
        bl.append(
            Buff("VentureSHRED", StatTypes.SHRED, shredBuff, self.wearerRole, [AtkType.ULT], 2, 2, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl


class VentureForthFeixiao(IVentureForthToHunt):
    name = "I Venture Forth to Hunt"
    path = Path.HUNT
    baseHP = 952.6
    baseATK = 635.04
    baseDEF = 463.05

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useSkl(enemyID)
        shredBuff = self.level * 0.03 + 0.24
        bl.append(
            Buff("VentureSHRED", StatTypes.SHRED, shredBuff, self.wearerRole, [AtkType.ALL], 3, 2, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt(enemyID)
        shredBuff = self.level * 0.03 + 0.24
        bl.append(
            Buff("VentureSHRED", StatTypes.SHRED, shredBuff, self.wearerRole, [AtkType.ULT], 2, 2, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl


