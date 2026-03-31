from Buff import *
from Lightcone import Lightcone
from Attributes import *


class PastAndFuture(Lightcone):
    name = "Past and Future"
    path = Path.HARMONY
    baseHP = 953
    baseATK = 423
    baseDEF = 397

    def __init__(self, wearerRole, level=5, targetRole=Role.DPS):
        super().__init__(wearerRole, level)
        self.targetRole = targetRole

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl = super().useSkl(enemyID)
        DmgBuff = self.level * 0.04 + 0.12
        bl.append(Buff("PastAndFutureSkillBuff", StatTypes.DMG_PERCENT, DmgBuff, self.targetRole, [AtkType.ALL], 1, 1,self.targetRole, TickDown.END))
        return bl, dbl, al, dl