from Buff import Buff
from Planar import Planar
from Result import Result
from Turn_Text import Turn
from Attributes import *


class DuranDynastyOfRunningWolves(Planar):
    name = "Duran, Dynasty of Running Wolves"
    procs = 0
    appliedCDBuff = False

    def __init__(self, wearerRole: Role):
        super().__init__(wearerRole)

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().allyTurn(turn, result)
        if AtkType.FUA in turn.atkType and turn.moveName not in bonusDMG:
            self.procs = self.procs + 1
            bl.append(
                Buff("DuranDMG", StatTypes.DMG_PERCENT, 0.05, self.wearerRole, [AtkType.FUA], 1, 5, Role.SELF, TickDown.PERM))
            if self.procs == 5 and not self.appliedCDBuff:
                self.appliedCDBuff = True
                bl.append(Buff("DuranCD", StatTypes.CD_PERCENT, 0.25, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                               TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        if AtkType.FUA in result.atkType and result.turnName not in bonusDMG:
            self.procs = self.procs + 1
            bl.append(
                Buff("DuranDMG", StatTypes.DMG_PERCENT, 0.05, self.wearerRole, [AtkType.FUA], 1, 5, Role.SELF, TickDown.PERM))
            if self.procs == 5 and not self.appliedCDBuff:
                self.appliedCDBuff = True
                bl.append(Buff("DuranCD", StatTypes.CD_PERCENT, 0.25, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                               TickDown.PERM))
        return bl, dbl, al, dl, hl