from Buff import *
from Lightcone import Lightcone
from Attributes import *


class ResolutionShinesasPearlsOfSweat(Lightcone):
    name = "Resolution Shines as Pearls of Sweat"
    path = Path.NIHILITY
    baseHP = 953
    baseATK = 476
    baseDEF = 331

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useBsc(enemyID)
        shredBuff = self.level * 0.01 + 0.11
        dbl.append(
            Debuff(f"ResoShred({self.wearerRole.name})", self.wearerRole, StatTypes.SHRED, shredBuff, enemyID, [AtkType.ALL],
                   1, 1, False, [0, 0], False))
        return bl, dbl, al, dl, hl


class ResolutionPela(ResolutionShinesasPearlsOfSweat):

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useSkl(enemyID)
        shredBuff = self.level * 0.01 + 0.11
        dbl.append(
            Debuff(f"ResoShred({self.wearerRole.name})", self.wearerRole, StatTypes.SHRED, shredBuff, enemyID, [AtkType.ALL],
                   1, 1, False, [0, 0], False))
        return bl, dbl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt(enemyID)
        shredBuff = self.level * 0.01 + 0.11
        dbl.append(
            Debuff(f"ResoShred({self.wearerRole.name})", self.wearerRole, StatTypes.SHRED, shredBuff, Role.ALL, [AtkType.ALL],
                   1, 1, False, [0, 0], False))
        return bl, dbl, al, dl, hl


class ResolutionJQ(ResolutionPela):
    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

class ResolutionMortenaxBlade(ResolutionJQ):
    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt(enemyID)
        shredBuff = self.level * 0.01 + 0.11
        dbl.append(
            Debuff(f"ResoShred({self.wearerRole.name})", self.wearerRole, StatTypes.SHRED, shredBuff, Role.ALL, [AtkType.ALL],
                   1, 1, False, [0, 0], False))
        return bl, dbl, al, dl, hl