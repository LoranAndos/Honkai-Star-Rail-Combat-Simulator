from Lightcone import Lightcone
from Buff import Buff
from Attributes import *


class MOTP(Lightcone):
    name = "Memories of the Past"
    path = Path.HARMONY
    baseHP = 952.6
    baseATK = 423.36
    baseDEF = 396.90

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        buffList, debuffList, advList, delayList = super().equip()
        breakBuff = self.level * 0.07 + 0.21
        buffList.append(
            Buff("MotpBE", StatTypes.BE_PERCENT, breakBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return buffList, debuffList, advList, delayList

    def useBsc(self, enemyID=-1):
        buffList, debuffList, advList, delayList = super().useBsc(enemyID)
        errGain = self.level + 3
        buffList.append(
            Buff("MotpBonusEnergy", StatTypes.ERR_T, errGain, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return buffList, debuffList, advList, delayList


class MotpHMC(MOTP):
    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl = super().useSkl(enemyID)
        bl.append(Buff("MotpBonusEnergy", StatTypes.ERR_T, self.level + 3, self.wearerRole))
        return bl, dbl, al, dl