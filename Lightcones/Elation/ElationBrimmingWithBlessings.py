from Buff import *
from Lightcone import Lightcone
from Attributes import *

class ElationBrimmingWithBlessings(Lightcone):
    name = "Elation Brimming With Blessings"
    path = Path.ELATION
    baseHP = 953
    baseATK = 529
    baseDEF = 463

    def __init__(self, wearerRole, level=5, targetRole=Role.DPS):
        super().__init__(wearerRole, level)
        self.targetRole = targetRole

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        atkAmount = self.level * 0.05 + 0.15
        bl.append(Buff("ElationBrimmingATK", StatTypes.ATK_PERCENT, atkAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

class ElationBrimmingWithBlessingsElationMC(ElationBrimmingWithBlessings):

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt(enemyID)
        elaAmount = self.level * 0.03 + 0.09
        bl.append(Buff("ElationBrimmingELA_ULT", StatTypes.ELA, elaAmount, self.targetRole, [AtkType.ALL], 2, 1, self.targetRole, TickDown.END))
        return bl, dbl, al, dl, hl