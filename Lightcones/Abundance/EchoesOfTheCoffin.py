from Buff import *
from Lightcone import Lightcone
from Attributes import *
from Result import Result
from Turn_Text import Turn


class EchoesOfTheCoffin(Lightcone):
    name = "Echoes Of The Coffin"
    path = Path.ABUNDANCE
    baseHP = 1164
    baseATK = 582
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        atkAmount = self.level * 0.04 + 0.20
        bl.append(Buff("EchoesOfTheCoffinATK", StatTypes.ATK_PERCENT, atkAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        ERRAmount = self.level * 0.05 + 2.5
        if result.turnDmg > 0:
            AmountHit = min(len(result.enemiesHit),3)
            bl.append(Buff("EchoesOfTheCoffinERR", StatTypes.ERR_T, ERRAmount*AmountHit, self.wearerRole, [AtkType.ALL], 1, 1,Role.SELF, TickDown.START))
        return dl, dbl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt(enemyID)
        SPDAmount = self.level * 0.02 + 0.10
        bl.append(Buff("EchoesOfTheCoffinSPD_ULT", StatTypes.SPD, SPDAmount, self.wearerRole, [AtkType.ALL], 2, 1, Role.ALL, TickDown.END))
        return bl, dbl, al, dl, hl