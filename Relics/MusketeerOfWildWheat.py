from Relic import Relic
from Buff import Buff
from Attributes import *


class MusketeerOfWildWheat(Relic):
    name = "Musketeer of Wild Wheat"

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(
            Buff("MuskATK", StatTypes.ATK_PERCENT, 0.12, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        if self.setType == 4:
            bl.append(
                Buff("MuskSPD", StatTypes.SPD_PERCENT, 0.06, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
            bl.append(
                Buff("MuskATK", StatTypes.DMG_PERCENT, 0.10, self.wearerRole, [AtkType.BSC], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl