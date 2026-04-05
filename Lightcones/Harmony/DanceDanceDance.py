from Delay_Text import *
from Lightcone import Lightcone


class DanceDanceDance(Lightcone):
    name = "Dance! Dance! Dance!"
    path = Path.HARMONY
    baseHP = 952.6
    baseATK = 423.36
    baseDEF = 396.90

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt(enemyID)
        adv = self.level * 0.02 + 0.14
        al.append(Advance(f"Dance3{self.wearerRole}", Role.ALL, adv))
        return bl, dbl, al, dl, hl