from Buff import *
from Lightcone import Lightcone
from Attributes import *
from Result import Result
from Turn_Text import Turn

class DazzledByAFloweryWorld(Lightcone):
    name = "Dazzled by a Flowery World"
    path = Path.ELATION
    baseHP = 1058
    baseATK = 582
    baseDEF = 463

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)
        self.spConsumedThisTurn = 0

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        CDBuff = self.level * 0.08 + 0.40
        bl.append(Buff("FloweryWorldCD", StatTypes.CD_PERCENT, CDBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        # Track SP consumed this turn from SparxieSkill
        if turn.moveName == "SparxieSkill":
            spConsumed = abs(min(turn.spChange-3, 0))  # spChange is negative, get absolute value
            self.spConsumedThisTurn += spConsumed
            # DEF ignore per SP consumed, stacking up to 4 times
            stacks = min(self.spConsumedThisTurn, 4)
            ShredVal = stacks * (self.level * 0.01 + 0.04)
            bl.append(Buff("FloweryWorldSHREDPunchBuff", StatTypes.SHRED, ShredVal, self.wearerRole, [AtkType.ELAPUNCH], 1, 1, Role.SELF, TickDown.END))
            bl.append(Buff("FloweryWorldSHREDBangerBuff", StatTypes.SHRED, ShredVal, self.wearerRole, [AtkType.ELABANGER], 1, 1, Role.SELF, TickDown.END))
            # Stream Promo: if 4+ SP consumed in same turn, +20% Elation for all allies
            if self.spConsumedThisTurn >= 4:
                ELABuff = self.level * 0.16 + 0.04
                bl.append(Buff("FloweryWorldELABuff", StatTypes.ELA, ELABuff, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF, TickDown.END))
            self.spConsumedThisTurn = 0  # reset after skill resolves
        return bl, dbl, al, dl, hl