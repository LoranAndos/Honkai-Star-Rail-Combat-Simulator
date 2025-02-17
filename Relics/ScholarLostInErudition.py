from Relic import Relic
from Buff import *
from Attributes import *


class ScholarLostInErudition(Relic):
    name = "Scholar lost in Erudition"

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl = super().equip()
        bl.append(Buff("ScholarCR", StatTypes.CR_PERCENT, 0.08, self.wearerRole, [AtkType.ALL]))
        if self.setType == 4:
            bl.append(Buff("ScholarDMG", StatTypes.DMG_PERCENT, 0.2, self.wearerRole, [AtkType.SKL, AtkType.ULT]))
        return bl, dbl, al, dl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl = super().useUlt(enemyID)
        if self.setType == 4:
            bl.append(
                Buff("ScholarBonusDMG", StatTypes.DMG_PERCENT, 0.25, self.wearerRole, [AtkType.SKL], 2, 1, self.wearerRole,
                     tdType=TickDown.START))
        return bl, dbl, al, dl