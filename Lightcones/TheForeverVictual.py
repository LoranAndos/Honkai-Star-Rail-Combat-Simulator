from Buff import *
from Lightcone import Lightcone
from Attributes import *

class TheForeverVictual(Lightcone):
    name = "The Forever Victual"
    path = Path.HARMONY
    baseHP = 953
    baseATK = 476
    baseDEF = 331

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.03 + 0.09
        bl.append(Buff("ForeverVictualATK", StatTypes.ATK_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useSkl(enemyID)
        atkAmount = self.level * 0.02 + 0.06
        bl.append(Buff("ForeverVictual_SKLATK", StatTypes.ATK_PERCENT, atkAmount, self.wearerRole, [AtkType.ALL], 1, 3, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl