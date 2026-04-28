from Buff import *
from Lightcone import Lightcone
from Attributes import *
from HPChecks import getEnemyHPRatio
from Turn_Text import Turn
from Result import Result

class TheBirthOfTheSelf(Lightcone):
    name = "The Birth of the Self"
    path = Path.ERUDITION
    baseHP = 953
    baseATK = 476
    baseDEF = 331

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.06 + 0.18
        bl.append(Buff("BirthOfSelfDB", StatTypes.DMG_PERCENT, BuffAmount, self.wearerRole, [AtkType.FUA], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        if any(getEnemyHPRatio(e) <= 0.5 for e in result.enemiesHit):
            BuffAmount = self.level * 0.06 + 0.18
            bl.append(Buff("BirthOfSelfDB_HPred", StatTypes.DMG_PERCENT, BuffAmount, self.wearerRole, [AtkType.FUA], 1, 1, Role.SELF, TickDown.START))
        return bl, dbl, al, dl, hl