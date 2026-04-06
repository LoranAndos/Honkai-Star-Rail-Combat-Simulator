from Buff import *
from Lightcone import Lightcone
from Attributes import *

class ButTheBattleIsntOver(Lightcone):
    name = "But the Battle Isn't Over"
    path = Path.HARMONY
    baseHP = 1164
    baseATK = 529
    baseDEF = 463
    UltAmount = 0

    def __init__(self, wearerRole, level=1, targetRole = Role.DPS):
        super().__init__(wearerRole, level)
        self.targetRole = targetRole

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.02 + 0.08
        bl.append(Buff("BattleIsntOverERR", StatTypes.ERR_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useSkl(enemyID)
        DmgAmount = self.level * 0.05 + 0.25
        bl.append(Buff("BattleIsntOverDMG", StatTypes.DMG_PERCENT, DmgAmount, self.targetRole, [AtkType.ALL], 1, 1, self.targetRole, TickDown.END))
        return bl, dbl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt(enemyID)
        if self.UltAmount % 2 == 0:
            bl.append(Buff("BattleIsntOverSP", StatTypes.SKLPT, 1, self.wearerRole))
        self.UltAmount += 1
        return bl, dbl, al, dl, hl