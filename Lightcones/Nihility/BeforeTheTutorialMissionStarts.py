from Buff import *
from Lightcone import Lightcone
from Attributes import *
from Turn_Text import Turn
from Result import Result


class BeforeTheTutorialMissionStarts(Lightcone):
    name = "Before the Tutorial Mission Starts"
    path = Path.NIHILITY
    baseHP = 953
    baseATK = 476
    baseDEF = 331

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        ehrAmount = self.level * 0.05 + 0.15
        bl.append(
            Buff("TutorialEHR", StatTypes.EHR_PERCENT, ehrAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn, result, enemyID=-1):
        bl, dbl, al, dl, hl = super().ownTurn(turn,result)
        energyAmount = self.level * 1 + 3
        if turn.charName == ("Jiaoqiu") and turn.moveName not in bonusDMG:
            bl.append(
                Buff("TutorialERR", StatTypes.ERR_T, energyAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        return bl, dbl, al, dl, hl
