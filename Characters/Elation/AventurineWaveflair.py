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
        self.cheersArmed = True      # Cheers triggers when Fervor reaches 10; re-arms once Fervor drops below 10
        self.cheersActive = False    # a "Cheers! To Summer's Blaze" instance (fixed 20 Punchline) is in progress
        self.elaEnhanced = False     # next Elation Skill becomes "All In! To Summer's Blaze"

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("BangerStartBattle", StatTypes.BANGER, 20, self.role, [AtkType.ALL], self.BangerDuration, 1, self.role, TickDown.END))
        bl.append(Buff("AventurineWaveflairTraceCR", StatTypes.CR_PERCENT, 0.187, self.role))
        bl.append(Buff("AventurineWaveflairTraceSPD", StatTypes.SPD, 9, self.role))
        bl.append(Buff("AventurineWaveflairTraceELA", StatTypes.ELA, 0.10, self.role))
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
        self.Fervor = min(self.Fervor + 4, self.FERVOR_CAP)
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
        self.Fervor = min(self.Fervor + 8, self.FERVOR_CAP)
        bl.append(Buff("AventurineWaveflairUltSPD", StatTypes.SPD_PERCENT, e5SPD, self.role, [AtkType.ALL], 4, 1, self.role,TickDown.START))
        return bl, dbl, al, dl, tl, hl, sl

    def _handleSequenceEnd(self, result: Result):
        # End of the fixed-20-Punchline instance started by Cheers (same marker the EMC Ult instance uses)
        if result.turnName == "AhaElationFixedEMCSequenceComplete" and self.cheersActive:
            self.cheersActive = False
            Character.EMCUlt = False

    def _checkFervor(self):
        bl, dbl, al, dl, tl, hl, sl = [], [], [], [], [], [], []
        if self.Fervor < self.FERVOR_THRESHOLD:
            self.cheersArmed = True
        if self.Fervor >= self.FERVOR_THRESHOLD and self.cheersArmed and not self.cheersActive:
            self.cheersArmed = False
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
        self._handleSequenceEnd(result)
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
        self._handleSequenceEnd(result)

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
            self.Fervor = min(self.Fervor + 1, self.FERVOR_CAP)
            Character.SharedPunchline += 1
            bl, dbl, al, dl, tl, hl, sl = self.extendLists(bl, dbl, al, dl, tl, hl, sl, *self._checkFervor())

        return bl, dbl, al, dl, tl, hl, sl

    def _buildElaTurns(self, enemyID, tl, fervorConsumed=0):
        if self.eidolon >= 5:
            e5MulBig, e5MulSmall, e5MulEnhanced = 0.66, 0.198, 0.231
        elif self.eidolon >= 3:
            e5MulBig, e5MulSmall, e5MulEnhanced = 0.63, 0.189, 0.2205
        else:
            e5MulBig, e5MulSmall, e5MulEnhanced = 0.60, 0.18, 0.21

        if fervorConsumed == 0:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ELAPUNCH],
                           [self.element], [10*e5MulSmall * Character.ahaElaDMGBoost, 0], [10*3.33, 0], 0, Scaling.ELA, 0,
                           "AventurineWaveflairELASkillRandom"))
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELAPUNCH],
                           [self.element], [e5MulBig * Character.ahaElaDMGBoost, 0], [10, 0], 0, Scaling.ELA, 0,
                           "AventurineWaveflairELASkill"))
        else:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ELAPUNCH],
                           [self.element], [(10*e5MulSmall+fervorConsumed*e5MulEnhanced) * Character.ahaElaDMGBoost, 0], [10*5, 0], 0, Scaling.ELA, 0,
                           "AventurineWaveflairELASkillRandom"))
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELAPUNCH],
                           [self.element], [e5MulBig * Character.ahaElaDMGBoost, 0], [20, 0], 0, Scaling.ELA, 0,
                           "AventurineWaveflairELASkill"))

    def useAllInElaSkill(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useElaSkill(enemyID)
        consumed = self.Fervor
        self.Fervor = 0
        self.cheersArmed = True
        self._buildElaTurns(enemyID, tl, fervorConsumed=consumed)
        return bl, dbl, al, dl, tl, hl, sl

    def useElaSkill(self, enemyID=-1, cheers=False):
        # Next Elation Skill in an Aha Instant after a Cheers use is enhanced
        if self.elaEnhanced and not cheers:
            self.elaEnhanced = False
            return self.useAllInElaSkill(enemyID)
        bl, dbl, al, dl, tl, hl, sl = super().useElaSkill(enemyID)
        self._buildElaTurns(enemyID, tl)
        if cheers:
            self.elaEnhanced = True
        return bl, dbl, al, dl, tl, hl, sl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)
        self.AHASpdBuffAmount = specialRes.attr1
        self.TotalElationChar = specialRes.attr2
        self.Banger = specialRes.attr3
        self.CharSpd = specialRes.attr4
        self.AhaInTeam = specialRes.attr5
        self.AhaEidolon = specialRes.attr6

        bl.append(Buff("AhaSpdBuff",StatTypes.SPD,self.AHASpdBuffAmount,Role.AHA,[AtkType.SPECIAL],1,1,Role.AHA,TickDown.PERM))
        if self.Tech:
            self.Tech = False
            bl.append(Buff("BangerAventurineWaveflairTech", StatTypes.BANGER, 20, self.role, [AtkType.ALL], self.BangerDuration, 1, self.role, TickDown.END))
            tl.append(Turn(self.name, self.role, -1, Targeting.AOE, [AtkType.TECH], [self.element], [1.0, 0], [0, 0], 0,self.scaling, 0, "AventurineWaveflairTech"))
            tl.append(Turn(self.name, self.role, -1, Targeting.SINGLE, [AtkType.TECH], [self.element], [0.0, 0], [20, 0], 0,self.scaling, 0, "AventurineWaveflairTech"))
            self.Fervor = min(self.Fervor + 2, self.FERVOR_CAP)

        return bl, dbl, al, dl, tl, hl, sl