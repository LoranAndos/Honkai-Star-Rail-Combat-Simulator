from Buff import *
from Lightcone import Lightcone
from Attributes import *

class TodaysGoodLuck(Lightcone):
    name = "Today's Good Luck"
    path = Path.ELATION
    baseHP = 953
    baseATK = 529
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.10 + 0.02
        bl.append(Buff("TodaysGoodLuckCR", StatTypes.CR_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useElaSkill(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useElaSkill(enemyID)
        BuffAmount = self.level * 0.10 + 0.02
        bl.append(Buff("TodaysGoodLuckELA", StatTypes.ELA, BuffAmount, self.wearerRole, [AtkType.ALL], 1, 2, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl