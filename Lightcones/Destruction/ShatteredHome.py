from Buff import *
from Lightcone import Lightcone
from Attributes import *
from HPChecks import getEnemyHPRatio
from Turn_Text import Turn
from Result import Result

class ShatteredHome(Lightcone):
    name = "Shattered Home"
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
        if any(getEnemyHPRatio(e) >= 0.5 for e in result.enemiesHit):
            DmgAmount = self.level * 0.05 + 0.15
            bl.append(Buff("ShatteredHomeDMG", StatTypes.DMG_PERCENT, DmgAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        return bl, dbl, al, dl, hl