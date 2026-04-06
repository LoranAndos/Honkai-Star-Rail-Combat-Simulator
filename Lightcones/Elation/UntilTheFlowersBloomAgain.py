from Buff import *
from Lightcone import Lightcone
from Attributes import *
from Character import Character
from math import floor

class UntilTheFlowersBloomAgain(Lightcone):
    name = "Until the Flowers Bloom Again"
    path = Path.ELATION
    baseHP = 953
    baseATK = 635
    baseDEF = 463

    def __init__(self, wearerRole, level=1, maxEnergy=480):
        super().__init__(wearerRole, level)
        self.maxEnergy = maxEnergy


    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        CDBuff = self.level * 0.15 + 0.45
        if self.level <= 3:
            ERRBuff = self.level * 0.015 + 0.085
        elif self.level == 4:
            ERRBuff = 0.14
        else:
            ERRBuff = 0.16
        bl.append(Buff("FlowersBloomCD", StatTypes.CD_PERCENT, CDBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("FlowersBloomERR", StatTypes.ERR_PERCENT, ERRBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        if self.maxEnergy >= 120:
            ERRExtraBuff = min(floor((self.maxEnergy-120)/10)*0.3,10.8)
            bl.append(Buff("FlowersBloomExtraERR", StatTypes.ERR_PERCENT, ERRExtraBuff/100, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useElaSkill(self, enemyID = -1):
        bl, dbl, al, dl, hl = super().equip()
        VulAmount = self.level * 0.0375 + 0.1125
        dbl.append(Debuff("FlowersBloomVul", self.wearerRole, StatTypes.VULN, VulAmount, Role.ALL, [AtkType.ALL], 2, 1, False, [0, 0], False))
        return bl, dbl, al, dl, hl