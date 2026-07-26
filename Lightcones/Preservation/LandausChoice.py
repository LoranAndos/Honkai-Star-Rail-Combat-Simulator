from Buff import *
from Lightcone import Lightcone
from Attributes import *

class LandausChoice(Lightcone):
    name = "Landau's Choice"
    path = Path.PRESERVATION
    baseHP = 953
    baseATK = 423
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        DmgReduction = 0.14 + 0.02 * self.level
        self.wearer.aggro *= 3
        bl.append(Buff("LandausChoiceDMGReduction", StatTypes.DMG_REDUCTION, DmgReduction, self.wearerRole,
                       [AtkType.ALL], 1, 1, self.wearerRole, TickDown.PERM))
        return bl, dbl, al, dl, hl, sl