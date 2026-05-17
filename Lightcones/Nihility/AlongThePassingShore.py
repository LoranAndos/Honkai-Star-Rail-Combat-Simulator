from Buff import *
from Lightcone import Lightcone
from Attributes import *
from Result import Result
from Turn_Text import Turn


class AlongThePassingShore(Lightcone):
    name = "Along the Passing Shore"
    path = Path.NIHILITY
    baseHP = 1058
    baseATK = 635
    baseDEF = 397

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        cdBuff = 0.06 * self.level + 0.30
        bl.append(Buff("PassingShoreCD", StatTypes.CD_PERCENT, cdBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        dmgDebuff = 0.04 * self.level + 0.20
        if (turn.moveName not in bonusDMG) and result.enemiesHit and result.turnDmg > 0:
            dbl.append(Debuff("PassingShoreDmgDebuff", self.wearerRole, StatTypes.DMG_PERCENT, dmgDebuff, Role.ALL, [AtkType.ALL], 1,1, Targeting.AOE))
            dbl.append(Debuff("PassingShoreUltDmgDebuff", self.wearerRole, StatTypes.DMG_PERCENT, dmgDebuff, Role.ALL, [AtkType.ULT], 1, 1, Targeting.AOE))
        return bl, dbl, al, dl, hl