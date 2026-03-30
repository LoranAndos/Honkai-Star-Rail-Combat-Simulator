from Buff import Buff
from Attributes import *
from Planar import Planar


class Lushaka(Planar):
    name = "Lushaka, the Sunken Seas"

    def __init__(self, wearerRole: Role, slot1Role=Role.DPS):
        super().__init__(wearerRole)
        self.slot1Role = slot1Role

    def equip(self):
        buffList, debuffList, advList, delayList = super().equip()
        buffList.append(
            Buff("LushakaERR", StatTypes.ERR_PERCENT, 0.05, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        buffList.append(
            Buff(f"LushakaATK({self.wearerRole.name})", StatTypes.ATK_PERCENT, 0.12, self.slot1Role, [AtkType.ALL], 1, 1,
                 Role.SELF, TickDown.PERM))
        return buffList, debuffList, advList, delayList