from Buff import *
from Lightcone import Lightcone
from Attributes import *

class MemorysCurtainNeverFalls(Lightcone):
    name = "Memory's Curtain Never Falls"
    path = Path.REMEMBRANCE
    baseHP = 1058
    baseATK = 529
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        spdAmount = self.level * 0.015 + 0.045
        bl.append(Buff("MemorysCurtainSPD", StatTypes.SPD_PERCENT, spdAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useSkl(enemyID)
        BuffAmount = self.level * 0.02 + 0.06
        bl.append(Buff("MemorysCurtainDB_SKL", StatTypes.DMG_PERCENT, BuffAmount, Role.ALL, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl