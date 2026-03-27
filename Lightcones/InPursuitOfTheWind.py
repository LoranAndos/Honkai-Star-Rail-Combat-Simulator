from Buff import *
from Lightcone import Lightcone
from Attributes import *

class InPursuitOfTheWind(Lightcone):
    name = "In Pursuit of the Wind"
    path = Path.HARMONY
    baseHP = 1058
    baseATK = 476
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dl, al, dl, hl = super().equip()
        beAmount = self.level * 0.2 + 0.14
        bl.append(Buff("InPursuitBE", StatTypes.BRK_DMG, beAmount, self.wearerRole, [AtkType.BRK], 1, 1, Role.ALL, TickDown.PERM))
        return bl, dl, al, dl, hl