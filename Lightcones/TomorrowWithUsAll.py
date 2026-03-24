from Buff import *
from Lightcone import Lightcone
from Attributes import *

class TomorrowWithUsAll(Lightcone):
    name = "Tomorrow, With Us All"
    path = Path.ELATION
    baseHP = 953
    baseATK = 476
    baseDEF = 331

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.03 + 0.09
        bl.append(Buff("TomorrowWithUsDB", StatTypes.CD_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dl, al, dl, hl = super().useUlt()
        elaAmount = self.level * 0.01 + 0.07
        bl.append(Buff("ForeverVictual_Ult", StatTypes.ELA, elaAmount, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF, TickDown.END))
        return bl, dl, al, dl, hl
