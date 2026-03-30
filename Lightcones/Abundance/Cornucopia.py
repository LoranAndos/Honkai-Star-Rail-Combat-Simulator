from Buff import *
from Lightcone import Lightcone
from Attributes import *

class Cornucopia(Lightcone):
    name = "Cornucopia"
    path = Path.ABUNDANCE
    baseHP = 953
    baseATK = 265
    baseDEF = 265

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.03 + 0.09
        bl.append(Buff("Cornucopia_SKLOGH", StatTypes.OGH_PERCENT, BuffAmount, self.wearerRole, [AtkType.SKL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("Cornucopia_ULTOGH", StatTypes.OGH_PERCENT, BuffAmount, self.wearerRole, [AtkType.ULT], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl