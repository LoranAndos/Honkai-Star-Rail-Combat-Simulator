from Buff import Buff
from Attributes import *
from Planar import Planar
from Turn_Text import Turn
from Result import Result

class TengokuLivestream(Planar):
    name = "Tengoku@Livestream"

    def __init__(self, wearerRole: Role):
        super().__init__(wearerRole)
        self.spConsumedThisTurn = 0

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("TengokuCD", StatTypes.CD_PERCENT, 0.16, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        if turn.moveName == "SparxieSkill":
            spConsumed = abs(min(turn.spChange-2, 0))  # spChange is negative, get absolute value
            self.spConsumedThisTurn += spConsumed
            if self.spConsumedThisTurn >= 3:
                bl.append(Buff("TengokuSPSparxieCD", StatTypes.CD_PERCENT, 0.32, self.wearerRole, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
            self.spConsumedThisTurn = 0
        elif turn.moveName == "ArcherSkill":
            spConsumed = abs(min(turn.spChange-2, 0))  # spChange is negative, get absolute value
            self.spConsumedThisTurn += spConsumed
            if self.spConsumedThisTurn >= 3:
                bl.append(Buff("TengokuSPArcherCD", StatTypes.CD_PERCENT, 0.32, self.wearerRole, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
        elif turn.moveName == "RinTohsakaSkillSingle":
            spConsumed = abs(min(turn.spChange, 0))  # spChange is negative, get absolute value
            self.spConsumedThisTurn += spConsumed
            if self.spConsumedThisTurn >= 3:
                bl.append(Buff("TengokuSPRinCD", StatTypes.CD_PERCENT, 0.32, self.wearerRole, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
            self.spConsumedThisTurn = 0
        return bl, dbl, al, dl, hl

    def takeTurn(self) -> str:
        self.spConsumedThisTurn = 0