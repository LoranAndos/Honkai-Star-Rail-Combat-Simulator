from Buff import Buff
from Attributes import *
from Planar import Planar


class LushakaTheSunkenSeas(Planar):
    name = "Lushaka, the Sunken Seas"

    def __init__(self, wearerRole: Role, slot1Role=Role.DPS):
        super().__init__(wearerRole)
        self.slot1Role = slot1Role

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("LushakaERR", StatTypes.ERR_PERCENT, 0.05, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff(f"LushakaATK({self.wearerRole.name})", StatTypes.ATK_PERCENT, 0.12, self.slot1Role, [AtkType.ALL], 1, 1,Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl