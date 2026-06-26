from Buff import *
from Lightcone import Lightcone
from Attributes import *
from HPChecks import getEnemyHPRatio
from Turn_Text import Turn
from Result import Result

class TheSeriousnessOfBreakfast(Lightcone):
    name = "The Seriousness of Breakfast"
    path = Path.ERUDITION
    baseHP = 847
    baseATK = 476
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)
        self.NumKills = 0

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.03 + 0.09
        bl.append(Buff("BreakfastDMG", StatTypes.DMG_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        AtkBuff = self.level * 0.01 + 0.03
        if result.numKills != 0:
            self.NumKills = min(self.NumKills + result.numKills , 3)
            bl.append(Buff("BreakfastKillAtk", StatTypes.ATK_PERCENT, AtkBuff*self.NumKills, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl