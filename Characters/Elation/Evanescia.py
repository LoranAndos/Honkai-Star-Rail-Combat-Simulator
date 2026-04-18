import logging

from Buff import *
from Delay_Text import Advance
from Character import Character
from Lightcones.Elation.UntilTheFlowersBloomAgain import UntilTheFlowersBloomAgain
from Lightcones.Elation.TomorrowTogether import TomorrowTogether
from Lightcones.Elation.TodaysGoodLuck import TodaysGoodLuck
from Lightcones.Elation.MushyShroomyAdventures import MushyShroomysAdventuresEMC, MushyShroomysAdventuresSparxie
from Planars.IzumoGenseiAndTakamaDivineRealm import IzumoGenseiAndTakamaDivineRealm
from Planars.PunklordeStageZero import PunklordeStageZero
from RelicStats import RelicStats
from Relics.EverGloriousMagicalGirl import EverGloriousMagicalGirl
from Relics.GeniusOfBrilliantStars import GeniusOfBrilliantStars
from Relics.EagleOfTwilightLine import EagleOfTwilightLine
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
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.FUA: 0,
              AtkType.ELAPUNCH: 0, AtkType.ELABANGER: 0}

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
    Count = 0

    # Elation Skill Participation ID (for Banger conversion mechanics)
    elationParticipationID = 0

    # Master Fox: fires every time currEnergy crosses a new multiple of 240.
    # masterFoxFiredCount tracks how many times it has fired so far this battle.
    MASTER_FOX_THRESHOLD = 240
    masterFoxFiredCount = 0

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, targetRole=Role.DPS, rotation=None, targetPrio=Priority.DEFAULT,
                 elationParticipationID=146) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else UntilTheFlowersBloomAgain(role, 1)
        self.relic1 = r1 if r1 else EverGloriousMagicalGirl(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else PunklordeStageZero(role)
        self.relicStats = subs if subs else RelicStats(5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 13, 10, StatTypes.CD_PERCENT,
                                                       StatTypes.SPD, StatTypes.ATK_PERCENT, StatTypes.ERR_PERCENT)
        self.targetRole = targetRole
        self.rotation = rotation if rotation else ["E"]
        self.masterFoxFiredCount = 0
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
        """Emit the Banger buff that comes from Evanescia gaining energy.
        Per-instance Banger gain from Energy is capped at 100.
        Master Fox is driven purely by currEnergy crossing multiples of 240 —
        there is no separate masterFoxEnergy accumulator.
        """
        bangerGain = min(amount, 100)
        final_banger = floor(bangerGain * (1 + self.ERR))
        bl.append(Buff(f"TalentBangerFromEnergy_{source}{self.Count}", StatTypes.BANGER, final_banger,
                       self.role, [AtkType.ALL], self.BangerDuration, 100, self.role, TickDown.END))
        self.Count += 1
        logger.debug(f"{self.name} +{final_banger} Banger from Energy ({source})")
        return bangerGain, amount

    def _addBangerEnergy(self, bangerAmount: int, bl: list, source: str = ""):
        """When Banger is gained, simultaneously gain equal Energy (ERR_F = no ERR multiplier).
        The ERR_F buff feeds into currEnergy through handleEnergyFromBuffs, which is what
        drives the Master Fox threshold check.
        """
        bl.append(Buff(f"TalentErrFromBanger_{source}{self.Count}", StatTypes.ERR_F, bangerAmount,
                       self.role, [AtkType.ALL], 1, 100, self.role, TickDown.END))
        self.Count += 1
        logger.debug(f"{self.name} +{bangerAmount} ERR_F from Banger sync ({source})")

    def _tryMasterFoxFUA(self, enemyID: int, bl: list, tl: list) -> bool:
        """Fire Master Fox once for every new multiple of 240 that currEnergy has crossed.

        Uses masterFoxFiredCount to know how many times it has already fired, so it
        only fires for thresholds that haven't been consumed yet.

        After useUlt spends 240 energy, currEnergy drops and masterFoxFiredCount is
        synced down in useUlt so the next crossing fires again cleanly.

        Returns True if at least one FUA fired.
        """
        E5MulFUA = 1.1 if self.eidolon >= 5 else 1.0
        E5MulELA = 0.276 if self.eidolon >= 5 else 0.25
        fired = False

        thresholds_crossed = int(self.currEnergy // self.MASTER_FOX_THRESHOLD)

        while self.masterFoxFiredCount < thresholds_crossed:
            self.masterFoxFiredCount += 1
            logger.debug(
                f"{self.name} Master Fox FUA triggered! (fire #{self.masterFoxFiredCount}, "
                f"currEnergy: {self.currEnergy:.1f})")

            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                           Targeting.AOE, [AtkType.FUA], [self.element],
                           [E5MulFUA, 0], [10, 0], 10 * (1 + self.ERR), self.scaling, 0, "EvanesciaMasterFoxFUA"))

            if self.Banger >= 1:
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                               Targeting.AOE, [AtkType.ELABANGER], [self.element],
                               [E5MulELA, 0], [0, 0], 0, Scaling.ELA, 0, "EvanesciaMasterFoxELAPUNCH"))

            # The 10 energy from FUA regen adds Banger but does NOT call _tryMasterFoxFUA
            # recursively — the next check happens in ownTurn after currEnergy has updated.
            self._addEnergy(10, bl, "MasterFoxFUARegen")
            fired = True

        return fired

    # ---------------------------------------------------------------------------
    # Core actions
    # ---------------------------------------------------------------------------

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20, self.scaling, 1, "EvanesciaBasic"))
        self._addEnergy(20, bl, "Basic")
        # _tryMasterFoxFUA not called here — ownTurn handles it after currEnergy settles.
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e5MulMain = 3.3 if self.eidolon >= 5 else 3.0
        e5MulSub = 1.65 if self.eidolon >= 5 else 1.5
        e5MulELA = 0.176 if self.eidolon >= 5 else 0.16
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.BLAST, [AtkType.SKL], [self.element],
                       [e5MulMain, e5MulSub], [20, 10], 30, self.scaling, -1, "EvanesciaSkill"))
        Character.SharedPunchline += 10
        self._addEnergy(30, bl, "Skill")

        if self.Banger >= 1:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                           Targeting.SINGLE, [AtkType.ELABANGER], [self.element],
                           [e5MulELA, 0], [0, 0], 0, Scaling.ELA, 0, "EvanesciaSkillELAPUNCH"))

        # _tryMasterFoxFUA not called here — ownTurn handles it after currEnergy settles.
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        # Sync fired count down so the next crossing of 240 fires Master Fox again.
        self.masterFoxFiredCount = int(self.currEnergy // self.MASTER_FOX_THRESHOLD)

        e3MulAOE = 1.76 if self.eidolon >= 3 else 1.6
        e3MulSingle = 1.296 if self.eidolon >= 3 else 1.2
        e5MulAOE = 0.264 if self.eidolon >= 5 else 0.24
        e5MulSingle = 0.308 if self.eidolon >= 5 else 0.28

        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.AOE, [AtkType.ULT], [self.element],
                       [e3MulAOE, 0], [20, 0], 5, self.scaling, 0, "EvanesciaUlt"))

        enemyCount = self._getEnemyCount()
        if enemyCount >= 3:
            bounceCount = 6
        elif enemyCount == 2:
            bounceCount = 7
        else:
            bounceCount = 9

        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.SINGLE, [AtkType.ULT], [self.element],
                       [e3MulSingle * bounceCount, 0], [5 * bounceCount, 0], 0, self.scaling, 0, "EvanesciaUltSingle"))

        if self.Banger >= 1:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                           Targeting.AOE, [AtkType.ELABANGER], [self.element],
                           [e5MulAOE, 0], [0, 0], 0, Scaling.ELA, 0, "EvanesciaUltELAPUNCH_AOE"))
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                           Targeting.SINGLE, [AtkType.ELABANGER], [self.element],
                           [e5MulSingle * bounceCount, 0], [0, 0], 0, Scaling.ELA, 0, "EvanesciaUltELAPUNCH_ST"))

        self._addEnergy(5, bl, "Ult")

        if self.eidolon == 6:
            if self.UltCounter % 4 == 0:
                self.currEnergy = self.currEnergy + 120
                self._addEnergy(120 / (1 + self.ERR), bl, "E6Ult")
            self.UltCounter += 1

        # _tryMasterFoxFUA not called here — ownTurn handles it after currEnergy settles.
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)

        if result.turnName == "AhaEvanesciaGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        if result.turnName == "EvanesciaMasterFoxFUA":
            dbl.append(Debuff("EvanesciaMasterFoxDebuff", self.role, StatTypes.VULN, 0.12, Role.ALL, [AtkType.ALL], 3, 1))
            if self.eidolon >= 1:
                ela_bl, ela_dbl, ela_al, ela_dl, ela_tl, ela_hl = self.useElaSkill(-1)
                bl.extend(ela_bl); dbl.extend(ela_dbl); al.extend(ela_al)
                dl.extend(ela_dl); tl.extend(ela_tl); hl.extend(ela_hl)

        # Check Master Fox after every action that gave Evanescia energy.
        # By the time ownTurn is called, handleEnergyFromBuffs has already updated
        # currEnergy, so the threshold check is accurate here.
        if result.charRole == self.role and result.turnName in (
            "EvanesciaBasic", "EvanesciaSkill", "EvanesciaUlt",
            "EvanesciaELASkill", "EvanesciaMasterFoxFUA",
        ):
            enemyID = result.enemyID if hasattr(result, 'enemyID') else -1
            self._tryMasterFoxFUA(enemyID, bl, tl)

        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if result.turnName == "AhaEvanesciaGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

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

        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.AOE, [AtkType.ELAPUNCH], [self.element],
                       [e5Mul, 0], [20, 0], 5, Scaling.ELA, 0, "EvanesciaELASkill"))
        if Character.EMCUlt == True:
            bl.append(Buff(f"BangerELASkill{self.Count}", StatTypes.BANGER,
                           20, self.role, [AtkType.ALL], self.BangerDuration, 1,
                           self.role, TickDown.END))
            self.Count += 1
        bl.append(Buff(f"EvanesciaELASkillBanger{self.Count}", StatTypes.BANGER, BangerBuff, self.role, [AtkType.ALL],
                       self.BangerDuration, 100, self.role, TickDown.END))
        self.Count += 1

        # Update currEnergy directly for the instant Banger→Energy portion.
        self.currEnergy = self.currEnergy + BangerBuff

        self._addEnergy(5, bl, "ElaSkill")
        # _tryMasterFoxFUA not called here — ownTurn handles it after currEnergy settles.
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
        bl.append(Buff("EvanesciaTalentELAfromCD", StatTypes.ELA, self.CD * E5CdBuff, self.role, [AtkType.ALL], 1, 1,
                       self.role, TickDown.START))

        if self.tech:
            tl.append(Turn(self.name, self.role, -1, Targeting.AOE, [AtkType.TECH], [self.element], [1, 0], [20, 0], 0,
                           self.scaling, 0, "EvanesciaTech"))
            bl.append(Buff("EvanesciaTechBanger", StatTypes.BANGER, 20, self.role, [AtkType.ALL], self.BangerDuration,
                           1, self.role, TickDown.END))
            self.currEnergy = self.currEnergy + 20
            self.tech = False

        if self.eidolon == 6:
            self.BangerDuration = 3
            bl.append(Buff("EvanesciaE6Merry", StatTypes.MERRY,
                           0.15 + min(floor(self.Banger / 100) * 0.02, 0.20), self.role,
                           [AtkType.ALL], 1, 1, self.role, TickDown.START))

        return bl, dbl, al, dl, tl, hl

    # ---------------------------------------------------------------------------
    # Helper methods
    # ---------------------------------------------------------------------------

    def _getEnemyCount(self):
        return self.get_alive_enemy_count()

    def _handleTeammateBangerConversion(self, turn: Turn, result: Result, bl: list):
        """Stub — external calls from MainFunctions.handleBangerConversions() handle this."""
        pass

    def receiveBangerFromTeammate(self, bangerAmount: int, source: str, bl: list):
        """Called when a teammate with lower Elation ID gains Banger.
        Base: converts 50% into Evanescia's own Banger.
        E2:   converts 100% instead.
        """
        conversionRate = 2.0 if self.eidolon >= 2 else 1.0
        convertedBanger = floor(bangerAmount * conversionRate)
        bl.append(Buff(f"EvanesciaBangerConvert_{source}{self.Count}", StatTypes.BANGER, convertedBanger,
                       self.role, [AtkType.ALL], self.BangerDuration, 100, self.role, TickDown.END))
        self.Count += 1
        logger.debug(f"{self.name} converted {convertedBanger} Banger from teammate {source}")
        self._addBangerEnergy(convertedBanger, bl, f"ConvertedFrom_{source}")

    def receiveBangerFromExpiration(self, bangerAmount: int, source: str, bl: list):
        """Called when a teammate's Banger buff expires.
        Base: converts 50% into Evanescia's own Banger.
        E2:   converts 100% instead.
        """
        conversionRate = 1.5 if self.eidolon >= 2 else 1.0
        convertedBanger = floor(bangerAmount * conversionRate)
        bl.append(Buff(f"EvanesciaBangerExpire_{source}{self.Count}", StatTypes.BANGER, convertedBanger,
                       self.role, [AtkType.ALL], self.BangerDuration, 100, self.role, TickDown.END))
        self.Count += 1
        logger.debug(f"{self.name} converted {convertedBanger} Banger from expired {source} buff")
        self._addBangerEnergy(convertedBanger, bl, f"ExpiredFrom_{source}")

    def receiveEnergyBuff(self, energyAmount: int, source: str, bl: list):
        """Called when Evanescia receives an energy buff from another character.
        Converts the energy into Banger (capped at 100 per instance).
        """
        bangerGain = min(energyAmount, 100)
        bl.append(Buff(f"EvanesciaBangerFromEnergyBuff_{source}{self.Count}", StatTypes.BANGER, bangerGain,
                       self.role, [AtkType.ALL], self.BangerDuration, 100, self.role, TickDown.END))
        self.Count += 1
        logger.debug(f"{self.name} gained {bangerGain} Banger from {energyAmount} energy buff ({source})")

    def receiveEnergyFromDamage(self, energyAmount: int, bl: list):
        """Called when Evanescia receives energy from being hit.
        Converts the energy into Banger (capped at 100 per instance).
        """
        bangerGain = min(energyAmount, 100)
        bl.append(Buff(f"EvanesciaBangerFromDamage{self.Count}", StatTypes.BANGER, bangerGain,
                       self.role, [AtkType.ALL], self.BangerDuration, 100, self.role, TickDown.END))
        self.Count += 1
        logger.debug(f"{self.name} gained {bangerGain} Banger from {energyAmount} hit energy")