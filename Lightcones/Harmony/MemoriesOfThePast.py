from Lightcone import Lightcone
from Buff import Buff
from Attributes import *
from Healing import *
from Result import Result
from Turn_Text import Turn


class MemoriesOfThePast(Lightcone):
    name = "Memories of the Past"
    path = Path.HARMONY
    baseHP = 952.6
    baseATK = 423.36
    baseDEF = 396.90


    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        breakBuff = self.level * 0.07 + 0.21
        bl.append(Buff("MotpBE", StatTypes.BE_PERCENT, breakBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        if result.turnDmg > 0 and result.turnName not in bonusDMG:
            errGain = self.level + 3
            bl.append(Buff("MotpBonusEnergy", StatTypes.ERR_T, errGain, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl