import logging

from Buff import *
from Character import Character
from Delay_Text import *
from Lightcones.Harmony.EarthlyEscapade import EarthlyEscapade
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
    overflowSP = 0
    currentSP = 0
    maxSP = 5
    SkillSP = -1

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, targetRole=Role.DPS, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else EarthlyEscapade(role)
        self.relic1 = r1 if r1 else ScholarLostInErudition(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else RutilantArena(role)
        self.relicStats = subs if subs else RelicStats(13, 4, 0, 4, 4, 0, 3, 3, 3, 3, 0, 11, StatTypes.CD_PERCENT, StatTypes.Spd,
                                                       StatTypes.HP_PERCENT,StatTypes.ERR_PERCENT)
        self.targetRole = targetRole
        self.rotation = rotation if rotation else ["E"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("SparkleTraceHP", StatTypes.HP_PERCENT, 0.28, self.role))
        bl.append(Buff("SparkleTraceCD", StatTypes.CD_PERCENT, 0.24, self.role))
        bl.append(Buff("SparkleTraceERS", StatTypes.ERS_PERCENT, 0.10, self.role))
        bl.append(Buff("SparkleTeamATK", StatTypes.ATK_PERCENT, 0.45, Role.ALL))
        if self.eidolon >= 1:
            bl.append(Buff("SparkleE1SPD", StatTypes.SPD_PERCENT, 0.15, self.role, [AtkType.ALL], 2, 1, Role.SELF, TickDown.START))
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
        tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.SKL], [self.element], [0, 0], [0, 0], 30,
                       self.scaling, self.SkillSP, "SparkleSkill"))
        if self.eidolon == 6:
            bl.append(Buff("SparkleCD", StatTypes.CD_PERCENT, self.cdStat * (e3CDMul+0.3) + e3CDFlat, Role.ALL,[AtkType.ALL], 2, 1, self.targetRole, TickDown.END))
            bl.append(Buff("SparklePEN", StatTypes.PEN, 0.10, Role.ALL, [AtkType.ALL], 2, 1, self.targetRole,TickDown.END))
        else:
            bl.append(Buff("SparkleCD", StatTypes.CD_PERCENT, self.cdStat * e3CDMul + e3CDFlat, self.targetRole,[AtkType.ALL], 2, 1, self.targetRole, TickDown.END))
            bl.append(Buff("SparklePEN", StatTypes.PEN, 0.10, self.targetRole, [AtkType.ALL], 2, 1, self.targetRole,TickDown.END))
        self.SkillSP = -1
        if self.role != self.targetRole:
            al.append(Advance("SparkleForward", self.targetRole, 0.50))
        if self.eidolon >= 1:
            bl.append(Buff("SparkleE1SPD", StatTypes.SPD_PERCENT, 0.15, self.role, [AtkType.ALL], 2, 1, Role.SELF, TickDown.START))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e4SP = 7 if self.eidolon >= 4 else 6
        e5VUL = 0.0648 if self.eidolon >= 5 else 0.06
        tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ULT], [self.element],
                       [0, 0], [0, 0], 5, self.scaling, e4SP, "SparkleUlt"))  # 6 SP gain
        bl.append(Buff("SparkleUltVUL", StatTypes.VULN, e5VUL*3, Role.ALL,[AtkType.ALL], 3, 1, Role.SELF,TickDown.END))
        if self.eidolon >= 1:
            bl.append(Buff("SparkleE1ATK", StatTypes.ATK_PERCENT, 0.40, Role.ALL, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        if result.turnName == "SparkleUlt":
            # Calculate overflow: if current SP + 6 > maxSP, record overflow up to 10
            overflow = max(0, self.currentSP + 6 - self.maxSP)
            self.overflowSP = min(overflow, 10)
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        e5VUL = 0.044 if self.eidolon >= 5 else 0.04
        if turn.spChange <= -1:
            bl.append(Buff("SparkleVUL", StatTypes.VULN, e5VUL, Role.ALL,[AtkType.ALL], 2, 3, Role.SELF, TickDown.END))
            if self.eidolon >= 2:
                bl.append(Buff("SparkleE2SHRED", StatTypes.SHRED, 0.10, Role.ALL,[AtkType.ALL], 2, 3, Role.SELF, TickDown.END))
        if turn.spChange <= -1 and turn.charRole == self.targetRole:
            spConsumed = abs(min(turn.spChange, 0))
            for _ in range(spConsumed):
                bl.append(Buff("SparkleTalentERR", StatTypes.ERR_T, spConsumed, self.role,[AtkType.ALL], 1, 100, Role.SELF, TickDown.START))
        elif turn.spChange <= -1 and turn.charRole == self.targetRole and turn.charName == "Sparxie":
            spConsumed = abs(min(turn.spChange, 0))
            for _ in range(spConsumed):
                bl.append(Buff("SparkleTalentERR", StatTypes.ERR_T, spConsumed+10, self.role,[AtkType.ALL], 1, 100, Role.SELF, TickDown.START))
        if turn.moveName == "SparxieSkill":
            self.SkillSP = 0
        if self.overflowSP > 0:
            spToRestore = min(self.overflowSP, self.maxSP - self.currentSP)
            if spToRestore > 0:
                tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.SPECIAL],
                               [self.element], [0, 0], [0, 0], 0, self.scaling,
                               spToRestore, "SparkleOverflowSP"))
                self.overflowSP -= spToRestore
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        if self.startSP:
            self.startSP = False
            tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.SPECIAL],
                           [self.element], [0, 0], [0, 0], 0, self.scaling, 3, "SparkleTechSP"))
            bl.append(Buff("SparkleTechERR", StatTypes.ERR_T, 20, self.role,
                           [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        self.cdStat = specialRes.attr1
        self.currentSP = specialRes.attr2  # current SP from spTracker
        self.maxSP = specialRes.attr3  # max SP from spTracker
        return bl, dbl, al, dl, tl, hl