import logging
from Buff import Buff
from Planar import Planar
from MainFunctions import Special
from Attributes import *

logger = logging.getLogger(__name__)

class BoneCollectionsSereneDemesne(Planar):
    name = "Bone Collection's Serene Demesne"

    def __init__(self, wearerRole: Role):
        super().__init__(wearerRole)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("BoneHPBuff", StatTypes.HP_PERCENT, 0.12, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def specialStart(self, special: Special):
        bl, dbl, al, dl, hl = super().specialStart(special)
        if special.specialName == "Tribbie" :
            HPStat = special.attr4
            if HPStat >= 5000:
                bl.append(Buff("BoneCDBuff", StatTypes.CD_PERCENT, 0.28, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl