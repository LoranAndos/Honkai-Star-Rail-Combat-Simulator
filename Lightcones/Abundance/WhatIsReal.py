from Lightcone import Lightcone
from Buff import *
from Attributes import *
from Healing import Healing

class WhatIsReal(Lightcone):
    name = "What is Real"
    path = Path.ABUNDANCE
    baseHP = 1058.4
    baseATK = 423.36
    baseDEF = 330.75

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        beBuff = self.level * 0.06 + 0.18
        bl.append(Buff("WhatIsRealBE", StatTypes.BE_PERCENT, beBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useBsc(enemyID)
        #Like this till I figure out how to add healing in a lightcone
        #HealAmount = self.level * 0.005 + 0.015
        #hl.append(Healing("WhatIsRealBasicScalingHeal", [HealAmount,0], Scaling.MAXHP, self.wearerRole, self.wearerRole, Targeting.SINGLE))
        #hl.append(Healing("WhatIsRealBasicFlatHeal", [800,0], Scaling.Other, self.wearerRole, self.wearerRole, Targeting.SINGLE))
        return bl, dbl, al, dl, hl