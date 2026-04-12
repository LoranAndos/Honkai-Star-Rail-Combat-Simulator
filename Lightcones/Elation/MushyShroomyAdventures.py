from Buff import *
from Lightcone import Lightcone
from Attributes import *

class MushyShroomysAdventures(Lightcone):
    name = "Mushy Shroomy's Adventures"
    path = Path.ELATION
    baseHP = 847
    baseATK = 476
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        elaAmount = self.level * 0.02 + 0.10
        bl.append(Buff("MushyShroomyELA", StatTypes.ELA, elaAmount, self.wearerRole, [AtkType.ALL], 1, 3, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

class MushyShroomysAdventuresEMC(MushyShroomysAdventures):

    def useElaSkill(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useElaSkill(enemyID)
        elaDBAmount = self.level * 0.01 + 0.05
        dbl.append(Debuff("MushyShroomyPunchEMCELA_SKL", self.wearerRole, StatTypes.VULN, elaDBAmount, Role.ALL, [AtkType.ELAPUNCH], 2, 1, False, [0, 0], False))
        dbl.append(Debuff("MushyShroomyBangerEMCELA_SKL", self.wearerRole, StatTypes.VULN, elaDBAmount, Role.ALL, [AtkType.ELABANGER], 2, 1, False, [0, 0], False))
        return bl, dbl, al, dl, hl


class MushyShroomysAdventuresYaoGuang(MushyShroomysAdventures):

    def useElaSkill(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useElaSkill(enemyID)
        elaDBAmount = self.level * 0.01 + 0.05
        dbl.append(Debuff("MushyShroomyPunchYaoGuangELA_SKL", self.wearerRole, StatTypes.VULN, elaDBAmount, Role.ALL,
                          [AtkType.ELAPUNCH], 2, 1, False, [0, 0], False))
        dbl.append(Debuff("MushyShroomyBangerYaoGuangELA_SKL", self.wearerRole, StatTypes.VULN, elaDBAmount, Role.ALL,
                          [AtkType.ELABANGER], 2, 1, False, [0, 0], False))
        return bl, dbl, al, dl, hl

class MushyShroomysAdventuresSparxie(MushyShroomysAdventures):

    def useElaSkill(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useElaSkill(enemyID)
        elaDBAmount = self.level * 0.01 + 0.05
        dbl.append(Debuff("MushyShroomyPunchSparxieELA_SKL", self.wearerRole, StatTypes.VULN, elaDBAmount, Role.ALL,
                          [AtkType.ELAPUNCH], 2, 1, False, [0, 0], False))
        dbl.append(Debuff("MushyShroomyBangerSparxieELA_SKL", self.wearerRole, StatTypes.VULN, elaDBAmount, Role.ALL,
                          [AtkType.ELABANGER], 2, 1, False, [0, 0], False))
        return bl, dbl, al, dl, hl

class MushyShroomysAdventuresSilverWolf999(MushyShroomysAdventures):

    def useElaSkill(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useElaSkill(enemyID)
        elaDBAmount = self.level * 0.01 + 0.05
        dbl.append(Debuff("MushyShroomyPunchSilverWolf999ELA_SKL", self.wearerRole, StatTypes.VULN, elaDBAmount, Role.ALL,
                          [AtkType.ELAPUNCH], 2, 1, False, [0, 0], False))
        dbl.append(Debuff("MushyShroomyBangerSilverWolf999ELA_SKL", self.wearerRole, StatTypes.VULN, elaDBAmount, Role.ALL,
                          [AtkType.ELABANGER], 2, 1, False, [0, 0], False))
        return bl, dbl, al, dl, hl