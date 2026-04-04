from Buff import Buff
from Planar import Planar
from Delay_Text import *
from Attributes import *


class SprightlyVonwacq(Planar):
    name = "Sprightly Vonwacq"

    def __init__(self, wearerRole: Role):
        super().__init__(wearerRole)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("VonwacqERR", StatTypes.ERR_PERCENT, 0.05, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        al.append(Advance("VonwacqADV", self.wearerRole, 0.4))
        return bl, dbl, al, dl, hl