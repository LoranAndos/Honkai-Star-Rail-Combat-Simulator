from Buff import *
from Lightcone import Lightcone
from Attributes import *
from Character import Character


class WelcometotheCosmicCity(Lightcone):
    name = "Welcome to the Cosmic City"
    path = Path.ELATION
    baseHP = 1164
    baseATK = 476
    baseDEF = 529

    MAX_TRIGGERS = 1
    BASICS_TO_RESET = 3

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)
        self.Superpower = False
        self.SuperpowerCount = 0
        self.basicCount = 0

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        SpdBuff = self.level * 0.03 + 0.15
        DefShred = self.level * 0.04 + 0.16
        bl.append(Buff("CosmicCitySPD", StatTypes.SPD_PERCENT, SpdBuff, self.wearerRole, [AtkType.ALL], 1, 1,
                       Role.SELF, TickDown.PERM))
        bl.append(Buff("CosmicCityDefShredBanger", StatTypes.SHRED, DefShred, self.wearerRole, [AtkType.ELABANGER],
                       1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("CosmicCityDefShredPunch", StatTypes.SHRED, DefShred, self.wearerRole, [AtkType.ELAPUNCH],
                       1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl, sl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, hl, sl = super().useBsc(enemyID)
        self.basicCount += 1
        if self.basicCount >= self.BASICS_TO_RESET:
            self.basicCount = 0
            self.SuperpowerCount = 0
        return bl, dbl, al, dl, hl, sl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl, sl = super().useUlt(enemyID)
        PunchlineGain = self.level * 5 + 15
        if self.wearer.name == "SilverWolf999" and self.SuperpowerCount < self.MAX_TRIGGERS:
            self.SuperpowerCount += 1
            self.basicCount = 0
            Character.SharedPunchline += PunchlineGain
        return bl, dbl, al, dl, hl, sl