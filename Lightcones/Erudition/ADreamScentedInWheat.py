from Buff import *
from Lightcone import Lightcone
from Attributes import *

class ADreamScentedInWheat(Lightcone):
    name = "A Dream Scented in Wheat"
    path = Path.ERUDITION
    baseHP = 953
    baseATK = 529
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        crAmount = self.level * 0.02 + 0.10
        dbAmount = self.level * 0.04 + 0.20
        bl.append(Buff("DreamScentedCR", StatTypes.CR_PERCENT, crAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("DreamScentedDB_ULT", StatTypes.DMG_PERCENT, dbAmount, self.wearerRole, [AtkType.ULT], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("DreamScentedDB_FUA", StatTypes.DMG_PERCENT, dbAmount, self.wearerRole, [AtkType.FUA], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl