from Buff import *
from Lightcone import Lightcone
from Attributes import *

class TheFlowerRemembers(Lightcone):
    name = "The Flower Remembers"
    path = Path.REMEMBRANCE
    baseHP = 1058
    baseATK = 529
    baseDEF = 331

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        cdAmount = self.level * 0.04 + 0.20
        cdMemoAmount = self.level * 0.06 + 0.18
        bl.append(Buff("FlowerRemembersCD", StatTypes.CD_PERCENT, cdAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("FlowerRemembersCD_MEMO", StatTypes.CD_PERCENT, cdMemoAmount, self.wearerRole, [AtkType.MEMO], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl