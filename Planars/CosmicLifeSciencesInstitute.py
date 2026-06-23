from Buff import Buff
from Planar import Planar
from MainFunctions import Special
from Attributes import *


class CosmicLifeSciencesInstitute(Planar):
    name = "Cosmic Life Sciences Institute"

    def __init__(self, wearerRole: Role):
        super().__init__(wearerRole)

    def specialStart(self, special: Special):
        bl, dbl, al, dl, hl = super().specialStart(special)
        if special.specialName == "Saber" :
            EnergyStat = special.attr2
            if EnergyStat >= 200:
                bl.append(Buff("CosmicLifeDMG", StatTypes.DMG_PERCENT, min((EnergyStat-200)*0.02,0.32), self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        if special.specialName == "Gilgamesh" :
            EnergyStat = special.attr5
            if EnergyStat >= 200:
                bl.append(Buff("CosmicLifeDMG", StatTypes.DMG_PERCENT, min((EnergyStat-200)*0.02,0.32), self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl
