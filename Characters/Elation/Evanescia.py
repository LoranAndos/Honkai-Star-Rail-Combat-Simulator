import logging

from Buff import *
from Delay_Text import Advance
from Character import Character
from Lightcones.Elation.UntilTheFlowersBloomAgain import UntilTheFlowersBloomAgain
from Lightcones.Elation.TomorrowTogether import TomorrowTogether
from Lightcones.Elation.TodaysGoodLuck import TodaysGoodLuck
from Lightcones.Elation.MushyShroomyAdventures import MushyShroomysAdventuresEMC
from Planars.IzumoGenseiAndTakamaDivineRealm import IzumoGenseiAndTakamaDivineRealm
from Planars.PunklordeStageZero import PunklordeStageZero
from RelicStats import RelicStats
from Relics.EverGloriousMagicalGirl import EverGloriousMagicalGirl
from Relics.GeniusOfBrilliantStars import GeniusOfBrilliantStars
from Result import *
from Turn_Text import Turn
from Healing import *
from random import randrange
from math import floor

logger = logging.getLogger(__name__)


class Evanescia(Character):
    # Standard Character Settings
    name = "Evanescia"
    path = Path.ELATION
    element = Element.PHYSICAL
    scaling = Scaling.ATK
    baseHP = 1048
    baseATK = 737
    baseDEF = 461
    baseSPD = 104
    maxEnergy = 480
    currEnergy = 240
    ultCost = 240
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0,AtkType.BRK: 0, AtkType.FUA: 0, AtkType.ELAPUNCH: 0, AtkType.ELABANGER: 0}

    # Unique Character Properties
    hasSummon = True
    AHASpdBuffAmount = 0
    TotalElationChar = 0
    ElaStat = 0
    Punch = 0
    Banger = 0
    tech = True
    BangerDuration = 2
    UltCounter = 0
    ERR = 0.0

    # Elation Skill Participation ID (for Banger conversion mechanics)
    # Lower ID = higher priority for Banger conversion
    elationParticipationID = 0  # Set this appropriately in team setup

    # Talent: Master Fox energy accumulator (separate from currEnergy / ult cost)
    # Tracks energy accumulated toward the 240-threshold that triggers Master Fox's FUA.
    masterFoxEnergy = 0
    MASTER_FOX_THRESHOLD = 240

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, targetRole=Role.DPS, rotation=None, targetPrio=Priority.DEFAULT,
                 elationParticipationID=146) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else UntilTheFlowersBloomAgain(role, 1)
        self.relic1 = r1 if r1 else EverGloriousMagicalGirl(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else PunklordeStageZero(role)
        self.relicStats = subs if subs else RelicStats(5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 13, 10, StatTypes.CD_PERCENT,
                                                       StatTypes.SPD,StatTypes.ATK_PERCENT, StatTypes.ERR_PERCENT)
        self.targetRole = targetRole
        self.rotation = rotation if rotation else ["E"]
        self.masterFoxEnergy = 0
        self.elationParticipationID = elationParticipationID

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("BangerStartBattle", StatTypes.BANGER, 20, self.role, [AtkType.ALL], self.BangerDuration, 1, self.role, TickDown.END))
        bl.append(Buff("EvanesciaTraceCR", StatTypes.CR_PERCENT, 0.187, self.role))
        bl.append(Buff("EvanesciaTraceSPD", StatTypes.SPD, 5, self.role))
        bl.append(Buff("EvenesciaTraceELA", StatTypes.ELA, 0.18, self.role))
        bl.append(Buff("EvanesciaTrace1CR", StatTypes.CR_PERCENT, 0.30, self.role))
        bl.append(Buff("EvanesciaBangerStart", StatTypes.BANGER, 240, self.role, [AtkType.ALL], self.BangerDuration, 1, self.role, TickDown.END))

        if self.eidolon >= 2:
            bl.append(Buff("EvanesciaE2CD", StatTypes.CD_PERCENT, 0.36, self.role))
        if self.eidolon >= 1:
            bl.append(Buff("EvanesciaE1PEN", StatTypes.PEN, 0.20, self.role))
        if self.eidolon >= 4:
            bl.append(Buff("EvanesciaE4Shred", StatTypes.SHRED, 0.15, self.role))
        return bl, dbl, al, dl, hl

    # ---------------------------------------------------------------------------
    # Talent helpers
    # ---------------------------------------------------------------------------

    def _addEnergy(self, amount: int, bl: list, source: str = ""):
        """Add energy to masterFoxEnergy and apply the bidirectional Banger sync.

        Per instance: Banger gained from this energy cannot exceed 100.
        Returns (bangerGained, energyAdded) for logging/chaining.
        """
        # Calculate base values before ERR
        bangerGain = min(amount, 100)

        # Apply ERR multiplier ONCE to get final amounts
        final_banger = floor(bangerGain * (1 + self.ERR))
        final_energy = floor(amount * (1 + self.ERR))

        # Add Banger buff
        bl.append(Buff(f"TalentBangerFromEnergy_{source}", StatTypes.BANGER, final_banger,
                       self.role, [AtkType.ALL], 1, 100, self.role, TickDown.END))

        # Add to masterFoxEnergy (using the already-multiplied value)
        self.masterFoxEnergy += final_energy

        logger.debug(
            f"{self.name} +{final_energy} masterFoxEnergy (total {self.masterFoxEnergy}) | +{final_banger} Banger from Energy")
        return bangerGain, amount

    def _addBangerEnergy(self, bangerAmount: int, bl: list, source: str = ""):
        """When Banger is gained, simultaneously gain equal Energy (uncapped for the energy side).
        The per-instance cap only applies to the Banger-from-Energy direction, not Energy-from-Banger.
        """
        bl.append(Buff(f"TalentErrFromBanger_{source}", StatTypes.ERR_F, bangerAmount,
                       self.role, [AtkType.ALL], 1, 1, self.role, TickDown.END))
        # CRITICAL FIX: Actually add to masterFoxEnergy when Banger is gained
        self.masterFoxEnergy += bangerAmount
        logger.debug(
            f"{self.name} +{bangerAmount} ERR from Banger sync ({source}) | masterFoxEnergy now {self.masterFoxEnergy}")

    def _tryMasterFoxFUA(self, enemyID: int, bl: list, tl: list) -> bool:
        """Check masterFoxEnergy threshold and emit Master Fox FUA if reached.
        Master Fox FUA:
          - Deals 100% ATK AOE Physical DMG (AtkType.FUA)
          - Regenerates 10 Energy for Evanescia
          - Also deals 25% ELAPUNCH AOE (Elation DMG)
        Returns True if FUA fired.
        """
        E5MulFUA = 1.1 if self.eidolon >= 5 else 1.0
        E5MulELA = 0.276 if self.eidolon >= 5 else 0.25
        if self.masterFoxEnergy >= self.MASTER_FOX_THRESHOLD:
            self.masterFoxEnergy -= self.MASTER_FOX_THRESHOLD
            logger.debug(f"{self.name} Master Fox FUA triggered! masterFoxEnergy remaining: {self.masterFoxEnergy}")

            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                           Targeting.AOE, [AtkType.FUA], [self.element],
                           [E5MulFUA, 0], [20, 0], 10*(1+self.ERR), self.scaling, 0, "EvanesciaMasterFoxFUA"))

            if self.Banger >= 1:
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                               Targeting.AOE, [AtkType.ELABANGER], [self.element],
                               [E5MulELA, 0], [0, 0], 0, Scaling.ELA, 0, "EvanesciaMasterFoxELAPUNCH"))

            # The 10 ERR from FUA feeds back into masterFoxEnergy via the Energy<->Banger sync
            self._addEnergy(10, bl, "MasterFoxFUARegen")
            return True
        return False

    # ---------------------------------------------------------------------------
    # Core actions
    # ---------------------------------------------------------------------------

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20*(1+self.ERR), self.scaling, 1, "EvanesciaBasic"))
        # Basic gives 20 ERR — sync to masterFoxEnergy
        self._addEnergy(20, bl, "Basic")
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e5MulMain = 3.3 if self.eidolon >= 5 else 3.0
        e5MulSub = 1.65 if self.eidolon >= 5 else 1.5
        e5MulELA = 0.176 if self.eidolon >= 5 else 0.16
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.BLAST, [AtkType.SKL], [self.element],
                       [e5MulMain, e5MulSub], [20, 10], 30*(1+self.ERR), self.scaling, -1, "EvanesciaSkill"))
        Character.SharedPunchline += 10
        # Skill gives 30 ERR — sync to masterFoxEnergy
        self._addEnergy(30, bl, "Skill")

        # Talent: if Banger >= 1, Skill also deals 16% ELAPUNCH ST to the attacked target
        if self.Banger >= 1:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                           Targeting.SINGLE, [AtkType.ELABANGER], [self.element],
                           [e5MulELA, 0], [0, 0], 0, Scaling.ELA, 0, "EvanesciaSkillELAPUNCH"))

        self._tryMasterFoxFUA(enemyID, bl, tl)
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e3MulAOE = 1.76 if self.eidolon >= 3 else 1.6
        e3MulSingle = 1.296 if self.eidolon >= 3 else 1.2
        e5MulAOE = 0.264 if self.eidolon >= 5 else 0.24
        e5MulSingle = 0.308 if self.eidolon >= 5 else 0.28

        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.AOE, [AtkType.ULT], [self.element],
                       [e3MulAOE, 0], [20, 0], 5*(1+self.ERR), self.scaling, 0, "EvanesciaUlt"))

        # NEW: Calculate bounce count based on enemy count
        # Base bounce is 5 (from the original single target turn below)
        # 3+ enemies: +1 bounce = 6 total
        # 2 enemies: +2 bounces = 7 total
        # 1 enemy: +4 bounces = 9 total
        enemyCount = self._getEnemyCount()
        if enemyCount >= 3:
            bounceCount = 6
        elif enemyCount == 2:
            bounceCount = 7
        else:  # 1 enemy
            bounceCount = 9

        # Single target bounces with dynamic count
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.SINGLE, [AtkType.ULT], [self.element],
                       [e3MulSingle * bounceCount, 0], [5 * bounceCount, 0], 0, self.scaling, 0, "EvanesciaUltSingle"))

        # Talent: if Banger >= 1, Ult also fires Elation hits
        # Ult Elation DMG uses Banger >= maxEnergy (480) — clamp via savedPunchline + forced floor
        if self.Banger >= 1:
            # AOE ELAPUNCH: 24%
            # For Ult Elation hits the Banger used must be at least maxEnergy (480).
            # We temporarily force SharedPunchline to max(SharedPunchline, maxEnergy) for these turns.

            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                           Targeting.AOE, [AtkType.ELABANGER], [self.element],
                           [e5MulAOE, 0], [0, 0], 0, Scaling.ELA, 0, "EvanesciaUltELAPUNCH_AOE"))

            # ST ELAPUNCH: 25% to the random enemy target already chosen by bestEnemy
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                           Targeting.SINGLE, [AtkType.ELABANGER], [self.element],
                           [e5MulSingle*bounceCount, 0], [0, 0], 0, Scaling.ELA, 0, "EvanesciaUltELAPUNCH_ST"))

        # Ult gives 5 ERR — sync to masterFoxEnergy
        self._addEnergy(5, bl, "Ult")

        if self.eidolon == 6:
            if self.UltCounter % 4 == 0:
                bl.append(Buff("EvanesciaUltExtraERR", StatTypes.ERR_F, 120, self.role, [AtkType.ALL], 1, 1, self.role,
                               TickDown.START))
                self._addEnergy(120, bl, "E6Ult")
            self.UltCounter += 1

        self._tryMasterFoxFUA(enemyID, bl, tl)
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        if result.turnName == "AhaEvanesciaGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        if result.turnName == "EvanesciaMasterFoxFUA":
            dbl.append(Debuff("EvanesciaMasterFoxDebuff",self.role, StatTypes.VULN,0.12,Role.ALL, [AtkType.ALL], 3, 1))
            if self.eidolon >= 1:
                return self.useElaSkill(-1)

        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if result.turnName == "AhaEvanesciaGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        # NEW: Handle teammate Banger buffs for conversion
        self._handleTeammateBangerConversion(turn, result, bl)

        return bl, dbl, al, dl, tl, hl

    def useElaSkill(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useElaSkill(enemyID)
        if self.eidolon >= 5:
            e5Mul = 1.21
        elif 5 > self.eidolon >= 3:
            e5Mul = 1.155
        else:
            e5Mul = 1.10
        if self.eidolon >= 1:
            BangerBuff = 15
        else:
            BangerBuff = 5

        #print(f"DEBUG {self.name} useElaSkill | SharedPunchline: {Character.SharedPunchline} | ahaFixedPunchline: {Character.ahaFixedPunchline}")

        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.AOE, [AtkType.ELAPUNCH], [self.element],
                       [e5Mul, 0], [20, 0], 5*(1+self.ERR), Scaling.ELA, 0, "EvanesciaELASkill"))
        bl.append(Buff("EvanesciaELASkillBanger", StatTypes.BANGER, BangerBuff, self.role, [AtkType.ALL], self.BangerDuration, 100,
                 self.role, TickDown.END))
        self.currEnergy = self.currEnergy + BangerBuff
        self.masterFoxEnergy += BangerBuff

        self._addEnergy(5, bl, "ElaSkill")
        self._tryMasterFoxFUA(enemyID, bl, tl)
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.AHASpdBuffAmount = specialRes.attr1
        self.TotalElationChar = specialRes.attr2
        self.ElaStat = specialRes.attr3
        self.Punch = specialRes.attr4
        self.Banger = specialRes.attr5
        self.CD = specialRes.attr6
        self.ERR = specialRes.attr7
        E5CdBuff = 0.22 if self.eidolon >= 5 else 0.20
        bl.append(Buff("AhaSpdBuff", StatTypes.SPD, self.AHASpdBuffAmount, Role.AHA, [AtkType.SPECIAL], 1, 1, Role.AHA,
                       TickDown.START))

        bl.append(
            Buff("EvanesciaTalentELAfromCD", StatTypes.ELA, self.CD * E5CdBuff, self.role, [AtkType.ALL], 1, 1, self.role,
                 TickDown.START))

        if self.tech:
            tl.append(
                Turn(self.name, self.role, -1, Targeting.AOE, [AtkType.TECH], [self.element], [1, 0], [20, 0], 0,
                     self.scaling, 0, "EvanesciaTech"))
            bl.append(
                Buff("EvanesciaTechBanger", StatTypes.BANGER, 20, self.role, [AtkType.ALL], self.BangerDuration, 1,
                     self.role, TickDown.END))
            self.currEnergy = self.currEnergy + 20
            self.tech = False

        if self.eidolon == 6:
            self.BangerDuration = 3
            bl.append(
                Buff("EvanesciaE6Merry", StatTypes.MERRY, 0.15 + min(floor(self.Banger / 100) * 0.02, 0.20), self.role,
                     [AtkType.ALL], 1, 1, self.role, TickDown.START))

        return bl, dbl, al, dl, tl, hl

    # ---------------------------------------------------------------------------
    # NEW: Helper methods for new abilities
    # ---------------------------------------------------------------------------

    def _getEnemyCount(self):
        """Get the current number of alive enemies.

        Used for dynamic bounce calculation in Ultimate:
        - 3+ enemies: 6 bounces total
        - 2 enemies: 7 bounces total
        - 1 enemy: 9 bounces total
        """
        return self.get_alive_enemy_count()

    def _handleTeammateBangerConversion(self, turn: Turn, result: Result, bl: list):
        """Handle Banger conversion from teammates.

        When a teammate with lower Elation Skill Participation ID gains Banger,
        Evanescia converts 50% of it into her own Banger.

        This method is triggered from MainFunctions.handleBangerConversions()
        when a teammate's Banger buff is detected.
        """
        pass

    def receiveBangerFromTeammate(self, bangerAmount: int, source: str, bl: list):
        """Called by the simulation when a teammate with lower ID gains Banger.
        Converts 50% of the teammate's Banger into Evanescia's own Banger.
        """
        Conversion_Amount = 1.5 if self.eidolon >= 2 else 1
        convertedBanger = bangerAmount * Conversion_Amount
        bl.append(Buff(f"EvanesciaBangerConvert_{source}", StatTypes.BANGER, convertedBanger,
                       self.role, [AtkType.ALL], self.BangerDuration, 100, self.role, TickDown.END))
        logger.debug(f"{self.name} converted {convertedBanger} Banger from teammate {source}")

        # Apply bidirectional sync: Banger → Energy
        self._addBangerEnergy(convertedBanger, bl, f"ConvertedFrom_{source}")

    def receiveBangerFromExpiration(self, bangerAmount: int, source: str, bl: list):
        """Called by the simulation when a teammate's Banger buff expires.
        Converts 50% of the expired Banger into Evanescia's own Banger.
        """
        Conversion_Amount = 2 if self.eidolon >= 2 else 1
        convertedBanger = bangerAmount * Conversion_Amount
        bl.append(Buff(f"EvanesciaBangerExpire_{source}", StatTypes.BANGER, convertedBanger,
                       self.role, [AtkType.ALL], self.BangerDuration, 100, self.role, TickDown.END))
        logger.debug(f"{self.name} converted {convertedBanger} Banger from expired {source} buff")

        # Apply bidirectional sync: Banger → Energy
        self._addBangerEnergy(convertedBanger, bl, f"ExpiredFrom_{source}")

    def receiveEnergyBuff(self, energyAmount: int, source: str, bl: list):
        """NEW: Called when Evanescia receives an energy buff from another character.
        Converts the energy into Banger (capped at 100 per instance).
        """
        bangerGain = min(energyAmount, 100)
        bl.append(Buff(f"EvanesciaBangerFromEnergyBuff_{source}", StatTypes.BANGER, bangerGain,
                       self.role, [AtkType.ALL], self.BangerDuration, 100, self.role, TickDown.END))
        logger.debug(f"{self.name} gained {bangerGain} Banger from {energyAmount} energy buff from {source}")

        # Also add to masterFoxEnergy (the energy itself)
        self.masterFoxEnergy += energyAmount
        logger.debug(f"{self.name} +{energyAmount} masterFoxEnergy from buff (total {self.masterFoxEnergy})")

    def receiveEnergyFromDamage(self, energyAmount: int, bl: list):
        """NEW: Called when Evanescia receives energy from being hit.
        Converts the energy into Banger (capped at 100 per instance).
        """
        bangerGain = min(energyAmount, 100)
        bl.append(Buff(f"EvanesciaBangerFromDamage", StatTypes.BANGER, bangerGain,
                       self.role, [AtkType.ALL], self.BangerDuration, 100, self.role, TickDown.END))
        logger.debug(f"{self.name} gained {bangerGain} Banger from {energyAmount} energy received from damage")

        # Also add to masterFoxEnergy
        self.masterFoxEnergy += energyAmount
        logger.debug(f"{self.name} +{energyAmount} masterFoxEnergy from damage (total {self.masterFoxEnergy})")