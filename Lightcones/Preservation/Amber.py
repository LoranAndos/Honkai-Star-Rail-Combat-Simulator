from Buff import *
from Lightcone import Lightcone
from Attributes import *
from HPChecks import getCharHPRatio
from Turn_Text import Turn
from Result import Result

class Amber(Lightcone):
    name = "Amber"
    path = Path.DESTRUCTION
    baseHP = 847
    baseATK = 265
    baseDEF = 331

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.04 + 0.12
        bl.append(Buff("AmberDEF_equip", StatTypes.DEF_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)

        if getCharHPRatio(self.wearer) < 0.50:
            defBuff = self.level * 0.04 + 0.12
            bl.append(Buff("AmberDEF", StatTypes.DEF_PERCENT, defBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))

        return bl, dbl, al, dl, hl