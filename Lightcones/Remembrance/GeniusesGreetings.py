from Buff import *
from Lightcone import Lightcone
from Attributes import *

class GeniusesGreetings(Lightcone):
    name = "Geniuses' Greetings"
    path = Path.REMEMBRANCE
    baseHP = 953
    baseATK = 476
    baseDEF = 331

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        atkAmount = self.level * 0.04 + 0.12
        bl.append(Buff("GeniusesGreetingsATK", StatTypes.ATK_PERCENT, atkAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt(enemyID)
        BuffAmount = self.level * 0.05 + 0.15
        bl.append(Buff("GeniusesGreetingsDB", StatTypes.DMG_PERCENT, BuffAmount, Role.ALL, [AtkType.BSC], 3, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl