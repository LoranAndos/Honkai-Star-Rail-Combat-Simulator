import logging

from Buff import *
from Delay_Text import Advance
from Character import Character
from Lightcones.Elation.WelcomeToTheCosmicCity import WelcometotheCosmicCity
from Lightcones.Elation.MushyShroomyAdventures import MushyShroomysAdventures
from Planars.PunklordeStageZero import PunklordeStageZero
from RelicStats import RelicStats
from Relics.EverGloriousMagicalGirl import EverGloriousMagicalGirl
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
    tech = True

    # SilverWolf999 Specific Properties
    hiddenMMR = 0  # Talent: tracks Hidden MMR points
    hiddenMMR_MAX = 300  # Can overflow by 240, base 60 = 300 total
    godmodeActive = False  # State for Godmode Player
    godmodeBasicCount = 0  # Count Enhanced Basic ATK uses
    topLootBoxChance = 1.0  # Initial 100%, reduces to 20% after each trigger
    topLootBoxTriggersRemaining = 3  # 3 triggers per Ultimate
    WolfInstants = 0  # Legacy property

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, targetRole=Role.DPS, rotation=None, targetPrio=Priority.DEFAULT,
                 elationParticipationID=145) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else WelcometotheCosmicCity(role, 1)
        self.relic1 = r1 if r1 else EverGloriousMagicalGirl(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else PunklordeStageZero(role)
        self.relicStats = subs if subs else RelicStats(5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 13, 10, StatTypes.CD_PERCENT,
                                                       StatTypes.SPD, StatTypes.ATK_PERCENT, StatTypes.ERR_PERCENT)
        self.targetRole = targetRole
        self.rotation = rotation if rotation else ["E"]
        self.elationParticipationID = elationParticipationID
        self.hiddenMMR = 0
        self.godmodeActive = False
        self.godmodeBasicCount = 0
        self.topLootBoxChance = 1.0
        self.topLootBoxTriggersRemaining = 3

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(
            Buff("BangerStartBattle", StatTypes.BANGER, 20, self.role, [AtkType.ALL], 2, 1, self.role, TickDown.END))
        bl.append(Buff("SilverWolf999TraceCR", StatTypes.CR_PERCENT, 0.187, self.role))
        bl.append(Buff("SilwerWolf999TraceSPD", StatTypes.SPD, 9, self.role))
        bl.append(Buff("SilverWolf999TraceELA", StatTypes.ELA, 0.10, self.role))
        return bl, dbl, al, dl, hl

    # =========================================================================
    # TALENT: Hidden MMR → CRIT Rate/CRIT DMG conversion
    # =========================================================================

    def _applyHiddenMMRBuff(self, bl: list):
        """Apply Hidden MMR buffs: 0.3% CRIT Rate per point, then 0.6% CRIT DMG after 100% CR."""
        if self.hiddenMMR <= 0:
            return

        # Calculate CR boost: 0.3% per Hidden MMR point, capped at 100%
        cr_from_mmr = min(self.hiddenMMR * 0.003, 1.0)
        if cr_from_mmr > 0:
            bl.append(Buff("SilverWolf999HiddenMMRCR", StatTypes.CR_PERCENT, cr_from_mmr, self.role,
                           [AtkType.ALL], 1, 1, self.role, TickDown.START))

        # After 100% CR, overflow MMR becomes CRIT DMG: 0.6% per point
        overflow_mmr = max(self.hiddenMMR - (100 / 0.3), 0)  # ~333 points → 100% CR
        if overflow_mmr > 0:
            cd_from_mmr = overflow_mmr * 0.006
            bl.append(Buff("SilverWolf999HiddenMMRCD", StatTypes.CD_PERCENT, cd_from_mmr, self.role,
                           [AtkType.ALL], 1, 1, self.role, TickDown.START))

    def _enterGodmode(self, bl: list, al: list) -> bool:
        """Enter Godmode Player state. Returns True if entered."""
        if self.hiddenMMR >= 60 and not self.godmodeActive:
            self.godmodeActive = True
            self.godmodeBasicCount = 0
            self.topLootBoxChance = 1.0
            self.topLootBoxTriggersRemaining = 3
            bl.append(Buff("SilverWolf999Godmode", StatTypes.CC_IMMUNITY, 1, self.role, [AtkType.ALL], 999, 1,
                           self.role, TickDown.START))
            al.append(Advance("SilverWolf999GodmodeAdvance", self.role, 1.0))  # 100% advance
            logger.info(f"{self.name} entered Godmode Player state (Hidden MMR: {self.hiddenMMR})")
            return True
        return False

    def _exitGodmode(self):
        """Exit Godmode Player state and clear Hidden MMR."""
        if self.godmodeActive:
            self.godmodeActive = False
            self.godmodeBasicCount = 0
            self.hiddenMMR = 0  # Clear Hidden MMR on exit
            logger.info(f"{self.name} exited Godmode Player state")

    # =========================================================================
    # CORE ACTIONS
    # =========================================================================

    def useBsc(self, enemyID=-1):
        """Basic ATK - enhanced when in Godmode."""
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)

        if self.godmodeActive:
            # Enhanced Basic ATK in Godmode
            enhanced_turns = self._useEnhancedBasic(enemyID, bl, al)
            tl.extend(enhanced_turns)
        else:
            # Normal Basic ATK
            e3Mul = 1.1 if self.eidolon >= 3 else 1.0
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC],
                           [self.element], [e3Mul, 0], [10, 0], 0, self.scaling, 1, "SilverWolf999Basic"))

        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        """Skill ATK - applies Banger dependent Imaginary Elation DMG."""
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e3Mul = 1.76 if self.eidolon >= 3 else 1.6

        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.SKL],
                       [self.element], [e3Mul, 0], [10, 0], 0, self.scaling, -1, "SilverWolf999Skill"))

        Character.SharedPunchline += 5

        # Banger talent: 40% Imaginary Elation DMG while in possession of Certified Banger
        if self.Banger >= 1:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELAPUNCH],
                           [self.element], [0.40, 0], [0, 0], 0, Scaling.ELA, 0, "SilverWolf999SkillElation"))

        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        """Ultimate: Enters Godmode and creates Zone."""
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost + 20

        # Enter Godmode
        self._enterGodmode(bl, al)

        # Create Zone (logical marker for Top Loot Box triggers)
        bl.append(Buff("SilverWolf999Zone", StatTypes.BANGER, 0, self.role, [AtkType.ALL], 999, 1,
                       self.role, TickDown.START))

        logger.info(f"{self.name} used Ultimate: entered Godmode (Hidden MMR: {self.hiddenMMR})")

        return bl, dbl, al, dl, tl, hl

    def _useEnhancedBasic(self, enemyID: int, bl: list, al: list) -> list:
        """Enhanced Basic ATK: 100 bounces with 3 Top Loot Box triggers."""
        tl = []
        base_mul = 2.2 / 100  # 220% split among 100 bounces

        # DMG boost from Hidden MMR: +15% per 60 points (stackable up to 2x = +30%)
        mmr_boost_multiplier = 1.0 + (floor(min(self.hiddenMMR, 120) / 60) * 0.15)
        base_mul_boosted = base_mul * mmr_boost_multiplier

        # Each bounce
        bounce_count = 100
        bounces_per_lootbox = bounce_count // 3  # ~33 bounces between triggers

        for i in range(bounce_count):
            tl.append(Turn(self.name, self.role, -1, Targeting.SINGLE, [AtkType.BSC],
                           [self.element], [base_mul_boosted, 0], [0, 0], 0, self.scaling, 0,
                           f"SilverWolf999EnhancedBounce_{i + 1}"))

            # Pause for Top Loot Box trigger every ~33 bounces
            if (i + 1) % bounces_per_lootbox == 0 and self.topLootBoxTriggersRemaining > 0:
                self._triggerTopLootBox(enemyID, tl, bl)

        # Final Hit: 90% ATK split among all enemies
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.BSC],
                       [self.element], [0.9, 0], [0, 0], 0, self.scaling, 0, "SilverWolf999EnhancedFinal"))

        # Increment basic count and check Godmode exit
        self.godmodeBasicCount += 1
        if self.godmodeBasicCount >= 3:
            self._exitGodmode()
            al.append(Advance("SilverWolf999GodmodeExit", self.role, 1.0))  # Extra turn on exit
            # Extend buff duration by 1
            bl.append(Buff("SilverWolf999ExtendBuffs", StatTypes.BANGER, 0, self.role, [AtkType.ALL], 1, 1,
                           self.role, TickDown.START))

        return tl

    def _triggerTopLootBox(self, enemyID: int, tl: list, bl: list):
        """Top Loot Box: 90% Imaginary Elation DMG + random effect."""
        # Check trigger chance
        if random() > self.topLootBoxChance:
            # Chance failed, reduce for next time
            self.topLootBoxChance *= 0.2
            logger.debug(f"{self.name} Top Loot Box trigger failed (chance was {self.topLootBoxChance / 0.2:.0%})")
            return

        self.topLootBoxTriggersRemaining -= 1
        self.topLootBoxChance *= 0.2  # Reduce to 20% of current

        # Top Loot Box hit: 90% split among enemies
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELAPUNCH],
                       [self.element], [0.90, 0], [0, 0], 0, Scaling.ELA, 0, "SilverWolf999TopLootBox"))

        # Random effect
        effect = randint(1, 3)
        if effect == 1:
            # Big Flipping Sword: 20% True DMG to highest HP enemy
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.FUA],
                           [self.element], [0.20, 0], [0, 0], 0, self.scaling, 0, "SilverWolf999BigFlippingSword"))
            logger.info(f"{self.name} Top Loot Box: Big Flipping Sword triggered")
        elif effect == 2:
            # Kaboom Eggsplosion: Recover 2 SP
            bl.append(Buff("SilverWolf999SPRecovery", StatTypes.SP_GAIN, 2, self.role, [AtkType.ALL], 1, 1,
                           self.role, TickDown.START))
            logger.info(f"{self.name} Top Loot Box: Kaboom Eggsplosion triggered (+2 SP)")
        else:
            # Funky Munch Bean: Gain 3 Punchline
            Character.SharedPunchline += 3
            self.hiddenMMR = min(self.hiddenMMR + 3, self.hiddenMMR_MAX)
            logger.info(f"{self.name} Top Loot Box: Funky Munch Bean triggered (+3 Punchline, +3 Hidden MMR)")

    def useElaSkill(self, enemyID=-1):
        """Elation Skill - Enhanced in Godmode."""
        bl, dbl, al, dl, tl, hl = super().useElaSkill(enemyID)

        if self.eidolon >= 5:
            e5Mul = 0.99
        elif 5 > self.eidolon >= 3:
            e5Mul = 0.945
        else:
            e5Mul = 0.9

        self.savedPunchline = Character.SharedPunchline
        if Character.ahaFixedPunchline:
            Character.SharedPunchline = Character.ahaFixedPunchlineValue  # set to 20 or 40
            self.currEnergy += Character.ahaFixedPunchlineValue

        if self.godmodeActive:
            # Enhanced Elation Skill (converted to Elation DMG at same multiplier as Enhanced Basic)
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELAPUNCH],
                           [self.element], [1.5, 0], [20, 0], 0, Scaling.ELA, 0, "SilverWolf999EnhancedElaSkill"))
        else:
            # Normal Elation Skill
            self.currEnergy += 15
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELAPUNCH],
                           [self.element], [e5Mul, 0], [5, 0], 0, Scaling.ELA, -1, "SilverWolf999ELASkill"))
            for i in range(1, 5, 1):
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                               Targeting.SINGLE, [AtkType.ELAPUNCH], [self.element],
                               [e5Mul, 0], [5, 0], 0, Scaling.ELA, -1, "SilverWolf999ELASkillExtra"))

        # Banger talent: 40% Imaginary Elation DMG
        if self.Banger >= 1:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELAPUNCH],
                           [self.element], [0.40, 0], [0, 0], 0, Scaling.ELA, 0, "SilverWolf999ElaSkillBangerTalent"))

        bl.append(
            Buff("BangerELASkill", StatTypes.BANGER, self.SharedPunchline, self.role, [AtkType.ALL], 2, 1, self.role,
                 TickDown.END))
        if Character.ahaFixedPunchline:
            Character.SharedPunchline = self.savedPunchline

        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)

        if result.turnName == "AhaSilverWolf999GoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        # Handle Godmode state transitions
        if result.turnName == "AhaFixedEndGoGo":
            Character.ahaFixedPunchline = False
            Character.ahaFixedPunchlineValue = 20
            Character.ahaElaDMGBoost = 1.0

        if result.turnName == "AhaElationSequenceComplete":
            Character.SharedPunchline = 3
            Character.ahaFixedPunchline = False

        if result.turnName == "AhaEndGoGo":
            Character.ahaFixedPunchline = False
            Character.ahaFixedPunchlineValue = 20
            Character.ahaElaDMGBoost = 1.0

        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)

        if result.turnName == "AhaSilverWolf999GoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        if result.turnName == "AhaFixedEndGoGo":
            Character.ahaFixedPunchline = False
            Character.ahaFixedPunchlineValue = 20
            Character.ahaElaDMGBoost = 1.0

        if result.turnName == "AhaElationSequenceComplete":
            Character.SharedPunchline = 3
            Character.ahaFixedPunchline = False

        if result.turnName == "AhaEndGoGo":
            Character.ahaFixedPunchline = False
            Character.ahaFixedPunchlineValue = 20
            Character.ahaElaDMGBoost = 1.0

        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.AHASpdBuffAmount = specialRes.attr1
        self.TotalElationChar = specialRes.attr2
        self.ElaStat = specialRes.attr3
        self.Punch = specialRes.attr4
        self.SpdStat = specialRes.attr5
        self.Banger = specialRes.attr6 if len(specialRes.attr) > 5 else 0

        bl.append(Buff("AhaSpdBuff", StatTypes.SPD, self.AHASpdBuffAmount, Role.AHA, [AtkType.SPECIAL], 1, 1,
                       Role.AHA, TickDown.START))

        if self.tech:
            tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.TECH], [self.element], [1, 0],
                           [20, 0], 0, self.scaling, 0, "SilverWolf999Tech"))
            self.tech = False

        # Apply Hidden MMR buffs
        self._applyHiddenMMRBuff(bl)

        if self.currSPD >= 150:
            ELABuff = min(max((self.SpdStat - 150), 0), 100)
            bl.append(
                Buff("SilverWolf999TalentELABuff", StatTypes.ELA, 0.30 + ELABuff * 0.02, self.role, [AtkType.ALL], 1, 1,
                     self.role, TickDown.START))

        return bl, dbl, al, dl, tl, hl

    def takeTurn(self) -> str:
        return "A" if self.godmodeActive else "E"

    def canUseUlt(self) -> bool:
        return super().canUseUlt() if not self.godmodeActive else False