from Buff import *
from Lightcone import Lightcone
from Attributes import *
from Turn_Text import Turn
from Result import Result
from MainFunctions import Special


class LiesDanceOnTheBreeze(Lightcone):
    name = "Lies Dance on the Breeze"
    path = Path.NIHILITY
    baseHP = 953
    baseATK = 582
    baseDEF = 529
    SpdTreshpoint = False

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        SpdAmount = self.level * 0.03 + 0.15
        bl.append(Buff("LiesDanceSpd", StatTypes.SPD_PERCENT, SpdAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn, result, enemyID=-1):
        bl, dbl, al, dl, hl = super().ownTurn(turn,result)
        BigDefReduction = self.level * 0.02 + 0.14
        SmallDefReduction = self.level * 0.01 + 0.07
        if turn.moveName not in bonusDMG and result.turnDmg > 0 and result.enemiesHit:
            dbl.append(Debuff("LiesDanceBigShred", self.wearerRole, StatTypes.SHRED, BigDefReduction, Role.ALL, [AtkType.ALL], 2,1, Targeting.AOE))
        if turn.moveName not in bonusDMG and result.turnDmg > 0 and result.enemiesHit and self.SpdTreshpoint:
            dbl.append(Debuff("LiesDanceSmallShred", self.wearerRole, StatTypes.SHRED, SmallDefReduction, Role.ALL, [AtkType.ALL], 2,1, Targeting.AOE))
        return bl, dbl, al, dl, hl

    def specialStart(self, special: Special):
        bl, dbl, al, dl, hl = super().specialStart(special)
        if special.specialName == "Cipher" :
            self.SPDStat = special.attr1
            if self.SPDStat >= 170:
                self.SpdTreshpoint = True
        elif special.specialName == "MortenaxBlade" :
            self.SPDStat = special.attr3
            if self.SPDStat >= 170:
                self.SpdTreshpoint = True
        return bl, dbl, al, dl, hl