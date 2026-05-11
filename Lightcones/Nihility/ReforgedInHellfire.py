from Buff import *
from Lightcone import Lightcone
from Attributes import *

class ReforgedInHellfire(Lightcone):
    name = "Reforged in Hellfire"
    path = Path.NIHILITY
    baseHP = 1270
    baseATK = 476
    baseDEF = 463

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.075 + 0.225
        bl.append(Buff("ReforgedHP", StatTypes.HP_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        bl.append(Buff("ReforgedERR", StatTypes.ERR_F, 20, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.START))
        return bl, dbl, al, dl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useSkl()
        purgatoryCD = self.level * 0.075 + 0.225
        dbl.append(Debuff("ReforgedPurgatoryAllCD", self.wearerRole, StatTypes.CD_PERCENT,purgatoryCD, Role.ALL, [AtkType.ALL], 2, 1))
        return bl, dbl, al, dl, hl