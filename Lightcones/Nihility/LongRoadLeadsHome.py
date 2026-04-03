from Buff import *
from Lightcone import Lightcone
from Attributes import *
from Result import Result
from Turn_Text import Turn

class LongRoadLeadsHome(Lightcone):
    name = "Long Road Leads Home"
    path = Path.NIHILITY
    baseHP = 953
    baseATK = 476
    baseDEF = 662

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        beAmount = self.level * 0.10 + 0.50
        bl.append(Buff("LongRoadLeadsHomeBE", StatTypes.BE_PERCENT, beAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        beDBAmount = self.level * 0.03 + 0.15
        if result.brokenEnemy != []:
            dbl.append(Debuff("LongRoadLeadsHomeVULN", self.wearerRole, StatTypes.VULN, beDBAmount, -1, [AtkType.ALL], 2, 2, False, [0, 0], False))
        return bl, dbl, al, dl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().allyTurn(turn, result)
        beDBAmount = self.level * 0.03 + 0.15
        if result.brokenEnemy != []:
            dbl.append(Debuff("LongRoadLeadsHomeVULN", self.wearerRole, StatTypes.VULN, beDBAmount, -1, [AtkType.ALL], 2, 2, False, [0, 0], False))
        return bl, dbl, al, dl, hl