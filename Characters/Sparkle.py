import logging

from Buff import *
from Character import Character
from Delay_Text import *
from Lightcones.CruisingInTheStellarSea import CruisingInTheStellarSea
from Planars.RutilantArena import RutilantArena
from RelicStats import RelicStats
from Relics.ScholarLostInErudition import ScholarLostInErudition
from Result import *
from Turn_Text import Turn
from Healing import *

logger = logging.getLogger(__name__)


class Sparkle(Character):
    # Standard Character Settings
    name = "Sparkle"
    path = Path.HARMONY
    element = Element.QUANTUM
    scaling = Scaling.ATK
    baseHP = 1397.1
    baseATK = 523.91
    baseDEF = 485.10
    baseSPD = 101
    maxEnergy = 110
    currEnergy = 55
    ultCost = 110
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.FUA: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0}  # Adjust accordingly

    # Unique Character Properties
    cdStat = 0
    startSP = True

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, targetRole=Role.DPS, quaAllies=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else CruisingInTheStellarSea(role)
        self.relic1 = r1 if r1 else ScholarLostInErudition(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else RutilantArena(role)
        self.relicStats = subs if subs else RelicStats(13, 4, 0, 4, 4, 0, 3, 3, 3, 3, 0, 11, StatTypes.CD_PERCENT, StatTypes.Spd,
                                                       StatTypes.HP_PERCENT,StatTypes.ERR_PERCENT)
        self.targetRole = targetRole
        self.quaAllies = quaAllies
        self.rotation = rotation if rotation else ["E"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("SparkleTraceHP", StatTypes.HP_PERCENT, 0.28, self.role))
        bl.append(Buff("SparkleTraceCD", StatTypes.CD_PERCENT, 0.24, self.role))
        bl.append(Buff("SparkleTraceERS", StatTypes.ERS_PERCENT, 0.10, self.role))
        atkBoost = [0, 0.05, 0.15, 0.30]
        bl.append(Buff("SparkleTeamATK", StatTypes.ATK_PERCENT, 0.15 + atkBoost[self.quaAllies], Role.ALL))
        e5DMG = 0.066 if self.eidolon >= 5 else 0.06
        bl.append(Buff("SparkleDMG", StatTypes.DMG_PERCENT, e5DMG * 3, Role.ALL))
        if self.eidolon >= 2:
            bl.append(Buff("SparkleE2SHRED", StatTypes.SHRED, 0.24, Role.ALL))
        if self.eidolon == 6:
            bl.append(Buff("SparkleE6CD", StatTypes.CD_PERCENT, 0.30, Role.ALL))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 30, self.scaling, 1, "SparkleBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e3CDMul = 0.264 if self.eidolon >= 3 else 0.24
        e3CDFlat = 0.486 if self.eidolon >= 3 else 0.45
        bl.append(Buff("SparkleCD", StatTypes.CD_PERCENT, self.cdStat * e3CDMul + e3CDFlat, self.targetRole, turns=2,
                       tickDown=self.targetRole, tdType=TickDown.START))
        tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.SKL], [self.element], [0, 0], [0, 0], 30,
                       self.scaling, -1, "SparkleSkill"))
        if self.role != self.targetRole:
            al.append(Advance("SparkleForward", self.targetRole, 0.50))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e1Turns = 3 if self.eidolon >= 1 else 2
        e4SP = 5 if self.eidolon >= 4 else 4
        e5DMG = 0.108 if self.eidolon >= 5 else 0.1
        tl.append(
            Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ULT], [self.element], [0, 0], [0, 0], 5, self.scaling,
                 e4SP, "SparkleUlt"))
        bl.append(Buff("SparkleUltDMG", StatTypes.DMG_PERCENT, e5DMG * 3, Role.ALL, turns=e1Turns, tdType=TickDown.END))
        if self.eidolon >= 1:
            bl.append(Buff("SparkleE1ATK", StatTypes.ATK_PERCENT, 0.40, Role.ALL, turns=3, tdType=TickDown.END))
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        if self.startSP:
            self.startSP = False
            tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.SPECIAL], [self.element], [0, 0], [0, 0], 0,
                           self.scaling, 3, "SparkleTechSP"))
        self.cdStat = specialRes.attr1
        return bl, dbl, al, dl, tl, hl
