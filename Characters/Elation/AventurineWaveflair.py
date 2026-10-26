import logging

from Buff import *
from Character import Character
from Lightcones.Elation.DazzledByAFloweryWorld import DazzledByAFloweryWorld
from Lightcones.Elation.MushyShroomyAdventures import MushyShroomysAdventuresSparxie
from Planars.TengokuLivestream import TengokuLivestream
from RelicStats import RelicStats
from Relics.EverGloriousMagicalGirl import EverGloriousMagicalGirl
from Result import *
from Turn_Text import Turn
from Healing import *
from random import random
from math import floor

logger = logging.getLogger(__name__)


class AventurineWaveflair(Character):
    # Standard Character Settings
    name = "AventurineWaveflair"
    path = Path.ELATION
    element = Element.QUANTUM
    scaling = Scaling.ATK
    baseHP = 1164
    baseATK = 485
    baseDEF = 606
    baseSPD = 107
    maxEnergy = 130
    currEnergy = 65
    ultCost = 130
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.ELAPUNCH: 0, AtkType.ELABANGER: 0}  # Adjust accordingly

    # Unique Character Properties
    hasSummon = True
    AHASpdBuffAmount = 0
    TotalElationChar = 0
    Fervor = 0
    Banger = 0
    BangerDuration = 3   # base 2 turns, +1 from his kit
    CharSpd = 0
    Tech = True
    FERVOR_THRESHOLD = 10
    FERVOR_CAP = 30
    FERVOR_CAP_E2 = 50
    @property
    def fervorCap(self) -> int:
        """E2: the upper limit of Fervor increases to 50."""
        return self.FERVOR_CAP_E2 if self.eidolon >= 2 else self.FERVOR_CAP
    FIXED_PUNCHLINE = 20
    AhaInTeam = False
    AhaEidolon = 0


    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT,
                 elationParticipationID=156) -> None:  # Aventurine Waveflair ID: 156
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else MushyShroomysAdventuresSparxie(role,5)
        self.relic1 = r1 if r1 else EverGloriousMagicalGirl(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else TengokuLivestream(role)
        self.relicStats = subs if subs else RelicStats(6, 2, 2, 2, 2, 8, 2, 2, 2, 2, 9, 9, StatTypes.CR_PERCENT, StatTypes.SPD, StatTypes.ATK_PERCENT, StatTypes.ERR_PERCENT)
        self.rotation = rotation if rotation else ["E"]
        self.elationParticipationID = elationParticipationID
        # Instance-level state
        self.elaUses = 0             # E6: number of Elation Skills used so far
        self.cheersTriggered = set() # Fervor thresholds (10, and with E1 also 20/30) that already triggered Cheers
        self.cheersActive = False    # a "Cheers! To Summer's Blaze" instance (fixed 20 Punchline) is in progress
        self.elaEnhanced = False     # next Elation Skill becomes "All In! To Summer's Blaze"
        self.soleElation = False     # Trace 2: he is the only Elation character in the team (set in equip)
        self.trace2Count = 0         # unique-name counter for the Certified Banger buffs of Trace 2
        self.trace3Count = 0         # Trace 3 triggers (max 6, resets when he uses his Skill)

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("BangerStartBattle", StatTypes.BANGER, 20, self.role, [AtkType.ALL], self.BangerDuration, 1, self.role, TickDown.END))
        bl.append(Buff("AventurineWaveflairTraceCR", StatTypes.CR_PERCENT, 0.187, self.role))
        bl.append(Buff("AventurineWaveflairTraceSPD", StatTypes.SPD, 9, self.role))
        bl.append(Buff("AventurineWaveflairTraceELA", StatTypes.ELA, 0.10, self.role))
        # Trace 3: +48% CRIT DMG
        bl.append(Buff("AventurineWaveflairTrace3CD", StatTypes.CD_PERCENT, 0.48, self.role))
        # Eidolon 6: Elation DMG dealt merrymakes by 25%
        if self.eidolon >= 6:
            bl.append(Buff("AventurineWaveflairE6Merry", StatTypes.MERRY, 0.25, self.role))
        # Eidolon 1: +24% All-Type RES PEN
        if self.eidolon >= 1:
            bl.append(Buff("AventurineWaveflairE1PEN", StatTypes.PEN, 0.24, self.role))
        # Trace 2 (checked once, at the start of the battle)
        otherElation = [c for c in (Character._current_player_team or [])
                        if c.path == Path.ELATION and c.name != self.name]
        self.soleElation = len(otherElation) == 0
        if not self.soleElation:
            bl.append(Buff("AventurineWaveflairTrace2ELA", StatTypes.ELA, 0.20, Role.ALL))
            bl.append(Buff("AventurineWaveflairTrace2ELASelf", StatTypes.ELA, 0.80, self.role))
        return bl, dbl, al, dl, hl, sl

    def _ascended(self) -> bool:
        """The Path of Elation ascends: Aeon Aha is in the team and her Ultimate is active."""
        return bool(self.AhaInTeam and Character.AeonAhaUltActive)

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useBsc(enemyID)
        e5Mul = 1.1 if self.eidolon >= 5 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC],
[self.element],[e5Mul, 0], [10, 0], 20, self.scaling, 1, "AventurineWaveflairBasic"))
        return bl, dbl, al, dl, tl, hl, sl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useSkl(enemyID)
        e3Mul = 2.64 if self.eidolon >= 3 else 2.4
        e3ELAMul = 0.44 if self.eidolon >= 3 else 0.40
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.SKL],
                       [self.element], [e3Mul, 0], [10, 0], 30, self.scaling, -1, "AventurineWaveflairSkill"))
        if self.Banger >= 1:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELABANGER],
                           [self.element], [e3ELAMul, 0], [0, 0], 0, Scaling.ELA, 0, "AventurineWaveflairSkillELA"))
        Character.SharedPunchline += 4
        if self.eidolon >= 4:
            bl.append(Buff("AventurineWaveFlairE4Shred", StatTypes.SHRED, 0.18, Role.ALL, [AtkType.ALL], 3, 1,
                           self.role, TickDown.END))
        self.Fervor = min(self.Fervor + 4, self.fervorCap)
        self.trace3Count = 0
        return bl, dbl, al, dl, tl, hl, sl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e5Mul = 4.32 if self.eidolon >= 5 else 4.00
        e5SPD = 0.336 if self.eidolon >= 5 else 0.300
        e3ELAMul = 0.792 if self.eidolon >= 3 else 0.72
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT],
                       [self.element], [e5Mul, 0], [20, 0], 5, self.scaling, 0, "AventurineWaveflairUlt"))
        if self.Banger >= 1:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELABANGER],
                           [self.element], [e3ELAMul, 0], [0, 0], 0, Scaling.ELA, 0, "AventurineWaveflairUltELA"))
        Character.SharedPunchline += 6
        self.Fervor = min(self.Fervor + 8, self.fervorCap)
        bl.append(Buff("AventurineWaveflairUltSPD", StatTypes.SPD_PERCENT, e5SPD, self.role, [AtkType.ALL], 4, 1, self.role,TickDown.START))
        return bl, dbl, al, dl, tl, hl, sl

    def _handleSequenceEnd(self, result: Result):
        bl = []
        if result.turnName in self.ELA_SEQUENCE_END and self.soleElation:
            bl.append(Buff("AventurineWaveflairTrace2AhaSPD", StatTypes.SPD, 0, Role.AHA, [AtkType.SPECIAL], 1, 1,
                           Role.AHA, TickDown.PERM))
        return bl

    ELA_SEQUENCE_END = ("AhaElationSequenceComplete", "AhaElationFixedSequenceComplete", "AhaElationFixedEMCSequenceComplete")

    def _handleCheersEnd(self, result: Result):
        if result.turnName == "AhaElationFixedEMCSequenceComplete" and self.cheersActive:
            self.cheersActive = False
            Character.EMCUlt = False

    def _checkFervor(self):
        bl, dbl, al, dl, tl, hl, sl = [], [], [], [], [], [], []
        self.cheersTriggered = {t for t in self.cheersTriggered if t <= self.Fervor}
        thresholds = (10, 20, 30, 40, 50) if self.eidolon >= 2 else ((10, 20, 30) if self.eidolon >= 1 else (10,))
        reached = [t for t in thresholds if self.Fervor >= t and t not in self.cheersTriggered]
        if reached and not self.cheersActive:
            self.cheersTriggered.add(reached[0])   # one at a time; a further threshold triggers on the next check
            self.cheersActive = True
            Character.ahaFixedPunchline = True
            Character.ahaFixedPunchlineValue = self.FIXED_PUNCHLINE
            Character.EMCUlt = True
            for name in ("AventurineWaveflairCheers", f"ElationMCUltTrigger_{self.role.name}", "AhaFixedEndGoGo"):
                tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                               self.scaling, 0, name))
        return bl, dbl, al, dl, tl, hl, sl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().ownTurn(turn, result)
        bl.extend(self._handleSequenceEnd(result))
        self._handleCheersEnd(result)
        if result.turnName == "AhaAventurineWaveflairGoGo":
            return self.useElaSkill(-1)
        if result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1, cheers=self.cheersActive)

        pearl = next((c for c in (Character._current_player_team or []) if c.name == "Pearl"), None)
        if result.turnName == "AventurineWaveflairSkillELA" and Character.PearlUlt == True and pearl is not None and self.role == pearl.targetRole:
            if self._ascended():
                AhaExtraBuffRetain = 0.2 if self.AhaEidolon >= 2 else 0.1
            else:
                AhaExtraBuffRetain = 0.0
            bl.append(Buff("PearlAestheticArchetypeBanger", StatTypes.BANGER, 30 * Character.PearlE2Modifier * AhaExtraBuffRetain, self.role,
                           [AtkType.ALL], 2, 1, self.role, TickDown.END))
            Character.SharedPunchline -= (60*(1-AhaExtraBuffRetain)) * Character.PearlE2Modifier
            Character.PearlUlt = False

        # Skill / Ult gave Fervor: check the threshold
        if result.turnName in ("AventurineWaveflairSkill", "AventurineWaveflairUlt"):
            bl, dbl, al, dl, tl, hl, sl = self.extendLists(bl, dbl, al, dl, tl, hl, sl, *self._checkFervor())

        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)
        bl.extend(self._handleSequenceEnd(result))
        self._handleCheersEnd(result)

        if result.turnName == "AhaAventurineWaveflairGoGo":
            return self.useElaSkill(-1)
        if result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1, cheers=self.cheersActive)

        pearl = next((c for c in (Character._current_player_team or []) if c.name == "Pearl"), None)
        if result.turnName == "PearlUltimate" and Character.PearlUlt == True and pearl is not None and self.role == pearl.targetRole:
            bl.append(Buff("PearlAestheticArchetypeBanger", StatTypes.BANGER, 30 * Character.PearlE2Modifier, self.role,
                           [AtkType.ALL], 2, 1, self.role, TickDown.PERM))
            Character.SharedPunchline += 60 * Character.PearlE2Modifier

            bl, dbl, al, dl, tl, hl, sl = self.extendLists(bl, dbl, al, dl, tl, hl, sl, *self.useSkl(-1))

        if (turn.moveName not in bonusDMG) and result.enemiesHit and result.turnDmg > 0:
            self.Fervor = min(self.Fervor + 1, self.fervorCap)
            Character.SharedPunchline += 1

            if self.soleElation:
                bl.append(Buff(f"AventurineWaveflairTrace2Banger{self.trace2Count}", StatTypes.BANGER, 2, self.role,
                               [AtkType.ALL], self.BangerDuration, 1, self.role, TickDown.END))
                self.trace2Count += 1
                Character.SharedPunchline += 1
                bl.append(Buff("AventurineWaveflairTrace2AhaSPD", StatTypes.SPD, 25, Role.AHA, [AtkType.SPECIAL], 1, 1,
                               Role.AHA, TickDown.PERM))

            if self.trace3Count < 6 and any(t in (AtkType.BSC, AtkType.SKL, AtkType.FUA, AtkType.ULT) for t in turn.atkType):
                self.trace3Count += 1
                bl.append(Buff("AventurineWaveflairTrace3AllyCD", StatTypes.CD_PERCENT, 0.48, Role.ALL, [AtkType.ALL], 3, 1,
                               self.role, TickDown.END))
                self.Fervor = min(self.Fervor + 2, self.fervorCap)
            bl, dbl, al, dl, tl, hl, sl = self.extendLists(bl, dbl, al, dl, tl, hl, sl, *self._checkFervor())

        return bl, dbl, al, dl, tl, hl, sl

    def _buildElaTurns(self, enemyID, tl, fervorConsumed=0):
        if self.eidolon >= 5:
            e5MulBig, e5MulSmall, e5MulEnhanced = 0.66, 0.198, 0.231
        elif self.eidolon >= 3:
            e5MulBig, e5MulSmall, e5MulEnhanced = 0.63, 0.189, 0.2205
        else:
            e5MulBig, e5MulSmall, e5MulEnhanced = 0.60, 0.18, 0.21

        elaType = [AtkType.ELAPUNCH, AtkType.FUA] if self.soleElation else [AtkType.ELAPUNCH]  # Trace 2

        if fervorConsumed == 0:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, elaType,
                           [self.element], [10*e5MulSmall * Character.ahaElaDMGBoost, 0], [10*3.33, 0], 0, Scaling.ELA, 0,
                           "AventurineWaveflairELASkillRandom"))
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, elaType,
                           [self.element], [e5MulBig * Character.ahaElaDMGBoost, 0], [10, 0], 0, Scaling.ELA, 0,
                           "AventurineWaveflairELASkill"))
        else:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, elaType,
                           [self.element], [(10*e5MulSmall+fervorConsumed*e5MulEnhanced) * Character.ahaElaDMGBoost, 0], [10*5, 0], 0, Scaling.ELA, 0,
                           "AventurineWaveflairELASkillRandom"))
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, elaType,
                           [self.element], [e5MulBig * Character.ahaElaDMGBoost, 0], [20, 0], 0, Scaling.ELA, 0,
                           "AventurineWaveflairELASkill"))

    def useAllInElaSkill(self, enemyID=-1, consume=True):
        """"All In! To Summer's Blaze": consumes all Fervor (+21% random-enemy instance per point consumed).
        E6: when used outside the Aha Instant (the Cheers instance) it no longer consumes Fervor."""
        bl, dbl, al, dl, tl, hl, sl = super().useElaSkill(enemyID)
        fervor = self.Fervor
        if consume:
            self.Fervor = 0
            self.cheersTriggered.clear()
        self._buildElaTurns(enemyID, tl, fervorConsumed=fervor)
        return bl, dbl, al, dl, tl, hl, sl

    def useElaSkill(self, enemyID=-1, cheers=False):
        allIn = (self.elaEnhanced and not cheers) or (self.eidolon >= 6 and self.elaUses >= 2)
        if self.elaEnhanced and not cheers:
            self.elaEnhanced = False
        self.elaUses += 1
        if allIn:
            res = self.useAllInElaSkill(enemyID, consume=not cheers)
        else:
            res = list(super().useElaSkill(enemyID))
            self._buildElaTurns(enemyID, res[4])
            if cheers:
                self.elaEnhanced = True
        if self.eidolon >= 2:
            self.Fervor = min(self.Fervor + 4, self.fervorCap)
        return tuple(res)

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)
        self.AHASpdBuffAmount = specialRes.attr1
        self.TotalElationChar = specialRes.attr2
        self.Banger = specialRes.attr3
        self.CharSpd = specialRes.attr4
        self.AhaInTeam = specialRes.attr5
        self.AhaEidolon = specialRes.attr6

        bl.append(Buff("AhaSpdBuff",StatTypes.SPD,self.AHASpdBuffAmount,Role.AHA,[AtkType.SPECIAL],1,1,Role.AHA,TickDown.PERM))
        if self.currSPD >= 140:
            ELABuff = min(max((self.CharSpd-140), 0), 200)
            bl.append(Buff("AventurineWaveflairTalentELABuff", StatTypes.ELA, 0.30+ELABuff*0.01, self.role, [AtkType.ALL], 1, 1, self.role, TickDown.PERM))
        if self.Tech:
            self.Tech = False
            bl.append(Buff("BangerAventurineWaveflairTech", StatTypes.BANGER, 20, self.role, [AtkType.ALL], self.BangerDuration, 1, self.role, TickDown.END))
            tl.append(Turn(self.name, self.role, -1, Targeting.AOE, [AtkType.TECH], [self.element], [1.0, 0], [0, 0], 0,self.scaling, 0, "AventurineWaveflairTech"))
            tl.append(Turn(self.name, self.role, -1, Targeting.SINGLE, [AtkType.TECH], [self.element], [0.0, 0], [20, 0], 0,self.scaling, 0, "AventurineWaveflairTech"))
            self.Fervor = min(self.Fervor + 2, self.fervorCap)

        return bl, dbl, al, dl, tl, hl, sl