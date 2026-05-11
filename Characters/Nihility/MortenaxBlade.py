import logging

from Buff import *
from Character import Character
from Lightcones.Nihility.ReforgedInHellfire import ReforgedInHellfire
from Lightcones.Nihility.ResolutionShinesAsPearlsOfSweat import ResolutionMortenaxBlade
from Lightcones.Nihility.GoodNightAndSleepWell import GoodNightAndSleepWell
from Planars.BoneCollectionsSereneDemesne import BoneCollectionsSereneDemesne
from RelicStats import RelicStats
from Relics.DivineQueryingMasterSmith import DivineQueryMasterSmith
from Result import *
from Turn_Text import Turn
from Healing import *

logger = logging.getLogger(__name__)


class MortenaxBlade(Character):
    # Standard Character Settings
    name = "MortenaxBlade"
    path = Path.NIHILITY
    element = Element.FIRE
    scaling = Scaling.HP
    baseHP = 1358
    baseATK = 543
    baseDEF = 485
    baseSPD = 107
    maxEnergy = 80
    currEnergy = 40
    ultCost = 80
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.FUA: 0}  # Adjust accordingly

    # Unique Character Properties
    hasSummon = True

    EnhancedState = False
    ChargeCount = 0
    NihilityCount = 1
    Tech = True
    overflowEnergy = 0.0  # Accumulates up to 80 extra energy outside enhanced state
    E2AllyUltChargeCount = 0  # Tracks ally ult-as-FUA charges this reset window (max 9)
    E6ChargeReady = True      # E6: resets after any unit's turn, allows 1 charge per turn

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else ReforgedInHellfire(role, 1)
        self.relic1 = r1 if r1 else DivineQueryMasterSmith(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else BoneCollectionsSereneDemesne(role)
        self.relicStats = subs if subs else RelicStats(10, 2, 2, 2, 2, 2, 2, 2, 2, 2, 12, 4, StatTypes.CR_PERCENT, StatTypes.SPD,
                                                       StatTypes.HP_PERCENT, StatTypes.HP_PERCENT)
        self.rotation = rotation if rotation else ["E"]
        self.overflowEnergy = 0.0
        self.E2AllyUltChargeCount = 0
        self.E6ChargeReady = True

    def addEnergy(self, amount: float):
        """Outside enhanced state: energy above maxEnergy spills into overflowEnergy (cap 80).
        Inside enhanced state: normal cap at maxEnergy, no overflow accumulation."""
        if not self.EnhancedState:
            space = self.maxEnergy - self.currEnergy
            if amount > space:
                # Fill currEnergy to max, put the remainder into overflow
                self.currEnergy = self.maxEnergy
                self.overflowEnergy = min(80.0, self.overflowEnergy + (amount - space))
            else:
                self.currEnergy = min(self.maxEnergy, self.currEnergy + amount)
        else:
            self.currEnergy = min(self.maxEnergy, self.currEnergy + amount)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("MortenaxBladeTraceCR", StatTypes.CR_PERCENT, 0.12, self.role))
        bl.append(Buff("MortenaxBladeTraceHP", StatTypes.HP_PERCENT, 0.10, self.role))
        bl.append(Buff("MortenaxBladeTraceDMG", StatTypes.DMG_PERCENT, 0.224, self.role))
        if self.eidolon >= 2:
            bl.append(Buff("MortenaxBladeE2ULTDMG", StatTypes.DMG_PERCENT, 0.75, Role.ALL, [AtkType.ULT], 1, 1, Role.SELF, TickDown.PERM))
            bl.append(Buff("MortenaxBladeE2FUADMG", StatTypes.DMG_PERCENT, 0.75, Role.ALL, [AtkType.FUA], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e5MulReg = 0.55 if self.eidolon >= 5 else 0.5
        e5MulEnhanced = 1.1 if self.eidolon >= 5 else 1.0
        e3DefShred = 0.32 if self.eidolon >= 3 else 0.30
        e3Vul = 0.54 if self.eidolon >= 3 else 0.50
        if self.EnhancedState:
            dbl.append(Debuff("MortenaxBladeUltVul", self.role, StatTypes.VULN, e3Vul, self.bestEnemy(enemyID), [AtkType.ALL], 2,1, Targeting.SINGLE))
            dbl.append(Debuff("MortenaxBladeUltShred", self.role, StatTypes.SHRED, e3DefShred, self.bestEnemy(enemyID), [AtkType.ALL], 2,1, Targeting.SINGLE))
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e5MulEnhanced, 0], [10, 0], 20, self.scaling, 1, "MortenaxBladeEnhancedBasic"))
            self.ChargeCount += 1
            logger.debug(f"{self.name} has obtained 1 Charge. Current Charge count: {self.ChargeCount}.")
        else:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                     [e5MulReg, 0], [10, 0], 20, self.scaling, 1, "MortenaxBladeBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e5MulAoe = 0.792 if self.eidolon >= 5 else 0.72
        e5MulBounce = 0.264 if self.eidolon >= 5 else 0.24
        e3DefShred = 0.32 if self.eidolon >= 3 else 0.30
        e3Vul = 0.54 if self.eidolon >= 3 else 0.50
        if self.EnhancedState:
            if self.currHP >= 0.10*self.maxHP:
                self.currHP -= 0.10*self.maxHP
            else:
                self.currHP = 1
            if self.eidolon >= 6 and self.E6ChargeReady:
                self.ChargeCount += 1
                self.E6ChargeReady = False
                logger.debug(f"{self.name} E6: gained 1 Charge from HP consumption in Skill")
            dbl.append(Debuff("MortenaxBladeUltVul", self.role, StatTypes.VULN, e3Vul, Role.ALL, [AtkType.ALL], 2))
            dbl.append(Debuff("MortenaxBladeUltShred", self.role, StatTypes.SHRED, e3DefShred, Role.ALL, [AtkType.ALL], 2))
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.SKL], [self.element],
                           [e5MulAoe, 0], [10, 0], 30, self.scaling, 0, "MortenaxBladeAOESkill"))
            for i in range(4):
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.SKL], [self.element],
                               [e5MulBounce, 0], [5, 0], 0, self.scaling, 0, "MortenaxBladeBounceSkill"))
            self.ChargeCount += 1
            logger.debug(f"{self.name} has obtained 1 Charge. Current Charge count: {self.ChargeCount}.")
        if self.lightcone.name == "Reforged in Hellfire":
            purgatoryCD = self.lightcone.level * 0.075 + 0.225
            bl.append(Buff("MortenaxBladeCRBoost", StatTypes.CD_PERCENT, purgatoryCD, self.role, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        if self.EnhancedState == False:
            self.EnhancedState = True
            self.aggro = 200
            self.maxEnergy = 160
            self.ultCost = 160
            e3DefShred = 0.32 if self.eidolon >= 3 else 0.30
            e3Vul = 0.54 if self.eidolon >= 3 else 0.50
            e3CD = 0.66 if self.eidolon >= 3 else 0.60
            e4DMGBoost = 1.00 if self.eidolon >= 4 else 0.50
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.NA, [AtkType.ALL], [self.element],
                     [0, 0], [0, 0], 5, self.scaling, 0, "MortenaxBladeUlt"))
            dbl.append(Debuff("MortenaxBladeUltVul", self.role, StatTypes.VULN, e3Vul, Role.ALL, [AtkType.ALL], 2))
            dbl.append(Debuff("MortenaxBladeUltShred", self.role, StatTypes.SHRED, e3DefShred, Role.ALL, [AtkType.ALL], 2))
            if self.currHP >= 0.20*self.maxHP:
                self.currHP -= 0.20*self.maxHP
            else:
                self.currHP = 1
            if self.eidolon >= 6 and self.E6ChargeReady:
                self.ChargeCount += 1
                self.E6ChargeReady = False
                logger.debug(f"{self.name} E6: gained 1 Charge from HP consumption in Ult")
            bl.append(Buff("MortenaxBladeCRBoost", StatTypes.CR_PERCENT, 0.20, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
            bl.append(Buff("MortenaxBladeCDBoost", StatTypes.CD_PERCENT, e3CD, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
            bl.append(Buff("MortenaxBladeDMGReduction", StatTypes.DMG_REDUCTION, 0.50, self.role,[AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
            bl.append(Buff("MortenaxBladeDMGBoost", StatTypes.DMG_PERCENT, e4DMGBoost, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
            if self.NihilityCount >= 2:
                bl.append(Buff("MortenaxBladeULTDMG", StatTypes.DMG_PERCENT, 0.75, Role.ALL, [AtkType.ULT], 1, 1, Role.SELF,TickDown.PERM))
            else:
                bl.append(Buff("MortenaxBladeDMG", StatTypes.DMG_PERCENT, 0.75, self.role, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
            if self.eidolon >= 1:
                bl.append(Buff("MortenaxBladeE1Pen", StatTypes.PEN, 0.20, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
            if self.overflowEnergy > 0:
                self.currEnergy = min(self.maxEnergy, self.currEnergy + self.overflowEnergy)
                logger.debug(f"{self.name} transferred {self.overflowEnergy:.1f} overflow energy on Ult entry")
                self.overflowEnergy = 0.0
            # E2: reset ally ult charge counter when zone is deployed
            self.E2AllyUltChargeCount = 0
        else:
            e3EnhancedUlt = 3.78 if self.eidolon >= 3 else 3.50
            e6DMGBoost = 2.50 if self.eidolon >= 6 else 1.00
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT], [self.element],
                           [e3EnhancedUlt*e6DMGBoost, 0], [20, 0], 5, self.scaling, 0, "MortenaxBladeEnhancedUlt"))
            self.ChargeCount += 1
            logger.debug(f"{self.name} has obtained 1 Charge. Current Charge count: {self.ChargeCount}.")
        return bl, dbl, al, dl, tl, hl

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useFua(enemyID)
        e5MulAoe = 0.792 if self.eidolon >= 5 else 0.72
        e5MulBounce = 0.264 if self.eidolon >= 5 else 0.24
        e3DefShred = 0.32 if self.eidolon >= 3 else 0.30
        e3Vul = 0.54 if self.eidolon >= 3 else 0.50
        e3TalentEnergy = 27 if self.eidolon >= 3 else 25
        if self.EnhancedState:
            if self.currHP >= 0.10*self.maxHP:
                self.currHP -= 0.10*self.maxHP
            else:
                self.currHP = 1
            dbl.append(Debuff("MortenaxBladeUltVul", self.role, StatTypes.VULN, e3Vul, Role.ALL, [AtkType.ALL], 2))
            dbl.append(Debuff("MortenaxBladeUltShred", self.role, StatTypes.SHRED, e3DefShred, Role.ALL, [AtkType.ALL], 2))
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.FUA], [self.element],
                           [e5MulAoe, 0], [10, 0], e3TalentEnergy, self.scaling, 0, "MortenaxBladeAOEFUA"))
            for i in range(4):
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.FUA], [self.element],
                               [e5MulBounce, 0], [5, 0], 0, self.scaling, 0, "MortenaxBladeBounceFUA"))
            if self.eidolon >= 1:
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.NA, [AtkType.ALL], [self.element],
                         [0, 0], [0, 0], 0, self.scaling, 0, "MortenaxBladeUltDelay"))
        self.ChargeCount += 1
        logger.debug(f"{self.name} has obtained 1 Charge. Current Charge count: {self.ChargeCount}.")
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        if result.turnName == ("MortenaxBladeEnhancedBasic" or "MortenaxBladeBasic"):
            self.aggro = 10000
        elif result.turnName != ("MortenaxBladeEnhancedBasic" or "MortenaxBladeBasic") and self.EnhancedState:
            self.aggro = 200
        else:
            self.aggro = 100
        if self.eidolon >= 2:
            self.E2AllyUltChargeCount = 0
        if result.turnName == "InfiniteFury":
            self.EnhancedState = False
            if self.currEnergy >= 80:
                self.currEnergy = self.currEnergy / 2
            else:
                self.currEnergy = 40
            self.maxEnergy = 80
            self.ultCost = 80
            self.overflowEnergy = 0.0  # Clear overflow when zone is dispelled
            bl.append(Buff("MortenaxBladeCRBoost", StatTypes.CR_PERCENT, 0, self.role, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
            bl.append(Buff("MortenaxBladeCDBoost", StatTypes.CD_PERCENT, 0, self.role, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
            bl.append(Buff("MortenaxBladeDMGReduction", StatTypes.DMG_REDUCTION, 0, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
            bl.append(Buff("MortenaxBladeDMGBoost", StatTypes.DMG_PERCENT, 0, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
            if self.NihilityCount >= 2:
                bl.append(Buff("MortenaxBladeULTDMG", StatTypes.DMG_PERCENT, 0, Role.ALL, [AtkType.ULT], 1, 1, Role.SELF,TickDown.PERM))
            else:
                bl.append(Buff("MortenaxBladeDMG", StatTypes.DMG_PERCENT, 0, self.role, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
            if self.eidolon >= 1:
                bl.append(Buff("MortenaxBladeE1Pen", StatTypes.PEN, 0, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        if self.ChargeCount >= 9 and self.EnhancedState:
            self.ChargeCount -= 9
            return self.useFua(-1)
        # E6: reset charge trigger at end of every turn
        if self.eidolon >= 6 and self.EnhancedState:
            self.E6ChargeReady = True
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        e3DefShred = 0.32 if self.eidolon >= 3 else 0.30
        e3Vul = 0.54 if self.eidolon >= 3 else 0.50

        if (turn.moveName not in bonusDMG) and result.enemiesHit and result.turnDmg > 0 and self.EnhancedState:
            dbl.append(Debuff("MortenaxBladeUltVul", self.role, StatTypes.VULN, e3Vul, turn.targetID, [AtkType.ALL], 2))
            dbl.append(Debuff("MortenaxBladeUltShred", self.role, StatTypes.SHRED, e3DefShred, turn.targetID, [AtkType.ALL], 2))
            self.ChargeCount += 1
            logger.debug(f"{self.name} has obtained 1 Charge. Current Charge count: {self.ChargeCount}.")
        if self.ChargeCount >= 9 and self.EnhancedState:
            self.ChargeCount -= 9
            return self.useFua(-1)
        # E6: reset charge trigger at end of every turn
        if self.eidolon >= 6 and self.EnhancedState:
            self.E6ChargeReady = True
        return bl, dbl, al, dl, tl, hl

    def useHit(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useHit(enemyID)
        if self.EnhancedState:
            self.ChargeCount += 1
            logger.debug(f"{self.name} has obtained 1 Charge. Current Charge count: {self.ChargeCount}.")
            # E6: taking DMG also grants 1 Charge (once per turn, checked via E6ChargeReady)
            if self.eidolon >= 6 and self.E6ChargeReady:
                self.ChargeCount += 1
                logger.debug(f"{self.name} has obtained 1 Charge. Current Charge count: {self.ChargeCount}.")
                self.E6ChargeReady = False
                logger.debug(f"{self.name} E6: gained 1 Charge from taking DMG")
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.NihilityCount = specialRes.attr1
        if self.Tech:
            self.Tech = False
            tl.append(Turn(self.name, self.role, self.bestEnemy(-1), Targeting.SINGLE, [AtkType.ALL], [self.element],
                           [0, 0], [20, 0], 0, self.scaling, 0, "MortenaxBladeTech"))
            # Technique: taunt for 1 turn via aggro spike, reduce DMG taken by 90% for 2 turns
            self.aggro = 10000
            bl.append(Buff("MortenaxBladeTechDMGReduction", StatTypes.DMG_REDUCTION, 0.90, self.role,
                           [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, tl, hl

    def takeTurn(self) -> str:
        return "E" if self.EnhancedState else "A"