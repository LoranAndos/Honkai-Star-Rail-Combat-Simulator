from Buff import *
from Lightcone import Lightcone
from Attributes import *
from HPChecks import getCharHPRatio
from HPChecks import getEnemyHPRatio
from Turn_Text import Turn
from Result import Result

class ASecretVow(Lightcone):
    name = "A Secret Vow"
    path = Path.DESTRUCTION
    baseHP = 1058
    baseATK = 476
    baseDEF = 265

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        BuffAmount = self.level * 0.05 + 0.15
        bl.append(Buff("SecretVow", StatTypes.DMG_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl, sl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl, sl = super().ownTurn(turn, result)
        if any(getEnemyHPRatio(e) >= getCharHPRatio(self.wearer) for e in result.enemiesHit):
            BuffAmount = self.level * 0.05 + 0.15
            bl.append(Buff("SecretVowExtra", StatTypes.DMG_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl, sl