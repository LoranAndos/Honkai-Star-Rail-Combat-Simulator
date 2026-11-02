from Buff import *
from Lightcone import Lightcone
from Attributes import *
from Character import Character
from Healing import Healing
from math import floor

class SeeYouAtTheWorldsEnd(Lightcone):
    name = "See You at the World's End!"
    path = Path.ELATION
    baseHP = 847
    baseATK = 476
    baseDEF = 397

    CD_PER_ELATION = 0.10
    CD_AHA = 0.20

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)
        self._worldsEndRole = wearerRole

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        ElationCD = self.level * 0.01 + 0.05
        AhaCD = self.level * 0.02 + 0.10
        team = Character._current_player_team or []
        elationCount = sum(1 for c in team if c.path == Path.ELATION)
        cd = ElationCD * elationCount
        if any(c.name == "AeonAha" for c in team):
            cd += AhaCD
        bl.append(Buff("SeeYouAtTheWorldsEndCD", StatTypes.CD_PERCENT, cd,self.wearerRole, [AtkType.ALL], 1, 1,
                       Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl, sl