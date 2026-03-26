from Lightcone import Lightcone
from Attributes import *
from Result import Result
from Turn_Text import Turn
from Healing import Healing


class Pioneering(Lightcone):
    name = "Pioneering"
    path = Path.PRESERVATION
    baseHP = 953
    baseATK = 265
    baseDEF = 265

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        HealAmount = self.level * 0.02 + 0.10
        if result.brokenEnemy != []:
            hl.append(Healing("PioneerHeal",[HealAmount,0],Scaling.HP,self.wearerRole,self.wearerRole,Targeting.SINGLE))
        return bl, dbl, al, dl, hl