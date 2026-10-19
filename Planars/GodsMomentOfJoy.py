from Buff import Buff
from Attributes import *
from Planar import Planar
from MainFunctions import Special
from Result import Result
from Turn_Text import Turn
from Delay_Text import Advance


class GodsMomentOfJoy(Planar):
    name = "God's Moment of Joy"

    def __init__(self, wearerRole: Role):
        super().__init__(wearerRole)

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("GodsMomentSPD", StatTypes.SPD_PERCENT, 0.06, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        al.append(Advance("GodsMomentADV", self.wearerRole, 0.4))
        return bl, dbl, al, dl, hl, sl