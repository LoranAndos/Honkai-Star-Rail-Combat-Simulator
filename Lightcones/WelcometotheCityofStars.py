from Buff import *
from Lightcone import Lightcone
from Attributes import *

class WelcometotheCityofStars(Lightcone):
    name = "Welcome to the City of Stars"
    path = Path.ELATION
    baseHP = 953
    baseATK = 635
    baseDEF = 463

    Superpower = False
    SuperpowerCount = 0

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dl, al, dl, hl = super().equip()
        AtkBuff = self.level * 0.16 + 0.48
        bl.append(Buff("CityOfStarsATK", StatTypes.ATK_PERCENT, AtkBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useBsc(enemyID)
        ElationCount = self.level * 2 + 10
        if self.Superpower:
            if self.SuperpowerCount >1:
                bl.append(Buff("SuperPowerPunchLine", StatTypes.PUNCH, 2, self.wearerRole, [AtkType.SPECIAL], 1, 1, Role.SELF,TickDown.START))
                self.SuperpowerCount -= 1
            if self.SuperpowerCount == 1:
                bl.append(
                    Buff("SuperPowerPunchLine", StatTypes.PUNCH, 2, self.wearerRole, [AtkType.SPECIAL], 1, 1, Role.SELF,TickDown.START))
                bl.append(Buff("SuperPowerPunchLineEnd", StatTypes.PUNCH, ElationCount, self.wearerRole, [AtkType.SPECIAL], 1, 1, Role.SELF,TickDown.START))
                self.SuperpowerCount -= 1
        return bl, dbl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dl, al, dl, hl = super().equip()
        DefShred = self.level * 0.03 + 0.15
        bl.append(Buff("Superpower", StatTypes.SHRED, DefShred, self.wearerRole, [AtkType.ELA], 3, 1, Role.SELF, TickDown.END))
        self.Superpower = True
        self.SuperpowerCount = 3
        return bl, dl, al, dl, hl

