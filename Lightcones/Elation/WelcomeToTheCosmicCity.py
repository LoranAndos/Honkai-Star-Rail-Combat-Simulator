from Buff import *
from Lightcone import Lightcone
from Attributes import *

class WelcometotheCosmicCity(Lightcone):
    name = "Welcome to the Cosmic City"
    path = Path.ELATION
    baseHP = 1164
    baseATK = 476
    baseDEF = 529

    Superpower = False
    SuperpowerCount = 0

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        SpdBuff = self.level * 0.03 + 0.15
        DefShred = self.level * 0.04 + 0.16
        bl.append(Buff("CosmicCitySPD", StatTypes.SPD_PERCENT, SpdBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("SuperpowerDefShred", StatTypes.SHRED, DefShred, self.wearerRole, [AtkType.ELABANGER], 3, 1, Role.SELF, TickDown.END))
        bl.append(Buff("SuperpowerDefShred", StatTypes.SHRED, DefShred, self.wearerRole, [AtkType.ELAPUNCH], 3, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("SuperPowerPunchLine", StatTypes.PUNCH, 20, self.wearerRole, [AtkType.ALL], 1, 1, Role.ALL,TickDown.START))
        return bl, dbl, al, dl, hl

