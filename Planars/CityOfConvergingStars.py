from Buff import Buff
from Planar import Planar
from Attributes import *
from Result import Result
from Turn_Text import Turn


class CityOfConvergingStars(Planar):
    name = "City of Converging Stars"

    def __init__(self, wearerRole: Role):
        super().__init__(wearerRole)

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useFua()
        bl.append(Buff("ConvergingStarsATK", StatTypes.ATK_PERCENT, 0.24, self.wearerRole, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        if result.numKills != 0:
            bl.append(Buff("ConvergingStarsCD", StatTypes.CD_PERCENT, 0.12, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().allyTurn(turn, result)
        if result.numKills != 0:
            bl.append(Buff("ConvergingStarsCD", StatTypes.CD_PERCENT, 0.12, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl