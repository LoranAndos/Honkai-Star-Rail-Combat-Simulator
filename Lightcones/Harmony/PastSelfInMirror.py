from Buff import Buff
from Delay_Text import *
from Lightcone import Lightcone


class PastSelfInMirror(Lightcone):
    name = "Past Self in Mirror"
    path = Path.HARMONY
    baseHP = 1058.4
    baseATK = 529.20
    baseDEF = 529.20

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        be = self.level * 0.1 + 0.5
        bl.append(Buff("MirrorBE", StatTypes.BE_PERCENT, be, self.wearerRole))
        bl.append(Buff("MirrorERR", StatTypes.ERR_T, self.level * 0.025 + 0.075, Role.ALL))
        return bl, dbl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt(enemyID)
        dmg = self.level * 0.04 + 0.2
        bl.append(Buff("MirrorDMG", StatTypes.DMG_PERCENT, dmg, Role.ALL, turns=3, tdType=TickDown.END))
        bl.append(Buff("MirrorSP", StatTypes.SKLPT, 1, self.wearerRole))
        return bl, dbl, al, dl, hl