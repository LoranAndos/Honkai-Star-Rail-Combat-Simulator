from Buff import *
from Lightcone import Lightcone
from Healing import *

class WarmthShortensColdNights(Lightcone):
    name = "Warmth Shortens Cold Nights"
    path = Path.ABUNDANCE
    baseHP = 1058
    baseATK = 370
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)


    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        hpAmount = self.level * 0.04 + 0.12
        bl.append(Buff("WarmthShortensHP", StatTypes.HP_PERCENT, hpAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useBsc(enemyID)
        HealAmount = self.level * 0.005 + 0.015
        hl.append(Healing("WarmthShortensHeal_BSC", [HealAmount,0], Scaling.MAXHP, Role.ALL, self.wearerRole, Targeting.AOE))
        return bl, dbl, al, dl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useSkl(enemyID)
        HealAmount = self.level * 0.005 + 0.015
        hl.append(Healing("WarmthShortensHeal_BSC", [HealAmount,0], Scaling.MAXHP, Role.ALL, self.wearerRole, Targeting.AOE))
        return bl, dbl, al, dl, hl