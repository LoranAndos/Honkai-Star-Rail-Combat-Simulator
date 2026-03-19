from Buff import *
from Lightcone import Lightcone
from Attributes import *

class Arrows(Lightcone):
    name = "Arrows"
    path = Path.HUNT
    baseHP = 847
    baseATK = 318
    baseDEF = 265

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.03 + 0.09
        bl.append(Buff("ArrowsCR", StatTypes.CR_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
        return bl, dl, al, dl, hl