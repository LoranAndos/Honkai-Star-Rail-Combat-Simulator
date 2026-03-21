from Buff import *
from Lightcone import Lightcone
from Attributes import *

class Void(Lightcone):
    name = "Void"
    path = Path.NIHILITY
    baseHP = 847
    baseATK = 318
    baseDEF = 265

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.05 + 0.15
        bl.append(Buff("VoidDB", StatTypes.EHR_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 3, 1, Role.SELF,TickDown.END))
        return bl, dl, al, dl, hl