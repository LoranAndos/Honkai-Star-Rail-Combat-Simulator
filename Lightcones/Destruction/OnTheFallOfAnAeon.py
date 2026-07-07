from Buff import *
from Lightcone import Lightcone
from Attributes import *
from HPChecks import getCharHPRatio
from Turn_Text import Turn
from Result import Result

class OnTheFallOfAnAeon(Lightcone):
    name = "On the Fall of an Aeon"
    path = Path.DESTRUCTION
    baseHP = 1058
    baseATK = 529
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)
        self.AttackCount = 0


    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl, sl = super().ownTurn(turn, result)
        AtkBuff = self.level * 0.02 + 0.06
        DmgBuff = self.level * 0.03 + 0.09
        if turn.moveName not in bonusDMG and result.turnDmg > 0:
            self.AttackCount += 1
            bl.append(Buff("AeonATK", StatTypes.ATK_PERCENT, min(self.AttackCount,4)*AtkBuff, self.wearerRole,[AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        if result.brokenEnemy:
            bl.append(Buff("AeonDMG", StatTypes.DMG_PERCENT, DmgBuff, self.wearerRole,[AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl, sl