from Buff import *
from Lightcone import Lightcone
from Attributes import *

class HeyOverHere(Lightcone):
    name = "Hey, Over Here"
    path = Path.ABUNDANCE
    baseHP = 953
    baseATK = 423
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dl, al, dl, hl = super().equip()
        BuffAmount = self.level * 0.01 + 0.07
        bl.append(Buff("HeyOverHereHP", StatTypes.HP_PERCENT, BuffAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dl, al, dl, hl

    def useSkl(self, enemyID=-1):
        bl, dl, al, dl, hl = super().useSkl()
        oghAmount = self.level * 0.03 + 0.13
        bl.append(Buff("HeyOverHere_SKLOGH", StatTypes.OGH_PERCENT, oghAmount, self.wearerRole, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        return bl, dl, al, dl, hl