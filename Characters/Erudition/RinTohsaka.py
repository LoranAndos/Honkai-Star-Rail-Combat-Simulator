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
from Healing import *

logger = logging.getLogger(__name__)


class RinTohsaka(Character):
    # Standard Character Settings
    name = "RinTohsaka"
    path = Path.ERUDITION
    element = Element.QUANTUM
    scaling = Scaling.ATK
    baseHP = 1048
    baseATK = 699
    baseDEF = 461
    baseSPD = 102
    maxEnergy = 160
    currEnergy = 80
    ultCost = 160
    currAV = 0
    aggro = 75
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.FUA: 0}  # Adjust accordingly

    # Unique Character Properties
    GemEnergy = 20
    SPAmount = 0
    EnhancedSkill = False
    SkillGemMultiplier = 1
    HasShadowGem = False
    ShadowGemValue = 0
    ArcherInTeam = False
    Tech = True

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
        self.rotation = rotation if rotation else ["E","A","A"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("RinTohsakaTraceCD", StatTypes.CD_PERCENT, 0.373, self.role))
        bl.append(Buff("RinTohsakaTraceATK", StatTypes.ATK_PERCENT, 0.18, self.role))
        bl.append(Buff("RinTohsakaTraceDMG", StatTypes.DMG_PERCENT, 0.08, self.role))
        bl.append(Buff("RinTohsakaTrace1ATK", StatTypes.ATK_PERCENT, 1.50, self.role))
        bl.append(Buff("RinTohsakaTrace1Shred", StatTypes.SHRED, 0.20, self.role))
        if self.eidolon >= 2:
            bl.append(Buff("E2DMG", StatTypes.DMG_PERCENT, 0.30, self.role, [AtkType.SKL], 1, 1, Role.SELF, TickDown.PERM))
            bl.append(Buff("E2IDM", StatTypes.INDEPENDENTDAMAGEMULTIPLIER, 0.10, Role.ALL, [AtkType.SKL], 1, 1, Role.SELF, TickDown.PERM))
        if self.eidolon == 6:
            bl.append(Buff("RinTohsakaE6Pen", StatTypes.PEN, 0.20, self.role))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20, self.scaling, 1, "RinTohsakaBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e3Mul = 0.99 if self.eidolon >= 3 else 0.90
        e3MulNormal = 1.98 if self.eidolon >= 3 else 1.80
        if self.EnhancedSkill and not self.HasShadowGem:
            ExtraHits = min(self.GemEnergy//3,33)
            logger.info(f"Amount of extraHits from EnhancedSkill = {ExtraHits} from {self.GemEnergy} Gem Energy")
            SPUsage = 0 if self.SPAmount <= 2 else -(self.SPAmount -2)
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.SKL], [self.element],
                     [e3Mul, 0], [20, 0], 0, self.scaling, 0, "RinTohsakaSkillAOE"))
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.SKL], [self.element],
                     [e3Mul*ExtraHits, 0], [2*ExtraHits, 0], 30, self.scaling, SPUsage, "RinTohsakaSkillSingle"))
            bl.append(Buff("EnhancedSkillSPD", StatTypes.SPD_PERCENT, 0.20, self.role, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
            self.EnhancedSkill = False
            if self.eidolon >= 1 and self.GemEnergy >= 30:
                self.HasShadowGem = True
                self.ShadowGemValue = 3 * ExtraHits
                self.EnhancedSkill = True
            self.GemEnergy -= 3*ExtraHits
            self.SkillGemMultiplier = 2
        elif self.EnhancedSkill and self.HasShadowGem:
            ExtraHits = min(self.ShadowGemValue//3,33)
            logger.info(f"Amount of extraHits from EnhancedSkill = {ExtraHits} from {self.ShadowGemValue} Shadow Gem Energy")
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.SKL], [self.element],
                     [e3Mul, 0], [20, 0], 0, self.scaling, 0, "RinTohsakaSkillAOE"))
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.SKL], [self.element],
                     [e3Mul*ExtraHits, 0], [2*ExtraHits, 0], 30, self.scaling, 0, "RinTohsakaSkillSingle"))
            bl.append(Buff("EnhancedSkillSPD", StatTypes.SPD_PERCENT, 0.20, self.role, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
            self.EnhancedSkill = False
            self.HasShadowGem = False
            self.ShadowGemValue = 0
        else:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.SKL], [self.element],
                     [e3MulNormal, 0], [20, 0], 30, self.scaling, -1, "RinTohsakaSkill"))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e5Main = 4.40 if self.eidolon >= 5 else 4.0
        e5Side = 2.20 if self.eidolon >= 5 else 2.0
        e5Vuln = 0.22 if self.eidolon >= 5 else 0.20
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ULT], [self.element],
                       [e5Main, 0], [10, 0], 0, self.scaling, 0, "RinTohsakaUltMain"))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT], [self.element],
                       [e5Side, 0], [20, 0], 5, self.scaling, 1, "RinTohsakaUltSide"))
        dbl.append(Debuff("RinTohsakaUltVuln", self.role, StatTypes.VULN, e5Vuln, Role.ALL, [AtkType.ALL], 3,1,Targeting.AOE))
        self.GemEnergy += 30 if self.eidolon == 6 else 12
        logger.info(f"Rin has obtained 12 Gem Energy from Ultimate and now has {self.GemEnergy} Gem Energy")
        if self.eidolon >= 6:
            bl, dbl, al, dl, tl, hl = self.extendLists(bl, dbl, al, dl, tl, hl, *self.useSkl(-1))
        return bl, dbl, al, dl, tl, hl

    def useJointAttack(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useJointAttack(enemyID)
        e3Mult = 3.3 if self.eidolon >= 3 else 3.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.FUA],
                       [self.element], [e3Mult, 0], [20, 0], 10, self.scaling, 4, "RinTohsakaJointAttack"))
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        e5CD = 1.10 if self.eidolon >= 5 else 1.00
        if turn.spChange != 0:
            self.GemEnergy += abs(turn.spChange) * self.SkillGemMultiplier
            bl.append(Buff("TalentCD", StatTypes.CD_PERCENT, e5CD, turn.charRole, [AtkType.ALL], 2, 1, turn.charRole, TickDown.END))
            logger.info(f"Rin has obtained {abs(turn.spChange) * self.SkillGemMultiplier} Gem Energy from SP and now has {self.GemEnergy} Gem Energy")
            self.SkillGemMultiplier = 1
            if self.eidolon >= 4:
                bl.append(Buff("E4RinSpd", StatTypes.SPD_PERCENT, 0.10, turn.charRole, [AtkType.ALL], 3, 1, turn.charRole, TickDown.END))
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        e5CD = 1.10 if self.eidolon >= 5 else 1.00
        if turn.spChange != 0:
            self.GemEnergy += abs(turn.spChange)
            bl.append(Buff("RinTalentCD", StatTypes.CD_PERCENT, e5CD, turn.charRole, [AtkType.ALL], 2, 1, turn.charRole, TickDown.END))
            logger.info(f"Rin has obtained {abs(turn.spChange)} Gem Energy from SP and now has {self.GemEnergy} Gem Energy")
            if self.eidolon >= 4:
                bl.append(Buff("E4RinSpd", StatTypes.SPD_PERCENT, 0.10, turn.charRole, [AtkType.ALL], 3, 1, turn.charRole, TickDown.END))
        if turn.moveName == "ArcherJointAttack":
            bl, dbl, al, dl, tl, hl = self.extendLists(bl, dbl, al, dl, tl, hl, *self.useJointAttack(-1))
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.SPAmount = specialRes.attr1
        self.ArcherInTeam = specialRes.attr2
        if self.Tech:
            self.GemEnergy += 10
            logger.info(f"Rin has obtained 10 Gem Energy from Technique and now has {self.GemEnergy} Gem Energy")
            self.Tech = False
        return bl, dbl, al, dl, tl, hl

    def takeTurn(self) -> str:
        if self.SPAmount >= 7 or self.GemEnergy >= 15:
            self.EnhancedSkill = True
            logger.info(f"Rin can use Enhanced Skill")
        return super().takeTurn()