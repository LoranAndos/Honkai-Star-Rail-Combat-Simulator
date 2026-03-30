from Lightcone import Lightcone
from Buff import Buff
from Attributes import *


class PostOpConversation(Lightcone):
    name = "Post-Op Conversation"
    path = Path.ABUNDANCE
    baseHP = 1058
    baseATK = 423
    baseDEF = 331

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        errBuff = self.level * 0.02 + 0.06
        bl.append(Buff("PostOpERR", StatTypes.ERR_PERCENT, errBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        oghBuff = self.level * 0.03 + 0.09
        bl.append(Buff("PostOpOGH", StatTypes.OGH_PERCENT, oghBuff, self.wearerRole, [AtkType.ULT], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl