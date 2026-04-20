from Buff import *
from Lightcone import Lightcone
from Attributes import *
from HPChecks import getCharHPRatio
from Turn_Text import Turn
from Result import Result

class MutualDemise(Lightcone):
    name = "Mutual Demise"
    path = Path.DESTRUCTION
    baseHP = 847
    baseATK = 370
    baseDEF = 198

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)

        if getCharHPRatio(self.wearer) < 0.80:
            crBuff = self.level * 0.03 + 0.09
            bl.append(Buff("MutualDemiseCR", StatTypes.CR_PERCENT, crBuff, self.wearerRole,
                           [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))

        return bl, dbl, al, dl, hl