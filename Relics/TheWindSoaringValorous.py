from Relic import Relic
from Buff import Buff
from Attributes import *


class WindSoaring(Relic):
    name = "The Wind-Soaring Valorous"

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("WindSoaringATK", StatTypes.ATK_PERCENT, 0.12, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                          TickDown.PERM))
        if self.setType == 4:
            bl.append(Buff("WindSoaringCR", StatTypes.CR_PERCENT, 0.06, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                                 TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useFua(enemyID)
        if self.setType == 4:
            bl.append(Buff("WindSoaringDMG", StatTypes.DMG_PERCENT, 0.36, self.wearerRole, [AtkType.ULT], 1, 1, Role.SELF,
                     TickDown.END))
        return bl, dbl, al, dl, hl

class WindSoaringYunli(WindSoaring):
    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt(enemyID)
        if self.setType == 4:
            bl.append(Buff("WindSoaringDMG", StatTypes.DMG_PERCENT, 0.36, self.wearerRole, [AtkType.ULT], 1, 1, Role.SELF,
                     TickDown.END))
        return bl, dbl, al, dl, hl