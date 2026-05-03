from Relic import Relic
from Buff import Buff
from Delay_Text import *
from Attributes import *


class DivineQueryMasterSmith(Relic):
    name = "Divine-Querying Master Smith"

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("MasterSmithHP", StatTypes.HP_PERCENT, 0.12, self.wearerRole,
                       [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn, result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        if self.setType == 4 and result.charName == "MortenaxBlade":
            bl.append(Buff("MasterSmithCD", StatTypes.CD_PERCENT, 0.28, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
            bl.append(Buff("MasterSmithComburent", StatTypes.DMG_PERCENT, 0.15, Role.ALL, [AtkType.ALL], 2, 1, Role.SELF,TickDown.END))
        return bl, dbl, al, dl, hl