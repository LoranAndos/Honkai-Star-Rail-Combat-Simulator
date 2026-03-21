from Buff import *
from Lightcone import Lightcone
from Attributes import *

class Amber(Lightcone):
    name = "Amber"
    path = Path.PRESERVATION
    baseHP = 847
    baseATK = 265
    baseDEF = 331

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.04 + 0.12
        bl.append(Buff("AmberDEF", StatTypes.DEF_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))

        return bl, dl, al, dl, hl