from Lightcone import Lightcone
from Buff import Buff
from Result import Special
from Attributes import *


class BaptismOfPureThought(Lightcone):
    name = "Baptism of Pure Thought"
    path = Path.HUNT
    baseHP = 953
    baseATK = 582
    baseDEF = 529

    targetDebuffs = 0

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        cdBuff = self.level * 0.03 + 0.17
        bl.append(
            Buff("BaptismCD", StatTypes.CD_PERCENT, cdBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useBsc(enemyID)
        cdBuff = (self.level * 0.01 + 0.07) * self.targetDebuffs
        bl.append(Buff("BaptismDebuffCD", StatTypes.CD_PERCENT, cdBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                       TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useSkl(enemyID)
        cdBuff = (self.level * 0.01 + 0.07) * self.targetDebuffs
        bl.append(Buff("BaptismDebuffCD", StatTypes.CD_PERCENT, cdBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                       TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt(enemyID)
        cdBuff = (self.level * 0.01 + 0.07) * self.targetDebuffs
        bl.append(Buff("BaptismDebuffCD", StatTypes.CD_PERCENT, cdBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                       TickDown.PERM))
        dmgBuff = self.level * 0.06 + 0.30
        bl.append(Buff("BaptismDispDMG", StatTypes.DMG_PERCENT, dmgBuff, self.wearerRole, [AtkType.ALL], 2, 1, Role.SELF,
                       TickDown.END))
        shredBuff = self.level * 0.04 + 0.20
        bl.append(Buff("BaptismDispSHRED", StatTypes.SHRED, shredBuff, self.wearerRole, [AtkType.FUA], 2, 1, Role.SELF,
                       TickDown.END))
        return bl, dbl, al, dl, hl


class BaptismFeixiao(BaptismOfPureThought):
    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def specialStart(self, special: Special):
        if special.specialName == "Feixiao" or special.specialName == "FeixiaoTech":
            self.targetDebuffs = min(3.0, special.attr3[0])
        return super().specialStart(special)


class BaptismRatio(BaptismOfPureThought):
    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def specialStart(self, special: Special):
        if special.specialName == "Ratio":
            self.targetDebuffs = min(3.0, special.attr1[0])
        return super().specialStart(special)
