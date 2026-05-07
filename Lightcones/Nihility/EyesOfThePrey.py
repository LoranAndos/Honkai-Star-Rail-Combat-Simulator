from Buff import *
from Lightcone import Lightcone
from Attributes import *

class EyesOfThePrey(Lightcone):
    name = "Eyes of the Prey"
    path = Path.NIHILITY
    baseHP = 953
    baseATK = 476
    baseDEF = 331

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        ehrAmount = self.level * 0.05 + 0.15
        DOTAmount = self.level * 0.06 + 0.18
        bl.append(Buff("EyesOfThePreyEHR", StatTypes.EHR_PERCENT, ehrAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        bl.append(Buff("EyesOfThePreyDOT", StatTypes.DMG_PERCENT, DOTAmount, self.wearerRole, [AtkType.DOT], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl