from Lightcone import Lightcone
from Buff import Buff
from Attributes import *
from Turn_Text import Turn
from Result import Result
from HPChecks import getEnemyHPRatio
from Healing import *


class CruisingInTheStellarSea(Lightcone):
    name = "Cruising in the Stellar Sea"
    path = Path.HUNT
    baseHP = 953
    baseATK = 529
    baseDEF = 463

    def __init__(self, wearerRole, level: int = 5, uptime: float = 0.5):
        super().__init__(wearerRole, level)
        self.uptime = uptime

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        baseCR = self.level * 0.02 + 0.06
        bl.append(Buff("CruisingBaseCR", StatTypes.CR_PERCENT, baseCR, self.wearerRole,
                       [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)

        if result.charRole != self.wearerRole:
            return bl, dbl, al, dl, hl

        # Extra CR if an attacked enemy is at or below 50% HP
        extraCR = self.level * 0.02 + 0.06
        if any(getEnemyHPRatio(e) <= 0.5 for e in result.enemiesHit):
            bl.append(Buff("CruisingLowHPCR", StatTypes.CR_PERCENT, extraCR, self.wearerRole,
                           [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))

        # ATK +20% for 2 turns on kill
        atkBuff = self.level * 0.05 + 0.15
        if result.numKills > 0:
            bl.append(Buff("CruisingKillATK", StatTypes.ATK_PERCENT, atkBuff, self.wearerRole,
                           [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))

        return bl, dbl, al, dl, hl
