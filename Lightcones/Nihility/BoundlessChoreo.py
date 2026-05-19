from Buff import *
from Lightcone import Lightcone
from Attributes import *
from Turn_Text import Turn
from Result import Result


class BoundlessChoreo(Lightcone):
    name = "Boundless Choreo"
    path = Path.NIHILITY
    baseHP = 953
    baseATK = 476
    baseDEF = 331

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        CRAmount = self.level * 0.02 + 0.06
        CDAmount = self.level * 0.06 + 0.18
        bl.append(
            Buff("BoundlessCR", StatTypes.CR_PERCENT, CRAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(
            Buff("BoundlessDMG", StatTypes.CD_PERCENT, CDAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl