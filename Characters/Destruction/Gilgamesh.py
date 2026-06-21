import logging

from Buff import *
from Character import Character
from Lightcones.Erudition.FlickeringStars import FlickeringStars
from Lightcones.Erudition.EternalCalculus import EternalCalculus
from Planars.RutilantArena import RutilantArena
from Planars.TengokuLivestream import TengokuLivestream
from RelicStats import RelicStats
from Relics.GeniusOfBrilliantStars import GeniusOfBrilliantStars
from Result import *
from Turn_Text import Turn
from Delay_Text import Advance
from Healing import *

logger = logging.getLogger(__name__)


class Gilgamesh(Character):
    # Standard Character Settings
    name = "Gilgamesh"
    path = Path.DESTRUCTION
    element = Element.LIGHTNING
    scaling = Scaling.ATK
    baseHP = 1125
    baseATK = 718
    baseDEF = 509
    baseSPD = 97
    maxEnergy = 360
    currEnergy = 180
    ultCost = 360
    currAV = 0
    aggro = 125
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.FUA: 0}  # Adjust accordingly

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
        self.relicStats = subs if subs else RelicStats(8, 2, 2, 2, 2, 3, 2, 2, 2, 2, 14, 2, StatTypes.CR_PERCENT, StatTypes.SPD_PERCENT,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["E"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("GilgameshTraceATK", StatTypes.ATK, 0.18, self.role))
        bl.append(Buff("GilgameshTraceCR", StatTypes.CR_PERCENT, 0.187, self.role))
        bl.append(Buff("GilgameshTraceDMG", StatTypes.DMG_PERCENT, 0.08, self.role))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20, self.scaling, 1, "GilgameshBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e3Shred = 0.33 if self.eidolon >= 3 else 0.30
        bl.append(Buff("GilgameshSKLShred", StatTypes.SHRED, e3Shred, self.role, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))

        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)

        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)

        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)

        return bl, dbl, al, dl, tl, hl

    def takeTurn(self) -> str:
        return "A" if self.EnhancedBasic else "E"