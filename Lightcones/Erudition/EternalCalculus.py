from Buff import *
from Lightcone import Lightcone
from Attributes import *
from HPChecks import getEnemyHPRatio
from Turn_Text import Turn
from Result import Result

class EternalCalculus(Lightcone):
    name = "Eternal Calculus"
    path = Path.ERUDITION
    baseHP = 1058
    baseATK = 529
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        AtkBuff = self.level * 0.01 + 0.07
        bl.append(Buff("CalculusATK", StatTypes.ATK_PERCENT, AtkBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        AmountHit = len(result.enemiesHit)
        AtkBuff = self.level * 0.01 + 0.03
        SpdBuff = self.level * 0.02 + 0.06
        bl.append(Buff("CalculusHitATK", StatTypes.ATK_PERCENT, AtkBuff*AmountHit, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        if AmountHit >= 3:
            bl.append(Buff("CalculusHitSpd", StatTypes.SPD_PERCENT, SpdBuff, self.wearerRole, [AtkType.ALL], 1, 1,Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl