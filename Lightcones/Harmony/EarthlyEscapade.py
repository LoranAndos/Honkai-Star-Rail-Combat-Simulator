from Buff import Buff
from Delay_Text import *
from Lightcone import Lightcone


class EarthlyEscapade(Lightcone):
    name = "Earthly Escapade"
    path = Path.HARMONY
    baseHP = 1164
    baseATK = 529
    baseDEF = 463

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        cd = self.level * 0.07 + 0.25
        teamCR = self.level * 0.01 + 0.09
        teamCD = self.level * 0.07 + 0.21
        bl.append(Buff("EarthlyCD", StatTypes.CD_PERCENT, cd, self.wearerRole))
        bl.append(Buff("EarthlyTeamCR", StatTypes.CR_PERCENT, teamCR, Role.ALL))
        bl.append((Buff("EarthlyTeamCD", StatTypes.CD_PERCENT, teamCD, Role.ALL)))
        return bl, dbl, al, dl, hl