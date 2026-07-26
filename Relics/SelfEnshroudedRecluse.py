from Relic import Relic
from Buff import *
from Healing import *


class SelfEnshroudedRecluse(Relic):
    name = "Self-Enshrouded Recluse"

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("RecluseSHD", StatTypes.SHD_PERCENT, 0.10, self.wearerRole, [AtkType.ALL]))
        if self.setType == 4:
            bl.append(Buff("RecluseSHDExtra", StatTypes.SHD_PERCENT, 0.12, self.wearerRole, [AtkType.ALL]))
            bl.append(Buff("RecluseCD", StatTypes.CD_PERCENT, 0.15, Role.ALL, [AtkType.ALL]))
        return bl, dbl, al, dl, hl, sl
