from Buff import *
from Lightcone import Lightcone
from Attributes import *

class CollapsingSky(Lightcone):
    name = "Collapsing Sky"
    path = Path.DESTRUCTION
    baseHP = 846
    baseATK = 370
    baseDEF = 198

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.05 + 0.15
        bl.append(Buff("CollapsingSkyDB_SKL", StatTypes.DMG_PERCENT, BuffAmount, self.wearerRole, [AtkType.SKL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("CollapsingSkyDB_BSC", StatTypes.DMG_PERCENT, BuffAmount, self.wearerRole, [AtkType.BSC], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dl, al, dl, hl