from Lightcone import Lightcone
from Buff import Buff
from Attributes import *


class CruisingInTheStellarSea(Lightcone):
    name = "Cruising in the Stellar Sea"
    path = Path.HUNT
    baseHP = 952.6
    baseATK = 529.2
    baseDEF = 463.05

    def __init__(self, wearerRole, level: int = 5, uptime: float = 0.5):
        super().__init__(wearerRole, level)
        self.uptime = uptime

    def equip(self):
        buffList, debuffList, advList, delayList = super().equip()
        crBuff = (self.level * 0.02 + 0.06) + (self.level * 0.02 + 0.06) * self.uptime
        buffList.append(
            Buff("CruisingCR", StatTypes.CR_PERCENT, crBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        atkBuff = (self.level * 0.05 + 0.15) * self.uptime
        buffList.append(Buff("CruisingATK", StatTypes.ATK_PERCENT, atkBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                             TickDown.PERM))
        return buffList, debuffList, advList, delayList
