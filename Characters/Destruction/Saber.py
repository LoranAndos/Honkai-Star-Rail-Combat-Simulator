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


class Saber(Character):
    # Standard Character Settings
    name = "Saber"
    path = Path.DESTRUCTION
    element = Element.WIND
    scaling = Scaling.ATK
    baseHP = 1242
    baseATK = 602
    baseDEF = 655
    baseSPD = 101
    maxEnergy = 360
    currEnergy = 216
    ultCost = 360
    currAV = 0
    aggro = 125
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.FUA: 0}  # Adjust accordingly

    # Unique Character Properties
    EnhancedBasic = False
    CoreResonance = 1
    Tech = True
    overflowEnergy = 0.0
    CoreResonanceTally = 0
    E2CoreResonanceTally = 0
    CoreResonanceOld = 0
    UltCounter = 0
    Mana_Burst = True
    JointAttackMultiplier = 1.0
    GilgameshEidolon = 0

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

    def addEnergy(self, amount: float):
        """Outside enhanced state: energy above maxEnergy spills into overflowEnergy (cap 80).
        Inside enhanced state: normal cap at maxEnergy, no overflow accumulation."""
        EnergyLimit = 200 if self.eidolon == 6 else 120
        space = self.maxEnergy - self.currEnergy
        if amount > space:
            # Fill currEnergy to max, put the remainder into overflow
            self.currEnergy = self.maxEnergy
            self.overflowEnergy = min(EnergyLimit, self.overflowEnergy + (amount - space))
        else:
            self.currEnergy = min(self.maxEnergy, self.currEnergy + amount)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("SaberTraceHP", StatTypes.HP_PERCENT, 0.10, self.role))
        bl.append(Buff("SaberTraceCR", StatTypes.CR_PERCENT, 0.12, self.role))
        bl.append(Buff("SaberTraceDMG", StatTypes.DMG_PERCENT, 0.224, self.role))
        bl.append(Buff("SaberTrace1CR", StatTypes.CR_PERCENT, 0.20, self.role))
        if self.eidolon >= 1:
            bl.append(Buff("SaberE1DMG", StatTypes.DMG_PERCENT, 0.60, self.role, [AtkType.ULT]))
        if self.eidolon >= 4:
            bl.append(Buff("SaberE4Pen", StatTypes.WINPEN, 0.08, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        if self.eidolon == 6:
            bl.append(Buff("SaberE6Pen", StatTypes.WINPEN, 0.20, self.role, [AtkType.ULT], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        e3MulEnhancedSmall = 1.65 if self.eidolon >= 3 else 1.5
        e3MulEnhancedBig = 2.42 if self.eidolon >= 3 else 2.2
        enemyCount = self._getEnemyCount()
        if not self.EnhancedBasic:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20, self.scaling, 1, "SaberBasic"))
        else:
            self.CoreResonance += 2
            logger.debug(f"{self.name} got 2 Core Resonance from Enhanced basic")
            if enemyCount == 2:
                ExtraMultiplier = e3MulEnhancedSmall
            elif enemyCount == 1:
                ExtraMultiplier = e3MulEnhancedBig
            else:
                ExtraMultiplier = 0
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.BSC], [self.element],
                     [e3MulEnhancedSmall + ExtraMultiplier, 0], [20, 0], 30, self.scaling, 1, "SaberEnhancedBasic"))
            self.Mana_Burst = True
            self.EnhancedBasic = False
        if self.eidolon >= 1:
            self.CoreResonance += 1
            logger.debug(f"{self.name} got 1 Core Resonance from Eidolon 1")
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e5MulBig = 1.65 if self.eidolon >= 5 else 1.5
        e5MulSmall = 0.825 if self.eidolon >= 5 else 0.75
        e2ExtraMultiplier = 0.07 if self.eidolon >= 2 else 0
        if self.currEnergy + 8 * self.CoreResonance >= self.ultCost:
            CoreExtraMultiplier = (0.154+e2ExtraMultiplier) * self.CoreResonance if self.eidolon >= 5 else (0.14+e2ExtraMultiplier) * self.CoreResonance
            logger.debug(f"{self.name} used {self.CoreResonance} Core Resonance for Skill")
            self.CoreResonance = 0
            if self.Mana_Burst:
                self.Mana_Burst = False
                SpChange = 0
                HasUsedManaBurst = True
            else:
                SpChange = -1
                HasUsedManaBurst = False
        else:
            CoreExtraMultiplier = 0
            SpChange = -1
            HasUsedManaBurst = False
            self.CoreResonance += 3
            logger.debug(f"{self.name} got 3 Core Resonance from Skill")
        bl.append(Buff("Trace3CD", StatTypes.CD_PERCENT, 0.50, self.role, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.BLAST, [AtkType.SKL], [self.element],
                       [e5MulBig+CoreExtraMultiplier, e5MulSmall+CoreExtraMultiplier], [20, 10], 30, self.scaling, SpChange, "SaberSkill"))
        if CoreExtraMultiplier != 0:
            bl.append(Buff("SkillEnergy", StatTypes.ERR_F, 8*CoreExtraMultiplier, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
            if HasUsedManaBurst:
                al.append(Advance("Trace1Advance", self.role, 1.00))
        if self.eidolon >= 1:
            self.CoreResonance += 1
            logger.debug(f"{self.name} got 1 Core Resonance from Eidolon 1")
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e3MulBig = 3.08 if self.eidolon >= 3 else 2.8
        e3MulSmall = 1.21 if self.eidolon >= 3 else 1.1
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT], [self.element],
                       [e3MulBig*self.JointAttackMultiplier, 0], [40, 0], 0, self.scaling, 0, "SaberUltBig"))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ULT], [self.element],
                       [e3MulSmall*10*self.JointAttackMultiplier, 0], [20, 0], 5, self.scaling, 0, "SaberUltSmall"))
        self.JointAttackMultiplier = 1.0
        self.CoreResonance += 3
        logger.debug(f"{self.name} got 3 Core Resonance from Talent")
        self.EnhancedBasic = True
        if self.overflowEnergy > 0:
            self.currEnergy = min(self.maxEnergy, self.currEnergy + self.overflowEnergy)
            logger.debug(f"{self.name} transferred {self.overflowEnergy:.1f} overflow energy on Ult entry")
            self.overflowEnergy = 0.0
        if self.eidolon >= 4:
            bl.append(Buff("SaberE4ExtraPen", StatTypes.WINPEN, 0.04, self.role, [AtkType.ALL], 1, 3, Role.SELF, TickDown.PERM))
        if self.eidolon == 6:
            if self.UltCounter % 3 == 0:
                self.currEnergy = self.currEnergy + 300
            self.UltCounter += 1
        return bl, dbl, al, dl, tl, hl

    def useJointAttack(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useJointAttack(enemyID)
        e3SaberMult = 4.4 if self.GilgameshEidolon>= 3 else 4.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.FUA],
                       [self.element], [e3SaberMult, 0], [0, 0], 120, self.scaling, 0, "SaberJointAttack"))
        self.JointAttackMultiplier = 2.0
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        DmgBuff = 0.66 if self.eidolon >= 5 else 0.60
        if turn.moveName in UltimateList:
            bl.append(Buff("TalentDMG", StatTypes.DMG_PERCENT, DmgBuff, self.role, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
            self.CoreResonance += 3
            logger.debug(f"{self.name} got 3 Core Resonance from Talent")
        if turn.moveName == "GilgameshJointAttack":
            bl, dbl, al, dl, tl, hl = self.extendLists(bl, dbl, al, dl, tl, hl, *self.useJointAttack(-1))
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.GilgameshEidolon = specialRes.attr1
        if self.Tech:
            self.Tech = False
            bl.append(Buff("TalentATK", StatTypes.ATK_REDUCTION, 0.35, self.role, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
            self.CoreResonance += 2
            logger.debug(f"{self.name} got 2 Core Resonance from Technique")
        CoreResonance_diff = self.CoreResonance - self.CoreResonanceOld
        if CoreResonance_diff > 0:
            self.CoreResonanceTally = min(self.CoreResonanceTally + CoreResonance_diff, 8)
            self.E2CoreResonanceTally = min(self.CoreResonanceTally + CoreResonance_diff, 15)
        self.CoreResonanceOld = self.CoreResonance
        bl.append(Buff("Trace3CDExtra", StatTypes.CD_PERCENT, 0.04*self.CoreResonanceTally, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        if self.eidolon >= 2:
            bl.append(Buff("Trace3CDExtra", StatTypes.SHRED, 0.01 * self.CoreResonanceTally, self.role, [AtkType.ALL], 1,1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, tl, hl

    def takeTurn(self) -> str:
        return "A" if self.EnhancedBasic else "E"

    def _getEnemyCount(self):
        return self.get_alive_enemy_count()