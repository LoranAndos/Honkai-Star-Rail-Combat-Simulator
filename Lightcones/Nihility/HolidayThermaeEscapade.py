from Buff import *
from Lightcone import Lightcone
from Attributes import *
from Turn_Text import Turn
from Result import Result
from math import floor

class HolidayThermaeEscapade(Lightcone):
    name = "Holiday Thermae Escapade"
    path = Path.NIHILITY
    baseHP = 1058
    baseATK = 529
    baseDEF = 331

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.04 + 0.12
        bl.append(Buff("HolidayThermaeDB", StatTypes.DMG_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        if self.level <= 3:
            vulnAmount = floor(self.level * 0.015 + 0.085)
        elif self.level == 4:
            vulnAmount = 0.14
        else:
            vulnAmount = 0.16
        if result.turnDmg > 0 and result.charRole != bonusDMG:
            dbl.append(Debuff("HolidayThermaeVULN", self.wearerRole, StatTypes.VULN, vulnAmount, turn.targetID, [AtkType.ALL], 2, 1, False, [0, 0], False))
        return dl, dbl, al, dl, hl