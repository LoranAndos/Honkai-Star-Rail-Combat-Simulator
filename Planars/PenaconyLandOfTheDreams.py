from Buff import Buff
from Attributes import *
from Planar import Planar


class PenaconyLandOfTheDreams(Planar):
    name = "Penacony, Land of the Dreams"

    def __init__(self, wearerRole: Role, sameEleTeammates: list[Role]):
        super().__init__(wearerRole)
        self.sameEle = sameEleTeammates

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("PenaconyERR", StatTypes.ERR_PERCENT, 0.05, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        for role in self.sameEle:
            bl.append(Buff("PenaconyDMG", StatTypes.DMG_PERCENT, 0.1, role, [AtkType.ALL], 1, 1, role, TickDown.PERM))
        return bl, dbl, al, dl, hl