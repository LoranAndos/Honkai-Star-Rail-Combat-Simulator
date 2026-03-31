from Buff import *
from Lightcone import Lightcone
from Attributes import *

class ATrailOfBygoneBlood(Lightcone):
    name = "A Trail of Bygone Blood"
    path = Path.DESTRUCTION
    baseHP = 1058
    baseATK = 529
    baseDEF = 331

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        crAmount = self.level * 0.02 + 0.10
        dmgAmount = self.level * 0.04 + 0.20
        bl.append(Buff("BygoneBloodCR", StatTypes.CR_PERCENT, crAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("BygoneBlood_SKLDMG", StatTypes.DMG_PERCENT, dmgAmount, self.wearerRole, [AtkType.SKL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("BygoneBlood_ULTDMG", StatTypes.DMG_PERCENT, dmgAmount, self.wearerRole, [AtkType.ULT], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl