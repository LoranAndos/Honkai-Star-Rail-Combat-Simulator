from Buff import *
from Lightcone import Lightcone
from Attributes import *

class DataBank(Lightcone):
    name = "Data Bank"
    path = Path.ERUDITION
    baseHP = 741
    baseATK = 370
    baseDEF = 265

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.07 + 0.21
        bl.append(Buff("DataBank_ULTDMG", StatTypes.DMG_PERCENT, BuffAmount, self.wearerRole, [AtkType.ULT], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl