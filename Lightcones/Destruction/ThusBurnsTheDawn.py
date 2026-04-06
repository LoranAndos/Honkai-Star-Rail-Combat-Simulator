from Buff import *
from Lightcone import Lightcone
from Attributes import *
from Result import Result
from Turn_Text import Turn
from math import floor

class ThusBurnsTheDawn(Lightcone):
    name = "Thus Burns the Dawn"
    path = Path.DESTRUCTION
    baseHP = 953
    baseATK = 688
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("ThusBurnsTheDawnSPD", StatTypes.SPD, 12, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        ShredAmount = floor(self.level * 0.045 + 0.135)
        if result.turnDmg > 0:
            bl.append(Buff("ThusBurnsTheDawnSHRED", StatTypes.SHRED, ShredAmount, self.wearerRole, [AtkType.ALL], 1, 1,Role.SELF, TickDown.PERM))
        return dl, dbl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt()
        BuffAmount = self.level * 0.18 + 0.42
        bl.append(Buff("ThusBurnsTheDawnDB", StatTypes.DMG_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        return bl, dbl, al, dl, hl