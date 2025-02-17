from Buff import Buff
from Attributes import *
from Planar import Planar


class RutilantArena(Planar):
    name = "Rutilant Arena"

    def __init__(self, wearerRole: Role):
        super().__init__(wearerRole)

    def equip(self):
        bl, dbl, al, dl = super().equip()
        bl.append(
            Buff("RutilantCR", StatTypes.CR_PERCENT, 0.08, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("RutilantBonusDMG", StatTypes.DMG_PERCENT, 0.20, self.wearerRole, [AtkType.BSC, AtkType.SKL], 1, 1,
                       Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl