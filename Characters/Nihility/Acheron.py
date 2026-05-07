import logging

from Buff import *
from Character import Character
from Lightcones.Hunt.TheFinaleOfALie import TheFinaleOfALie
from Planars.CityOfConvergingStars import CityOfConvergingStars
from RelicStats import RelicStats
from Relics.TheAshblazingGrandDuke import DukeAshveil
from Result import *
from Turn_Text import Turn
from Healing import *
from math import floor
from HPChecks import getEnemyHPRatio

logger = logging.getLogger(__name__)


class Acheron(Character):
    # Standard Character Settings
    name = "Acheron"
    path = Path.NIHILITY
    element = Element.LIGHTNING
    scaling = Scaling.ATK
    baseHP = 1125
    baseATK = 699
    baseDEF = 437
    baseSPD = 101
    maxEnergy = 9
    currEnergy = 5
    ultCost = 9
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0}  # Adjust accordingly

    # Unique Character Properties
    specialEnergy = True
    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else TheFinaleOfALie(role, 1)
        self.relic1 = r1 if r1 else DukeAshveil(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else CityOfConvergingStars(role)
        self.relicStats = subs if subs else RelicStats(6, 2, 2, 2, 7, 2, 2, 2, 2, 2, 12, 4, StatTypes.CR_PERCENT, StatTypes.SPD,
                                                       StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["E"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("AcheronTraceCD", StatTypes.CD_PERCENT, 0.24, self.role))
        bl.append(Buff("AcheronTraceATK", StatTypes.ATK_PERCENT, 0.28, self.role))
        bl.append(Buff("AcheronTraceDMG", StatTypes.DMG_PERCENT, 0.08, self.role))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 0, self.scaling, 1, "AcheronBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)

        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost

        return bl, dbl, al, dl, tl, hl


    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)

        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)

        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)

        return bl, dbl, al, dl, tl, hl