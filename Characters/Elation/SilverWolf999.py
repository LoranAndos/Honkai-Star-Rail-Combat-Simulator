import logging

from Buff import *
from Delay_Text import Advance
from Character import Character
from Lightcones.Elation.TodaysGoodLuck import TodaysGoodLuck
from Lightcones.Elation.TomorrowTogether import TomorrowTogether
from Lightcones.Elation.WelcomeToTheCosmicCity import WelcometotheCosmicCity
from Lightcones.Elation.MushyShroomyAdventures import MushyShroomysAdventuresSilverWolf999
from Planars.IzumoGenseiAndTakamaDivineRealm import IzumoGenseiAndTakamaDivineRealm
from Planars.PunklordeStageZero import PunklordeStageZero
from RelicStats import RelicStats
from Relics.EverGloriousMagicalGirl import EverGloriousMagicalGirl
from Relics.GeniusOfBrilliantStars import GeniusOfBrilliantStars
from Result import *
from Turn_Text import Turn
from Healing import *
from random import randrange, random, randint
from math import floor

logger = logging.getLogger(__name__)


class SilverWolf999(Character):
    # Standard Character Settings
    name = "SilverWolf999"
    path = Path.ELATION
    element = Element.IMAGINARY
    scaling = Scaling.ATK
    baseHP = 1048
    baseATK = 388
    baseDEF = 655
    baseSPD = 110
    maxEnergy = 300
    currEnergy = 0
    ultCost = 60
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.BRK: 0, AtkType.ELAPUNCH: 0, AtkType.ELABANGER: 0}

    # Unique Character Properties
    hasSummon = True
    specialEnergy = True
    AHASpdBuffAmount = 0
    TotalElationChar = 0
    ElaStat = 0
    Punch = 0
    SpdStat = 0
    Banger = 0
    CR = 0
    tech = True

    # SilverWolf999 Specific Properties
    hiddenMMR = 0  # Talent: tracks Hidden MMR points
    hiddenMMR_MAX = 300  # Can overflow by 240, base 60 = 300 total
    godmodeActive = False  # State for Godmode Player
    godmodeBasicCount = 0  # Count Enhanced Basic ATK uses
    godmodeBasicUsesRemaining = 3  # E2: Extra uses from Hidden MMR breakpoints
    lastMMRThreshold = 0  # E2: Track last processed MMR threshold
    GuaranteedLootBoxChance = False  # Guaranteed chance from enhanced basic
    topLootBoxChance = 1.0  # Initial 100%, reduces to 20% after each trigger
    topLootBoxTriggersRemaining = 3  # 3 triggers per Ultimate
    EnhancedBasicLootBox = False  # Checks if a Loot box is from enhanced basic
    WolfInstants = 0  # Legacy property
    lastPunchlineValue = 0  # Track Punchline changes for Hidden MMR sync
    techniqueTriggered = False  # Track if technique was triggered this wave
    lastMmrCrContribution = 0 # Keep track of MMR CR contribution for Hidden MMR buff

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, targetRole=Role.DPS, rotation=None, targetPrio=Priority.DEFAULT,
                 elationParticipationID=999) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else WelcometotheCosmicCity(role, 1)
        self.relic1 = r1 if r1 else EverGloriousMagicalGirl(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else PunklordeStageZero(role)
        self.relicStats = subs if subs else RelicStats(10, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 10, StatTypes.CR_PERCENT,
                                                       StatTypes.SPD, StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT)
        self.targetRole = targetRole
        self.rotation = rotation if rotation else ["E"]
        self.elationParticipationID = elationParticipationID
        self.hiddenMMR = 0
        self.currEnergy = 0
        self.lastPunchlineValue = Character.SharedPunchline
        self.godmodeActive = False
        self.godmodeBasicCount = 0
        self.godmodeBasicUsesRemaining = 3
        self.lastMMRThreshold = 0
        self.topLootBoxChance = 1.0
        self.topLootBoxTriggersRemaining = 3
        self.techniqueTriggered = False
        self.e2ExtendPending = False

    def _updateEnergyFromMMR(self):
        """Constantly sync currEnergy to match hiddenMMR value."""
        self.currEnergy = self.hiddenMMR
        logger.debug(f"{self.name} currEnergy synced to hiddenMMR: {self.currEnergy}")

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("BangerStartBattle", StatTypes.BANGER, 20, self.role, [AtkType.ALL], 2, 1, self.role, TickDown.END))
        bl.append(Buff("SilverWolf999TraceCR", StatTypes.CR_PERCENT, 0.187, self.role))
        bl.append(Buff("SilwerWolf999TraceSPD", StatTypes.SPD, 9, self.role))
        bl.append(Buff("SilverWolf999TraceELA", StatTypes.ELA, 0.10, self.role))
        return bl, dbl, al, dl, hl

    # =========================================================================
    # TALENT: Hidden MMR → CRIT Rate/CRIT DMG conversion + Punchline sync
    # =========================================================================

    def _syncPunchlineToHiddenMMR(self):
        """Sync Punchline changes to Hidden MMR."""
        punchline_diff = Character.SharedPunchline - self.lastPunchlineValue
        if punchline_diff > 0 and Character.ahaYaoGuangUlt == False and Character.EMCUlt == False:
            self.hiddenMMR = min(self.hiddenMMR + punchline_diff, self.hiddenMMR_MAX)
            logger.debug(f"{self.name} +{punchline_diff} Hidden MMR from Punchline (total: {self.hiddenMMR})")
        self.lastPunchlineValue = Character.SharedPunchline
        self._updateEnergyFromMMR()

    def _applyHiddenMMRBuff(self, bl: list):
        """Apply Hidden MMR buffs: 0.3% CRIT Rate per point, then 0.6% CRIT DMG after 100% CR."""
        self._syncPunchlineToHiddenMMR()

        if self.hiddenMMR <= 0:
            return

        # Step 1: How much CR headroom is left (accounting for all external buffs)
        non_mmr_cr = self.CR - self.lastMmrCrContribution
        cr_headroom = max(1.0 - non_mmr_cr, 0)
        cr_from_mmr = min(self.hiddenMMR * 0.004, cr_headroom)

        # Step 2: CD overflow = EXACTLY the MMR that didn't go to CR
        # (never use a separate threshold formula here — they will always drift apart)
        mmr_for_cr = cr_from_mmr / 0.004
        overflow_mmr = self.hiddenMMR - mmr_for_cr  # ← key fix
        cd_from_overflow = overflow_mmr * 0.008

        self.lastMmrCrContribution = cr_from_mmr

        if cr_from_mmr > 0:
            bl.append(Buff("SilverWolf999HiddenMMRCR", StatTypes.CR_PERCENT, cr_from_mmr, self.role,
                           [AtkType.ALL], 1, 1, self.role, TickDown.END))

        # After 100% CR, overflow MMR becomes CRIT DMG: 0.6% per point
        overflow_mmr = max(self.hiddenMMR - ((100 - self.CR * 100) / 0.4), 0)
        if overflow_mmr > 0:
            cd_from_mmr = overflow_mmr * 0.008
            bl.append(Buff("SilverWolf999HiddenMMRCD", StatTypes.CD_PERCENT, cd_from_overflow, self.role,
                           [AtkType.ALL], 1, 1, self.role, TickDown.END))

    def _enterGodmode(self, bl: list, al: list) -> bool:
        """Enter Godmode Player state. Returns True if entered."""
        if self.hiddenMMR >= 60 and not self.godmodeActive:
            self.godmodeActive = True
            self.godmodeBasicCount = 0
            self.godmodeBasicUsesRemaining = 3
            self.lastMMRThreshold = 0
            self.topLootBoxChance = 1.0
            self.topLootBoxTriggersRemaining = 3
            self.hiddenMMR -= 20 if self.lightcone.name == "Welcome to the Cosmic City" else 40

            al.append(Advance("SilverWolf999GodmodeAdvance", self.role, 1.0))  # 100% advance

            # E2: Extend all buffs by 1 turn on entering Godmode
            if self.eidolon >= 2:
                self.e2ExtendPending = True
                logger.debug(f"{self.name} E2: Buff extension pending on Godmode entry")

            self._updateEnergyFromMMR()
            logger.info(f"{self.name} entered Godmode Player state (Hidden MMR: {self.hiddenMMR})")
            return True
        return False

    def _exitGodmode(self):
        """Exit Godmode Player state. E1: Retain 20% of Hidden MMR."""
        if self.godmodeActive:
            self.godmodeActive = False
            self.godmodeBasicCount = 0

            # E1: Retain 20% of Hidden MMR on exit
            if self.eidolon >= 1:
                retained_mmr = int(self.hiddenMMR * 0.2)
                self.hiddenMMR = retained_mmr
                logger.info(f"{self.name} E1: Retained 20% Hidden MMR ({retained_mmr}) on Godmode exit")
            else:
                self.hiddenMMR = 0

            self._updateEnergyFromMMR()

            logger.info(f"{self.name} exited Godmode Player state")

    def applyGodmodeBuffExtension(self, teamBuffs: list) -> list:
        """E2: On entering Godmode, extend all buffs on this unit by 1 turn.
        Called from handleUlts AFTER handleAdditions so the live buff list is accessible."""
        if self.eidolon < 2 or not self.e2ExtendPending:
            return teamBuffs
        self.e2ExtendPending = False
        extended = []
        for buff in teamBuffs:
            if buff.target == self.role:
                buff.turns += 1
                extended.append(buff.name)
        if extended:
            logger.info(f"{self.name} E2: Extended {len(extended)} buff(s) by 1 turn: {extended}")
        return teamBuffs

    def _checkAndExecuteE2ExtraBasic(self, enemyID: int, bl: list, al: list, dbl: list) -> list:
        """E2: Constantly check if MMR threshold crossed (120, 240). If so, immediately execute extra Enhanced Basic (no AV advance).
        This is called after ANY action that might change Hidden MMR."""
        tl = []

        if self.eidolon < 2 or not self.godmodeActive:
            return tl

        current_threshold = floor(self.hiddenMMR / 120) * 120

        # Check if new threshold reached
        if current_threshold > self.lastMMRThreshold:
            self.lastMMRThreshold = current_threshold
            logger.info(
                f"{self.name} E2: Hidden MMR crossed {current_threshold} threshold! Executing extra Enhanced Basic (no AV advance)")

            # Execute Enhanced Basic immediately without incrementing count initially
            enhanced_basic_turns = self._useEnhancedBasic(enemyID, bl, al, dbl, skip_exit_check=True)
            tl.extend(enhanced_basic_turns)

        return tl

    # =========================================================================
    # CORE ACTIONS
    # =========================================================================

    def useBsc(self, enemyID=-1):
        """Basic ATK - enhanced when in Godmode."""
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)

        if self.godmodeActive:
            # Enhanced Basic ATK in Godmode
            enhanced_turns = self._useEnhancedBasic(enemyID, bl, al, dbl)
            tl.extend(enhanced_turns)
        else:
            # Normal Basic ATK
            e3Mul = 1.1 if self.eidolon >= 3 else 1.0
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC],
                           [self.element], [e3Mul, 0], [10, 0], 0, self.scaling, 1, "SilverWolf999Basic"))
            if self.Banger >= 1:
                e5Mul = 0.44 if self.eidolon >= 5 else 0.40
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ELABANGER],
                               [self.element], [e5Mul, 0], [0, 0], 0, Scaling.ELA, 0, "SilverWolf999Talent"))
        extra_basic_turns = self._checkAndExecuteE2ExtraBasic(self.bestEnemy(-1), bl, al, dbl)
        tl.extend(extra_basic_turns)
        self._updateEnergyFromMMR()
        self._applyHiddenMMRBuff(bl)
        self._syncPunchlineToHiddenMMR()
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        """Skill ATK - applies Banger dependent Imaginary Elation DMG."""
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e3Mul = 1.76 if self.eidolon >= 3 else 1.6

        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.SKL],
                       [self.element], [e3Mul, 0], [10, 0], 0, self.scaling, -1, "SilverWolf999Skill"))

        Character.SharedPunchline += 5
        self._syncPunchlineToHiddenMMR()

        if self.Banger >= 1:
            e5Mul = 0.44 if self.eidolon >= 5 else 0.40
            tl.append(
                Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELABANGER], [self.element],
                     [e5Mul, 0], [0, 0], 0, Scaling.ELA, 0, "SilverWolf999Talent"))

        # E2: Check for MMR threshold and grant extra Enhanced Basic if needed (no AV advance)
        extra_basic_turns = self._checkAndExecuteE2ExtraBasic(enemyID, bl, al, dbl)
        tl.extend(extra_basic_turns)
        extra_basic_turns = self._checkAndExecuteE2ExtraBasic(self.bestEnemy(-1), bl, al, dbl)
        tl.extend(extra_basic_turns)
        self._updateEnergyFromMMR()
        self._applyHiddenMMRBuff(bl)
        self._syncPunchlineToHiddenMMR()
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        """Ultimate: Enters Godmode and creates Zone."""
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)

        # Enter Godmode
        self._enterGodmode(bl, al)

        # Create Zone (logical marker for Top Loot Box triggers)
        bl.append(Buff("SilverWolf999Zone", StatTypes.BANGER, 0, self.role, [AtkType.ALL], 999, 1,
                       self.role, TickDown.START))

        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.NA, [AtkType.ALL], [self.element],
                 [0, 0], [0, 0], 0, self.scaling, 0, "SilverWolf999Ult"))

        if self.eidolon >= 1:
            bl.append(Buff("SilverWolf999ZoneVul", StatTypes.VULN, 0.20, Role.ALL   , [AtkType.ALL], 3, 1,self.role, TickDown.END))
        extra_basic_turns = self._checkAndExecuteE2ExtraBasic(self.bestEnemy(-1), bl, al, dbl)
        tl.extend(extra_basic_turns)
        self._updateEnergyFromMMR()
        self._applyHiddenMMRBuff(bl)
        self._syncPunchlineToHiddenMMR()
        logger.info(f"{self.name} used Ultimate: entered Godmode (Hidden MMR: {self.hiddenMMR})")

        return bl, dbl, al, dl, tl, hl

    def _useEnhancedBasic(self, enemyID: int, bl: list, al: list, dbl: list, skip_exit_check: bool = False) -> list:
        """Enhanced Basic ATK: 100 bounces with 3 Top Loot Box triggers. E1: Enemies take +20% DMG.
        skip_exit_check: If True, don't check for Godmode exit (used for E2 threshold bonus uses)."""
        tl = []
        base_mul = 2.64 / 100 if self.eidolon >= 3 else 2.40 / 100  # 220% split among 100 bounces
        e3Mul = 1.1 if self.eidolon >= 3 else 1
        e6Mul = 1.5 if self.eidolon >= 6 else 1.0
        enemyCount = self._getEnemyCount()

        # DMG boost from Hidden MMR: +15% per 60 points (stackable up to 2x = +30%)
        mmr_boost_multiplier = 1.0 + (floor(min(self.hiddenMMR, 120) / 60) * 0.15)
        base_mul_boosted = base_mul * mmr_boost_multiplier * e6Mul

        # Each bounce
        bounce_count = 100
        bounces_per_lootbox = bounce_count // 3  # ~33 bounces between triggers

        for i in range(bounce_count):
            tl.append(Turn(self.name, self.role, -1, Targeting.SINGLE, [AtkType.ELABANGER],
                           [self.element], [base_mul_boosted, 0], [10/100, 0], 0, Scaling.ELA, 0,
                           f"SilverWolf999EnhancedBounce_{i + 1}"))

            # Pause for Top Loot Box trigger every ~33 bounces
            if (i + 1) % bounces_per_lootbox == 0:
                self.EnhancedBasicLootBox = True
                self._triggerTopLootBox(enemyID, tl, bl,is_sp_triggered=False)

        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELABANGER],
                       [self.element], [e3Mul * e6Mul / enemyCount, 0], [10, 0], 0, Scaling.ELA, 0, "SilverWolf999EnhancedFinal"))

        if self.Banger >= 1:
            e5Mul = 0.44 if self.eidolon >= 5 else 0.40
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELABANGER], [self.element],
                     [e5Mul, 0], [0, 0], 0, Scaling.ELA, 0, "SilverWolf999Talent"))

        # Increment basic count
        self.godmodeBasicCount += 1

        # Check Godmode exit only if not skipped (skip_exit_check = True means this is a bonus Enhanced Basic from E2)
        if not skip_exit_check and self.godmodeBasicCount >= self.godmodeBasicUsesRemaining:
            self._exitGodmode()

        self._updateEnergyFromMMR()
        self._applyHiddenMMRBuff(bl)
        self._syncPunchlineToHiddenMMR()
        return tl

    def _triggerTopLootBox(self, enemyID: int, tl: list, bl: list, is_sp_triggered: bool = False):
        """Top Loot Box: 90% Imaginary Elation DMG + random effect.
        is_sp_triggered: True for SP-triggered (uses probability), False for Enhanced Basic (always triggers)"""

        # Only apply probability check for SP-triggered loot boxes
        if is_sp_triggered and random() > self.topLootBoxChance:
            logger.debug(f"{self.name} Top Loot Box trigger failed (chance was {self.topLootBoxChance / 0.2:.0%})")
            return

        self.GuaranteedLootBoxChance = False
        self.topLootBoxTriggersRemaining -= 1

        # Only reduce chance for SP-triggered loot boxes
        if is_sp_triggered:
            self.topLootBoxChance *= 0.2

        e5Mul = 0.99 if self.eidolon >= 5 else 0.90
        if self.EnhancedBasicLootBox:
            e6Mul = 1.5 if self.eidolon >= 6 else 1.0
            self.EnhancedBasicLootBox = False
        else:
            e6Mul = 1.0
        enemyCount = self._getEnemyCount()

        tlb_mul = e5Mul * e6Mul
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELABANGER],
                       [self.element], [tlb_mul/enemyCount, 0], [0, 0], 0, Scaling.ELA, 0, "SilverWolf999TopLootBox"))

        # Random effect
        effect = randrange(1, 4)
        if effect == 1:
            # Big Flipping Sword: 20% True DMG to highest HP enemy
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ELABANGER],
                           [self.element], [e5Mul * 0.2 * e6Mul, 0], [0, 0], 0, Scaling.ELA, 0,
                           "SilverWolf999BigFlippingSword"))
            logger.info(f"{self.name} Top Loot Box: Big Flipping Sword triggered")
        elif effect == 2:
            # Kaboom Eggsplosion: Recover 2 SP
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.NA, [AtkType.ALL],
                           [self.element], [0, 0], [0, 0], 0, Scaling.ELA, 2,
                           "SilverWolf999SPRecovery"))
            logger.info(f"{self.name} Top Loot Box: Kaboom Eggsplosion triggered (+2 SP)")
        else:
            # Funky Munch Bean: Gain 3 Punchline
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.NA, [AtkType.ALL],
                           [self.element], [0, 0], [0, 0], 0, Scaling.ELA, 0,
                           "SilverWolf999FunkyMunchBean"))
            logger.info(f"{self.name} Top Loot Box: Funky Munch Bean triggered (+3 Punchline, +3 Hidden MMR)")
        self._updateEnergyFromMMR()
        self._applyHiddenMMRBuff(bl)
        self._syncPunchlineToHiddenMMR()

    def useElaSkill(self, enemyID=-1):
        """Elation Skill - Enhanced in Godmode."""
        bl, dbl, al, dl, tl, hl = super().useElaSkill(enemyID)

        if self.eidolon >= 5:
            e5Mul = 0.99
        elif 5 > self.eidolon >= 3:
            e5Mul = 0.945
        else:
            e5Mul = 0.9

        #print(f"DEBUG {self.name} useElaSkill | SharedPunchline: {Character.SharedPunchline} | ahaFixedPunchline: {Character.ahaFixedPunchline}")

        self.savedPunchline = Character.SharedPunchline

        if self.godmodeActive:
            if self.eidolon >= 4:
                ExtraPunchMul = (1+(Character.SharedPunchline*5) * 5 / (240 + (Character.SharedPunchline*5))) / (1+Character.SharedPunchline * 5 / (240 + Character.SharedPunchline))
            else:
                ExtraPunchMul = 1
            self.topLootBoxChance = 1.0
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ELAPUNCH],
                           [self.element], [e5Mul * ExtraPunchMul * 6, 0], [30, 0], 0, Scaling.ELA, 0,
                           "SilverWolf999ELASkill"))
        else:
            # Normal Elation Skill
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ELAPUNCH],
                           [self.element], [0, 0], [0, 0], 0, Scaling.ELA, 0,
                           "SilverWolf999NormalELASkill"))
            self.hiddenMMR = min(self.hiddenMMR + 15, self.hiddenMMR_MAX)

        # E2: Check for MMR threshold and grant extra Enhanced Basic if needed (no AV advance)
        extra_basic_turns = self._checkAndExecuteE2ExtraBasic(enemyID, bl, al, dbl)
        tl.extend(extra_basic_turns)

        self._updateEnergyFromMMR()
        self._applyHiddenMMRBuff(bl)
        self._syncPunchlineToHiddenMMR()
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)

        if result.turnName == "AhaSilverWolf999GoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        if result.turnName == "SilverWolf999FunkyMunchBean":
            Character.SharedPunchline += 3

        if result.turnName == "SilverWolf999TechniqueFunkyMunchBean":
            bl.append(Buff("SilverWolf999TechniqueBanger", StatTypes.BANGER, -99, self.role, [AtkType.ALL], 1, 1,
                           self.role, TickDown.START))
        extra_basic_turns = self._checkAndExecuteE2ExtraBasic(self.bestEnemy(-1), bl, al, dbl)
        tl.extend(extra_basic_turns)
        self._updateEnergyFromMMR()
        self._applyHiddenMMRBuff(bl)
        self._syncPunchlineToHiddenMMR()
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)

        if result.turnName == "AhaSilverWolf999GoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        if result.turnName == "AhaElationFixedSequenceComplete":
            self.hiddenMMR += Character.ahaFixedPunchlineValue + self.TotalElationChar

        if result.turnName == "AhaElationSequenceComplete":
            self.hiddenMMR += self.TotalElationChar + Character.savedPunchline

        if result.turnName == "ElationMCUlt":
            self.hiddenMMR += 5
            self.hiddenMMR += Character.ahaFixedPunchlineValue

        if result.turnName == "YaoGuangUlt":
            self.hiddenMMR += 5
            self.hiddenMMR += Character.ahaFixedPunchlineValue

        if result.turnName == "AhaElationFixedEMCSequenceComplete":
            Character.EMCUlt = False
            self.lastPunchlineValue = Character.SharedPunchline

        if self.godmodeActive == True and turn.moveName == "SparxieSkillElaExtra":
            LootboxProcs = floor(turn.dmgSplit[0]/0.2)
            i = 0
            while i < LootboxProcs:
                self._triggerTopLootBox(turn.targetID, tl, bl, is_sp_triggered=True)
                i += 1
        if self.godmodeActive == True and turn.moveName not in bonusDMG and result.turnDmg > 0 and turn.spChange <= -1 and turn.moveName != "SparxieSkill":
            self._triggerTopLootBox(turn.targetID, tl, bl, is_sp_triggered=True)
        # E2: Check for MMR threshold after ally turn damage (no AV advance)
        extra_basic_turns = self._checkAndExecuteE2ExtraBasic(turn.targetID, bl, al, dbl)
        tl.extend(extra_basic_turns)

        extra_basic_turns = self._checkAndExecuteE2ExtraBasic(self.bestEnemy(-1), bl, al, dbl)
        tl.extend(extra_basic_turns)
        self._updateEnergyFromMMR()
        self._applyHiddenMMRBuff(bl)
        self._syncPunchlineToHiddenMMR()
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.AHASpdBuffAmount = specialRes.attr1
        self.TotalElationChar = specialRes.attr2
        self.ElaStat = specialRes.attr3
        self.Punch = specialRes.attr4
        self.SpdStat = specialRes.attr5
        self.Banger = specialRes.attr6
        self.CR = specialRes.attr7

        enemyCount = self._getEnemyCount()

        bl.append(Buff("AhaSpdBuff", StatTypes.SPD, self.AHASpdBuffAmount, Role.AHA, [AtkType.SPECIAL], 1, 1,
                       Role.AHA, TickDown.START))

        if self.tech:
            if not self.techniqueTriggered:
                self.techniqueTriggered = True
                # Use fixed 99 Certified Banger for Elation DMG
                tlb_mul = 0.99 if self.eidolon >= 5 else 0.90
                tlb_mul = tlb_mul * (1.4 if self.eidolon >= 6 else 1.0)
                bl.append(Buff("SilverWolf999TechniqueBanger", StatTypes.BANGER, 99, self.role, [AtkType.ALL], 1, 1,
                              self.role, TickDown.START))
                tl.append(Turn(self.name, self.role, -1, Targeting.AOE, [AtkType.ELABANGER],
                              [self.element], [tlb_mul/enemyCount, 0], [0, 0], 0, Scaling.ELA, 0,
                              "SilverWolf999TechniqueFunkyMunchBean"))
                self.hiddenMMR = min(self.hiddenMMR + 3, self.hiddenMMR_MAX)
                logger.info(f"{self.name} Technique: Funky Munch Bean triggered (+3 Punchline, 99 Banger used)")

            self.tech = False

        # Apply Hidden MMR buffs
        self._applyHiddenMMRBuff(bl)
        self._syncPunchlineToHiddenMMR()

        if self.currSPD >= 160:
            ELABuff = min(max((self.SpdStat - 160), 0), 100)
            bl.append(Buff("SilverWolf999TalentELABuff", StatTypes.ELA, 0.50 + ELABuff * 0.02, self.role, [AtkType.ALL], 1, 1,self.role, TickDown.END))

        # E6: Inflict enemies with Absolute Weakness
        if self.eidolon >= 6:
            dbl.append(Debuff("SilverWolf999E6AbsoluteWeakness", self.role, StatTypes.PEN, 0.20, Role.ALL,[AtkType.ALL], 999, 1, False, [0, 0], False))
            logger.info(f"{self.name} E6: Enemies inflicted with Absolute Weakness (All-Type weakness + RES reduction)")

        self._updateEnergyFromMMR()
        extra_basic_turns = self._checkAndExecuteE2ExtraBasic(self.bestEnemy(-1), bl, al, dbl)
        tl.extend(extra_basic_turns)
        return bl, dbl, al, dl, tl, hl

    def _getEnemyCount(self):
        return self.get_alive_enemy_count()

    def takeTurn(self) -> str:
        return "A" if self.godmodeActive else "E"

    def canUseUlt(self) -> bool:
        return super().canUseUlt() if not self.godmodeActive else False