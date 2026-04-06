from Buff import *
from Lightcone import Lightcone
from Attributes import *

class EpochEtchedInGoldenBlood(Lightcone):
    name = "Epoch Etched in Golden Blood"
    path = Path.HARMONY
    baseHP = 953
    baseATK = 635
    baseDEF = 463

    def __init__(self, wearerRole, level=5, targetRole = Role.DPS):
        super().__init__(wearerRole, level)
        self.targetRole = targetRole

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        atkAmount = self.level * 0.16 + 0.48
        bl.append(Buff("EpochEtchedATK", StatTypes.ATK_PERCENT, atkAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useSkl(enemyID)
        BuffAmount = self.level * 0.135 + 0.405
        bl.append(Buff("EpochEtched", StatTypes.DMG_PERCENT, BuffAmount, self.targetRole, [AtkType.SKL], 3, 1, self.targetRole, TickDown.END))
        return bl, dbl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt(enemyID)
        bl.append(Buff("EpochEtchedSP", StatTypes.SKLPT, 1, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        return bl, dbl, al, dl, hl