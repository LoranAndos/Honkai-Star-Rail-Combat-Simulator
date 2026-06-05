from Buff import *
from Lightcone import Lightcone
from Attributes import *

class TheHellWhereIdealsBurn(Lightcone):
    name = "The Hell Where Ideals Burn"
    path = Path.HUNT
    baseHP = 953
    baseATK = 582
    baseDEF = 529
    SkillCount = 0

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        CRAmount = self.level * 0.04 + 0.12
        ATKAmount = self.level * 0.1 + 0.3
        bl.append(Buff("IdealsBurnCR", StatTypes.CR_PERCENT, CRAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("IdealsBurnATK", StatTypes.ATK_PERCENT, ATKAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useSkl(enemyID)
        ATKAmount = self.level * 0.025 + 0.075
        self.SkillCount += 1
        bl.append(Buff("IdealsBurnSKLATK", StatTypes.ATK_PERCENT, ATKAmount*min(self.SkillCount,4), self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl