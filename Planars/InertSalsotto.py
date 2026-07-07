from Buff import Buff
from Attributes import *
from Planar import Planar


class InertSalsotto(Planar):
    name = "Inert Salsotto"

    def __init__(self, wearerRole: Role):
        super().__init__(wearerRole)

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(
            Buff("SalsottoCR", StatTypes.CR_PERCENT, 0.08, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(
            Buff("SalsottoDMG", StatTypes.DMG_PERCENT, 0.15, self.wearerRole, [AtkType.ULT, AtkType.FUA], 1, 1, Role.SELF,
                 TickDown.PERM))
        return bl, dbl, al, dl, hl, sl