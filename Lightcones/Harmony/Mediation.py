from Buff import *
from Lightcone import Lightcone
from Attributes import *

class Mediation(Lightcone):
    name = "Mediation"
    path = Path.HARMONY
    baseHP = 847
    baseATK = 318
    baseDEF = 265

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        BuffAmount = self.level * 2 + 10
        bl.append(Buff("MediationSPD", StatTypes.SPD, BuffAmount, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF,TickDown.END))
        return bl, dbl, al, dl, hl