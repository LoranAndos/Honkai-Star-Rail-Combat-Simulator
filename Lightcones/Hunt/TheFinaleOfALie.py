from Buff import *
from Lightcone import Lightcone
from Attributes import *

class TheFinaleOfALie(Lightcone):
    name = "The Finale of a Lie"
    path = Path.HUNT
    baseHP = 847
    baseATK = 635
    baseDEF = 529
    FuaCount = 0

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        CRAmount = self.level * 0.03 + 0.15
        ATKAmount = self.level * 0.1 + 0.3
        VulAmount = self.level * 0.025 + 0.175
        bl.append(Buff("FinaleCR", StatTypes.CR_PERCENT, CRAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("FinaleATK", StatTypes.CR_PERCENT, ATKAmount, self.wearerRole, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
        dbl.append(Debuff("FinaleVul", self.wearerRole, StatTypes.VULN, VulAmount, Role.ALL, [AtkType.ALL], 3,1, Targeting.AOE))
        return bl, dbl, al, dl, hl

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useFua(enemyID)
        ATKAmount = self.level * 0.1 + 0.3
        VulAmount = self.level * 0.025 + 0.175
        self.FuaCount += 1
        if self.FuaCount % 4 == 0 and self.FuaCount != 0:
            bl.append(Buff("FinaleATK", StatTypes.CR_PERCENT, ATKAmount, self.wearerRole, [AtkType.ALL], 3, 1, Role.SELF,TickDown.END))
            dbl.append(Debuff("FinaleVul", self.wearerRole, StatTypes.VULN, VulAmount, Role.ALL, [AtkType.ALL], 3, 1,Targeting.AOE))
        return bl, dbl, al, dl, hl