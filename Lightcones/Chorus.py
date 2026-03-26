from Buff import *
from Lightcone import Lightcone
from Attributes import *

class Chorus(Lightcone):
    name = "Chorus"
    path = Path.HARMONY
    baseHP = 847
    baseATK = 318
    baseDEF = 265

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.01 + 0.07
        bl.append(Buff("ChorusATK", StatTypes.ATK_PERCENT, BuffAmount, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dl, al, dl, hl