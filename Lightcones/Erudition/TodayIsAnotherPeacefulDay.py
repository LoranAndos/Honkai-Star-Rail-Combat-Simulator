from Buff import *
from Lightcone import Lightcone
from Attributes import *
from MainFunctions import Special

class TodayIsAnotherPeacefulDay(Lightcone):
    name = "The Seriousness of Breakfast"
    path = Path.ERUDITION
    baseHP = 847
    baseATK = 529
    baseDEF = 331

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def specialStart(self, special: Special):
        bl, dbl, al, dl, hl = super().specialStart(special)
        DmgBuff = 0.0005 * self.level + 0.0015
        if special.specialName == "RinTohsaka":
            EnergyStat = special.attr3
            bl.append(Buff("PeacefulDayDMG", StatTypes.DMG_PERCENT, min(EnergyStat,160)*DmgBuff, self.wearerRole,[AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl