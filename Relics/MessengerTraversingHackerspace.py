from Relic import Relic
from Buff import *
from Attributes import *


class MessengerTraversingHackerspace(Relic):
    name = "Messenger Traversing Hackerspace"

    def __init__(self, wearerRole, setType, allyUlt=False):
        super().__init__(wearerRole, setType)
        self.allyUlt = allyUlt

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("MessengerSPD", StatTypes.SPD_PERCENT, 0.06, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt(enemyID)
        if self.allyUlt:
            bl.append(Buff("MessengerUltSPD", StatTypes.SPD_PERCENT, 0.12, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl