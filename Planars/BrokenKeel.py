from Buff import Buff
from Planar import Planar
from Attributes import *


class BrokenKeel(Planar):
    name = "Broken Keel"

    def __init__(self, wearerRole: Role):
        super().__init__(wearerRole)

    def equip(self):
        buffList, debuffList, advList, delayList = super().equip()
        buffList.append(Buff("KeelEFFRES", StatTypes.ERS_PERCENT, 0.10, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        buffList.append(Buff(f"KeelCD({self.wearerRole.name})", StatTypes.CD_PERCENT, 0.10, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        return buffList, debuffList, advList, delayList
