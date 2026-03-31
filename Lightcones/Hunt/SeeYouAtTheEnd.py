from Buff import *
from Lightcone import Lightcone
from Attributes import *

class SeeYouAtTheEnd(Lightcone):
    name = "See You at the End"
    path = Path.HUNT
    baseHP = 953
    baseATK = 529
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.04 + 0.20
        bl.append(Buff("SeeYouAtTheEndCD", StatTypes.CD_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("SeeYouAtTheEnd_SKLDMG", StatTypes.DMG_PERCENT, BuffAmount, self.wearerRole, [AtkType.SKL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("SeeYouAtTheEnd_FUADMG", StatTypes.DMG_PERCENT, BuffAmount, self.wearerRole, [AtkType.FUA], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl