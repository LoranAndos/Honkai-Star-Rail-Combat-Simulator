from Buff import *
from Lightcone import Lightcone
from Attributes import *

class WhenSheDecidedToSee(Lightcone):
    name = "When She Decided to See"
    path = Path.ELATION
    baseHP = 1058
    baseATK = 529
    baseDEF = 529

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dl, al, dl, hl = super().equip()
        SpdBuff = self.level * 0.03 + 0.15
        bl.append(Buff("DecidedToSeeSPD", StatTypes.SPD_PERCENT, SpdBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("DecidedToSeeSPD", StatTypes.ERR_F, 15, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        return bl, dl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dl, al, dl, hl = super().equip()
        CRBuff = self.level * 0.01 + 0.09
        CDBuff = self.level * 0.075 + 0.225
        ERBuff = self.level * 0.02 + 0.1
        bl.append(Buff("DecidedToSeeCR", StatTypes.CR_PERCENT, CRBuff, self.wearerRole, [AtkType.ALL], 3, 1, Role.ALL, TickDown.START))
        bl.append(Buff("DecidedToSeeCD", StatTypes.CD_PERCENT, CDBuff, self.wearerRole, [AtkType.ALL], 3, 1, Role.ALL,TickDown.START))
        bl.append(Buff("DecidedToSeeER", StatTypes.ERR_PERCENT, ERBuff, self.wearerRole, [AtkType.ALL], 3, 1, Role.SELF,TickDown.START))
        return bl, dl, al, dl, hl
