import logging

from Buff import *
from Character import Character
from Lightcones.Erudition.FlickeringStars import FlickeringStars
from Lightcones.Erudition.EternalCalculus import EternalCalculus
from Lightcones.Erudition.TheSeriousnessOfBreakfast import TheSeriousnessOfBreakfast
from Lightcones.Erudition.TodayIsAnotherPeacefulDay import TodayIsAnotherPeacefulDay
from Planars.RutilantArena import RutilantArena
from Planars.TengokuLivestream import TengokuLivestream
from Planars.PenaconyLandOfTheDreams import PenaconyLandOfTheDreams
from RelicStats import RelicStats
from Relics.GeniusOfBrilliantStars import GeniusOfBrilliantStars
from Relics.ScholarLostInErudition import ScholarLostInErudition
from Result import *
from Turn_Text import Turn
from Healing import *

logger = logging.getLogger(__name__)


class HimekoNova(Character):
    # Standard Character Settings
    name = "HimekoNova"
    path = Path.ERUDITION
    element = Element.FIRE
    scaling = Scaling.ATK
    baseHP = 1125
    baseATK = 757
    baseDEF = 485
    baseSPD = 98
    maxEnergy = 150
    currEnergy = 75
    ultCost = 150
    currAV = 0
    aggro = 75
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0}  # Adjust accordingly

    # Unique Character Properties


    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope
    # With Sparkle:
    # self.relicStats = subs if subs else RelicStats(2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 14, 9, StatTypes.CR_PERCENT, StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT)

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else EternalCalculus(role, 5)
        self.relic1 = r1 if r1 else GeniusOfBrilliantStars(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else RutilantArena(role)
        self.relicStats = subs if subs else RelicStats(8, 2, 2, 2, 2, 3, 2, 2, 2, 2, 12, 6, StatTypes.CR_PERCENT, StatTypes.SPD,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["A","A","E"]
        self.E4StackLimit = 2 if self.eidolon >= 4 else 1

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("HimekoNovaTraceCR", StatTypes.CR_PERCENT, 0.12, self.role))
        bl.append(Buff("HimekoNovaTraceATK", StatTypes.ATK_PERCENT, 0.28, self.role))
        bl.append(Buff("HimekoNovaTraceDMG", StatTypes.DMG_PERCENT, 0.08, self.role))

        return bl, dbl, al, dl, hl, sl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20, self.scaling, 1, "HimekoNovaBasic"))
        return bl, dbl, al, dl, tl, hl, sl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useSkl(enemyID)

        return bl, dbl, al, dl, tl, hl, sl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost

        return bl, dbl, al, dl, tl, hl, sl


    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().ownTurn(turn, result)

        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)

        return bl, dbl, al, dl, tl, hl, sl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)

        return bl, dbl, al, dl, tl, hl, sl

