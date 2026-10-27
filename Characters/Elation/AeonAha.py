import logging

from Buff import *
from Character import Character
from Lightcones.Elation.UponTheFirstEchoOfAha import UponTheFirstEchoOfAha
from Lightcones.Elation.MushyShroomyAdventures import MushyShroomysAdventuresAeonAHa
from Planars.GodsMomentOfJoy import GodsMomentOfJoy
from RelicStats import RelicStats
from Relics.DreamlitActor import DreamlitActor
from Result import *
from Turn_Text import Turn
from Healing import *
from Delay_Text import Advance
from random import random
from math import floor

logger = logging.getLogger(__name__)


class AeonAha(Character):
    # Standard Character Settings
    name = "AeonAha"
    path = Path.ELATION
    element = Element.QUANTUM
    scaling = Scaling.ELA
    baseHP = 1048
    baseATK = 679
    baseDEF = 509
    baseSPD = 94
    maxEnergy = 10
    currEnergy = 0
    ultCost = 8
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.ELAPUNCH: 0, AtkType.ELABANGER: 0}  # Adjust accordingly

    # Unique Character Properties
    hasSummon = True
    specialEnergy = True
    AHASpdBuffAmount = 0
    TotalElationChar = 0
    Wishpower = 0
    UltActive = False
    UltTurns = 0
    TalentWishpowerTrigger = True
    DPSName = "AeonAha"
    SpdStat = 0
    DPSElement = Element.QUANTUM
    BangerStat = 0
    ELAStat = 0
    EvaInTeam = False
    FirstUlt = True
    Tech = True

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, targetRole=Role.DPS, rotation=None, targetPrio=Priority.DEFAULT,
                 elationParticipationID=0) -> None:  # AeonAha ID: 0
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else MushyShroomysAdventuresAeonAHa (role,5)
        self.relic1 = r1 if r1 else DreamlitActor(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else GodsMomentOfJoy(role)
        self.relicStats = subs if subs else RelicStats(11, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7, 8, StatTypes.CR_PERCENT, StatTypes.SPD, StatTypes.HP_PERCENT, StatTypes.DEF_PERCENT)
        self.targetRole = targetRole
        self.rotation = rotation if rotation else ["E"]
        self.elationParticipationID = elationParticipationID
        # Aha Instant tracking (instance-level on purpose: class-level state leaks across runs/teams)
        self.instantActive = False
        self.instantNonTrueDMG = 0.0
        self.emcAscendDMG = 0.0
        self.emcAscendPending = False
        self.trueFromEMCAscend = False
        self.ahaSummon = None  # set in addSummons (MainFunctions.py)
        # Talent: Wishpower from teammate healing/shields (max once, re-arms on Ultimate)
        self.healShieldWishpowerUsed = False
        self._lastShieldHP = 0.0
        self._lastShieldCount = 0

    def _gainWishpowerFromSupport(self, source: str):
        """'When receiving healing or a Shield provided by a teammate, gains 1 point of Wishpower.
        This can be triggered up to 1 times. The trigger count resets after using Ultimate.'"""
        if self.healShieldWishpowerUsed:
            return
        self.healShieldWishpowerUsed = True
        self.currEnergy += 1
        logger.info(f"WISHPOWER > {self.name} gained 1 Wishpower from receiving {source} "
                    f"(total: {self.currEnergy})")

    def ChangeHpValue(self, HPChangingValue: float):
        super().ChangeHpValue(HPChangingValue)
        # Aha has no self-healing, so any positive HP change is healing from a teammate
        if HPChangingValue > 0:
            self._gainWishpowerFromSupport("healing")

    def _checkShieldReceived(self):
        """Shields are attached to her after the providing teammate's turn resolves, so compare
        against the last snapshot (any new/larger shield means one was provided to her)."""
        hp = self.getTotalShieldHP()
        count = len(self.shields)
        if hp > self._lastShieldHP + 1e-9 or count > self._lastShieldCount:
            self._gainWishpowerFromSupport("a Shield")
        self._lastShieldHP, self._lastShieldCount = hp, count

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("BangerStartBattle", StatTypes.BANGER, 20, self.role, [AtkType.ALL], 2, 1, self.role, TickDown.END))
        bl.append(Buff("AeonAhaTraceCR", StatTypes.CR_PERCENT, 0.12, self.role))
        bl.append(Buff("AeonAhaTraceSPD", StatTypes.SPD, 5, self.role))
        bl.append(Buff("AeonAhaTraceCD", StatTypes.ELA, 0.373, self.role))
        al.append(Advance("Trace3ADV", self.role, 0.30))
        if self.eidolon >= 1:
            self.currEnergy += 5
            bl.append(Buff("E1AhaMerry", StatTypes.MERRY, 0.15, Role.ALL, [AtkType.ALL], 1, 1, self.role, TickDown.PERM))
        return bl, dbl, al, dl, hl, sl

    def canUseUlt(self) -> bool:
        """Only use the Ultimate while the Aha summon still has more than 20% of its AV left, so the
        20% Advance it grants is not wasted."""
        if not super().canUseUlt():
            return False
        if not self.EvaInTeam:
            return True
        summon = self.ahaSummon
        if summon is None or summon.currSPD <= 0:
           return True
        fullAV = 10000 / summon.currSPD
        return summon.currAV > 0.20 * fullAV

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useBsc(enemyID)
        e3Mul = 0.55 if self.eidolon >= 3 else 0.50
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC,AtkType.ELABANGER],
[self.element],[e3Mul, 0], [10, 0], 0, self.scaling, 1, "AeonAhaBasic"))
        self.currEnergy += 1
        return bl, dbl, al, dl, tl, hl, sl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useSkl(enemyID)
        e5Mul = 0.55 if self.eidolon >= 5 else 0.50
        e5ELABuff = 0.22 if self.eidolon >= 5 else 0.20
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.FUA, AtkType.ELABANGER],
                 [self.element], [e5Mul, 0], [10, 0], 0, self.scaling, -1, "AeonAhaSkill"))
        tl.append(Turn(self.DPSName, self.targetRole, self.bestEnemy(enemyID),
                       Targeting.AOE, [AtkType.ELABANGER, AtkType.FUA], [self.DPSElement],
                       [0.20, 0], [0, 0], 0, Scaling.ELA, 0, "AhaDPSSkill"))
        bl.append(Buff("AhaSkillELA", StatTypes.ELA, e5ELABuff, self.targetRole, [AtkType.ALL], 1, 1, self.targetRole, TickDown.PERM))
        self.currEnergy += 1
        bl.append(Buff("Trace1SPRefund", StatTypes.SKLPT, 1, self.targetRole, [AtkType.ALL], 1, 1, self.targetRole, TickDown.START))
        return bl, dbl, al, dl, tl, hl, sl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        self.healShieldWishpowerUsed = False
        e3MulBig = 2.16 if self.eidolon >= 3 else 2.00
        e3MulSmall = 0.648 if self.eidolon >= 3 else 0.60
        if self.FirstUlt and self.eidolon == 6:
            al.append(Advance("AhaADV", Role.AHA, 1.00))
            Character.SharedPunchline += 100
        else:
            al.append(Advance("AhaADV", Role.AHA, 0.20))
        self.UltActive = True
        self.UltTurns = 3
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT, AtkType.ELABANGER],
                 [self.element], [e3MulBig, 0], [20, 0], 0, self.scaling, 0, "AeonAhaUlt"))
        for _ in range(5):
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ULT, AtkType.ELABANGER],
                     [self.element], [e3MulSmall, 0], [5, 0], 0, self.scaling, 0, "AeonAhaUltExtra"))
        return bl, dbl, al, dl, tl, hl, sl

    ELA_SEQUENCE_END = ("AhaElationSequenceComplete", "AhaElationFixedSequenceComplete", "AhaElationFixedEMCSequenceComplete")
    GREAT_BOON_MOVES = ("YaoGuangTalentADD", "YaoGuangTalentADDSP")
    EMC_ASCEND_MOVES = ("ElationMCUltAscendBig", "ElationMCUltAscendSmall")

    def _trackInstant(self, turn: Turn, result: Result):
        """Tracks the non-True DMG dealt during the current Aha Instant: all ELAPUNCH damage from
        Elation skills and Yao Guang's Great Boon procs (Aha's own DMG is excluded). Tracking
        starts when an Elation skill is triggered (GoGo / Ult-trigger marker) and the pool is
        cleared when the Aha turn ends."""
        name = result.turnName
        if name in self.EMC_ASCEND_MOVES:
            # Trailblazer's ascended Elation Skill resolves BEFORE Aha's skill is triggered; when it
            # does, the True DMG is based on this DMG alone.
            self.emcAscendPending = True
            self.emcAscendDMG += result.ElationturnDMG
        elif (name.startswith("Aha") and name.endswith("GoGo")) or name.startswith("ElationMCUltTrigger_"):
            if not self.instantActive:
                self.instantActive = True
                self.instantNonTrueDMG = self.emcAscendDMG if self.emcAscendPending else 0.0
                self.trueFromEMCAscend = self.emcAscendPending
                self.emcAscendDMG = 0.0
                self.emcAscendPending = False
        elif name in self.ELA_SEQUENCE_END:
            self.instantActive = False
            self.instantNonTrueDMG = 0.0
            self.trueFromEMCAscend = False
        elif self.instantActive and not self.trueFromEMCAscend and (AtkType.ELAPUNCH in turn.atkType or name in self.GREAT_BOON_MOVES):
            self.instantNonTrueDMG += result.ElationturnDMG

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().ownTurn(turn, result)
        self._checkShieldReceived()
        self._trackInstant(turn, result)
        e5CDBuff = 0.44 if self.eidolon >= 5 else 0.40
        if result.turnName == "AhaGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        pearl = next((c for c in (Character._current_player_team or []) if c.name == "Pearl"), None)
        if result.turnName == "AeonAhaSkill" and Character.PearlUlt == True and pearl is not None and self.role == pearl.targetRole:
            if self.UltActive:
                AhaExtraBuffRetain = 0.2 if self.eidolon >= 2 else 0.1
            else:
                AhaExtraBuffRetain = 0.0
            bl.append(Buff("PearlAestheticArchetypeBanger", StatTypes.BANGER, 30 * Character.PearlE2Modifier * AhaExtraBuffRetain, self.role,
                           [AtkType.ALL], 2, 1, self.role, TickDown.END))
            Character.SharedPunchline -= (60*(1-AhaExtraBuffRetain)) * Character.PearlE2Modifier
            Character.PearlUlt = False

        if Character.SharedPunchline >= 40 and self.TalentWishpowerTrigger:
            self.currEnergy += 1
            self.TalentWishpowerTrigger = False
            logger.info(f"WISHPOWER > {self.name} gained 1 Wishpower from reaching 40 Punchline")
            bl.append(Buff("AhaTalentCD", StatTypes.CD_PERCENT, e5CDBuff, Role.ALL, [AtkType.ALL], 3, 1, self.role, TickDown.END))

        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)
        self._checkShieldReceived()
        self._trackInstant(turn, result)
        e5CDBuff = 0.44 if self.eidolon >= 5 else 0.40

        if result.turnName == "AhaGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        pearl = next((c for c in (Character._current_player_team or []) if c.name == "Pearl"), None)
        if result.turnName == "PearlUltimate" and Character.PearlUlt == True and pearl is not None and self.role == pearl.targetRole:
            bl.append(Buff("PearlAestheticArchetypeBanger", StatTypes.BANGER, 30 * Character.PearlE2Modifier, self.role,
                           [AtkType.ALL], 2, 1, self.role, TickDown.PERM))
            Character.SharedPunchline += 60 * Character.PearlE2Modifier

            bl, dbl, al, dl, tl, hl, sl = self.extendLists(bl, dbl, al, dl, tl, hl, sl, *self.useSkl(-1))

        if turn.moveName == "AhaElationSequenceComplete":
            self.TalentWishpowerTrigger = True

        if Character.SharedPunchline >= 40 and self.TalentWishpowerTrigger and Character.PearlUlt == False:
            self.currEnergy += 1
            self.TalentWishpowerTrigger = False
            logger.info(f"WISHPOWER > {self.name} gained 1 Wishpower from reaching 40 Punchline")
            bl.append(Buff("AhaTalentCD", StatTypes.CD_PERCENT, e5CDBuff, Role.ALL, [AtkType.ALL], 3, 1, self.role, TickDown.END))
        return bl, dbl, al, dl, tl, hl, sl

    def _onTargetTurnBegins_Wishpower(self):
        self.currEnergy += 1
        logger.info(f"WISHPOWER > {self.name} gained 1 Wishpower from {self.targetRole.name}'s turn beginning "
                   f"(total: {self.Wishpower})")

    def useElaSkill(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useElaSkill(enemyID)
        if self.eidolon >= 5:
            e5Mul = 0.66
        elif 5 > self.eidolon >= 3:
            e5Mul = 0.63
        else:
            e5Mul = 0.60
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELABANGER],
                       [self.element], [e5Mul*Character.ahaElaDMGBoost, 0], [10, 0], 0, self.scaling, 0, "AeonAhaELASkill"))
        # Then True DMG = 20% of the non-True DMG allies dealt this Instant, split equally over all
        # enemies. The pool is read when this Turn resolves (see handleTurn in MainFunctions.py).
        trueMul = 0.20 * 1.25 if self.eidolon >= 4 else 0.20
        tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ALL],
                       [self.element], [trueMul, 0], [0, 0], 0, self.scaling, 0, "AeonAhaELATrueDMG"))
        self.currEnergy += 1
        return bl, dbl, al, dl, tl, hl, sl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)
        self._checkShieldReceived()
        self.AHASpdBuffAmount = specialRes.attr1
        self.TotalElationChar = specialRes.attr2
        self.DPSName = specialRes.attr3
        self.SpdStat = specialRes.attr4
        self.DPSElement = specialRes.attr5
        self.BangerStat = specialRes.attr6
        self.ELAStat = specialRes.attr7
        self.EvaInTeam = specialRes.attr8

        e5CDBuff = 0.44 if self.eidolon >= 5 else 0.40

        bl.append(Buff("AhaSpdBuff",StatTypes.SPD,self.AHASpdBuffAmount,Role.AHA,[AtkType.SPECIAL],1,1,Role.AHA,TickDown.PERM))
        if self.Tech:
            self.Tech = False
            Character.savedPunchline = Character.SharedPunchline
            Character.ahaYaoGuangUlt = True
            Character.SharedPunchline = 20
            Character.ahaFixedPunchlineValue = 20
            Character.ahaFixedPunchline = True
            tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.TECH], [self.element], [0, 0], [0, 0], 0,
                           self.scaling,0, "AeonAhaTech"))

        if Character.SharedPunchline >= 40 and self.TalentWishpowerTrigger:
            self.currEnergy += 1
            self.TalentWishpowerTrigger = False
            logger.info(f"WISHPOWER > {self.name} gained 1 Wishpower from reaching 40 Punchline")
            bl.append(Buff("AhaTalentCD", StatTypes.CD_PERCENT, e5CDBuff, Role.ALL, [AtkType.ALL], 3, 1, self.role, TickDown.END))

        if self.UltActive:
            if self.eidolon >= 2:
                bl.append(Buff("AhaEnhancedCR", StatTypes.CR_PERCENT, 0.20, self.role, [AtkType.ALL], 1, 1, self.role,
                               TickDown.PERM))
                bl.append(Buff("AhaEnhancedShred", StatTypes.SHRED, 0.60, self.role, [AtkType.ALL], 1, 1, self.role,
                               TickDown.PERM))
            else:
                bl.append(Buff("AhaEnhancedCR", StatTypes.CR_PERCENT, 0.12, self.role, [AtkType.ALL], 1, 1, self.role,
                               TickDown.PERM))
                bl.append(Buff("AhaEnhancedShred", StatTypes.SHRED, 0.30, self.role, [AtkType.ALL], 1, 1, self.role,
                               TickDown.PERM))
        else:
            bl.append(Buff("AhaEnhancedCR", StatTypes.CR_PERCENT, 0, self.role, [AtkType.ALL], 1, 1, self.role,
                           TickDown.PERM))
            bl.append(Buff("AhaEnhancedShred", StatTypes.SHRED, 0, self.role, [AtkType.ALL], 1, 1, self.role,
                           TickDown.PERM))
        if self.SpdStat >= 150:
            bl.append(Buff("AhaTrace3ELA", StatTypes.ELA, 1.50, self.role, [AtkType.ALL], 1, 1, self.role, TickDown.PERM))
        elif self.SpdStat >= 125:
            bl.append(Buff("AhaTrace3ELA", StatTypes.ELA, 1.20, self.role, [AtkType.ALL], 1, 1, self.role, TickDown.PERM))

        return bl, dbl, al, dl, tl, hl, sl

    def takeTurn(self) -> str:
        self._checkShieldReceived()
        if self.UltActive:
            self.UltTurns -= 1
        if self.UltTurns == 0:
            self.UltActive = False
        return super().takeTurn()