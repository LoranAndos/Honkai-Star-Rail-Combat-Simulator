from Buff import *
from Lightcone import Lightcone
from Attributes import *

class Passkey(Lightcone):
    name = "Passkey"
    path = Path.ERUDITION
    baseHP = 741
    baseATK = 370
    baseDEF = 265

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useSkl(enemyID)
        errAmount = self.level * 1 + 7
        bl.append(Buff("PasskeyERR_F", StatTypes.ERR_F, errAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        return bl, dbl, al, dl, hl