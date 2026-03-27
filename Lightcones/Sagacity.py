from Buff import *
from Lightcone import Lightcone
from Attributes import *

class Sagacity(Lightcone):
    name = "Sagacity"
    path = Path.ERUDITION
    baseHP = 741
    baseATK = 370
    baseDEF = 265

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt(enemyID)
        BuffAmount = self.level * 0.06 + 0.18
        bl.append(Buff("Sagacity_ATK", StatTypes.ATK_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 2, 1, Role.SELF,TickDown.START))
        return bl, dbl, al, dl, hl