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


class Pearl(Character):
    # Standard Character Settings
    name = "Pearl"
    path = Path.ELATION
    element = Element.ICE
    scaling = Scaling.DEF
    baseHP = 1203
    baseATK = 465.7
    baseDEF = 727.65
    baseSPD = 99
    maxEnergy = 180
    currEnergy = 90
    ultCost = 180
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.FUA: 0, AtkType.ADD: 0, AtkType.ELAPUNCH: 0, AtkType.ELABANGER: 0}

    # Unique Character Properties
    hasSummon = True
    AHASpdBuffAmount = 0
    TotalElationChar = 0
    ElaStat = 0
    CharDEF = 0
    Banger = 0
    ElationDPS = False
    DPSName = "Pearl"
    EnhancedUses = 0
    SpecialEnhanced = False
    tech = True
    ally1Role = 0
    ally2Role = 0
    ally3Role = 0
    ally1Proc = False
    ally2Proc = False
    ally3Proc = False


    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, targetRole=Role.DPS, rotation=None, targetPrio=Priority.DEFAULT,
                 elationParticipationID=104) -> None:
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

        # --- Talent: Certified Banger as Repellency ------------------------
        # A SEPARATE, persistent pool from the normal decaying StatTypes.BANGER
        # buffs below (BangerStartBattle/SkillBanger/UltBanger keep working
        # exactly as before, unaffected — this just also mirrors their gains
        # into a capped, non-decaying pool used to fuel Repellency).
        # "1 point of CB = 200 Repellency" — Repellency itself is never
        # stored separately, it's always derived as certifiedBanger * 200.
        self.certifiedBanger = 0.0
        self.certifiedBangerCap = 50.0
        self.repellencyPerCB = 240.0 if self.eidolon >= 4 else 200.0
        self.repellencyBlockPct = 0.65 if self.eidolon >= 4 else 0.60

    def _gainCertifiedBanger(self, amount: float):
        """Talent gain-side: mirrors a StatTypes.BANGER amount into the
        persistent, capped Repellency pool. Called by
        MainFunctions.handleCertifiedBangerAccumulation() for ANY Banger
        buff targeting Pearl's role (her own self-granted buffs included —
        not called directly from equip/useSkl/useUlt anymore, to avoid
        double-counting against that scan). Doesn't touch the normal
        decaying Banger buff at all — that's untouched and still feeds the
        existing (unrelated) Evanescia teammate-conversion system in
        MainFunctions.handleBangerConversions() at its full, uncapped value.
        """
        self.certifiedBanger = min(self.certifiedBangerCap, self.certifiedBanger + amount)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("BangerStartBattle", StatTypes.BANGER, 20, self.role, [AtkType.ALL], 2, 1, self.role, TickDown.END))
        bl.append(Buff("PearlTraceDEF", StatTypes.DEF_PERCENT, 0.225, self.role))
        bl.append(Buff("PearlTraceSPD", StatTypes.SPD, 9, self.role))
        bl.append(Buff("PearlTraceEFR", StatTypes.ERS_PERCENT, 0.10, self.role))
        bl.append(Buff("PearlTraceELA", StatTypes.ELA, 0.10, self.role))

        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 0.99 if self.eidolon >= 3 else 0.90
        e3EnhancedMul = 1.1 if self.eidolon >= 3 else 1.0
        e3ElationMul = 0.1625 if self.eidolon >= 3 else 0.15
        e3DPSElationMul = 0.66 if self.eidolon >= 3 else 0.60
        e3HealingMult = 0.088 if self.eidolon >= 3 else 0.080
        e3HealingFlat = 176 if self.eidolon >= 3 else 160
        if self.EnhancedUses != 0 and self.SpecialEnhanced:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                           Targeting.AOE, [AtkType.BSC], [self.element],
                           [e3EnhancedMul, 0], [30, 0], 30, self.scaling, 1, "PearlBasic"))
            hl.append(Healing("PearlBasicHeal", [e3HealingMult, 0], self.scaling, Role.ALL, self.role, Targeting.AOE))
            hl.append(Healing("PearlBasicHeal", [e3HealingFlat, 0], Scaling.Other, Role.ALL, self.role, Targeting.AOE))
            hl.append(Healing("PearlExtraBasicHeal", [e3HealingMult, 0], self.scaling, Role.ALL, self.role, Targeting.SINGLE))
            hl.append(Healing("PearlExtraBasicHeal", [e3HealingFlat, 0], Scaling.Other, Role.ALL, self.role,Targeting.SINGLE))
            if self.Banger >= 1:
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                               Targeting.AOE, [AtkType.ELABANGER], [self.element],
                               [e3ElationMul, 0], [0, 0], 0, Scaling.ELA, 0, "PearlELABasic"))
            tl.append(Turn(self.DPSName, self.targetRole, self.bestEnemy(enemyID),
                           Targeting.AOE, [AtkType.ELABANGER], [self.element],
                           [e3DPSElationMul, 0], [0, 0], 0, Scaling.ELA, 0, "PearlDPSELABasic"))
            self.EnhancedUses -= 1
        elif self.EnhancedUses != 0 and not self.SpecialEnhanced:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                           Targeting.AOE, [AtkType.BSC], [self.element],
                           [e3EnhancedMul, 0], [30, 0], 30, self.scaling, 1, "PearlBasic"))
            hl.append(Healing("PearlBasicHeal", [e3HealingMult, 0], self.scaling, Role.ALL, self.role, Targeting.AOE))
            hl.append(Healing("PearlBasicHeal", [e3HealingFlat, 0], Scaling.Other, Role.ALL, self.role, Targeting.AOE))
            hl.append(Healing("PearlExtraBasicHeal", [e3HealingMult, 0], self.scaling, Role.ALL, self.role, Targeting.SINGLE))
            hl.append(Healing("PearlExtraBasicHeal", [e3HealingFlat, 0], Scaling.Other, Role.ALL, self.role,Targeting.SINGLE))
            tl.append(Turn(self.DPSName, self.targetRole, self.bestEnemy(enemyID),
                           Targeting.AOE, [AtkType.ELABANGER], [self.element],
                           [e3DPSElationMul, 0], [0, 0], 0, Scaling.ELA, 0, "PearlDPSELABasic"))
            self.EnhancedUses -= 1
        else:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                           Targeting.SINGLE, [AtkType.BSC], [self.element],
                           [e3Mul, 0], [10, 0], 20, self.scaling, 1, "PearlBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e5HealingMult = 0.132 if self.eidolon >= 5 else 0.120
        e5HealingFlat = 264 if self.eidolon >= 5 else 240
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.NA, [AtkType.SKL], [self.element],
                       [0, 0], [0, 0], 30, self.scaling, -1, "PearlSkill"))
        bl.append(Buff("SkillBanger", StatTypes.BANGER, 15, self.role, [AtkType.ALL], 2, 1, self.role, TickDown.END))
        hl.append(Healing("PearlSkillHeal",[e5HealingMult,0],self.scaling,Role.ALL,self.role,Targeting.AOE))
        hl.append(Healing("PearlSkillHeal",[e5HealingFlat,0],Scaling.Other,Role.ALL,self.role,Targeting.AOE))
        hl.append(Healing("PearlExtraSkillHeal",[e5HealingMult,0],self.scaling,Role.ALL,self.role,Targeting.SINGLE))
        hl.append(Healing("PearlExtraSkillHeal",[e5HealingFlat,0],Scaling.Other,Role.ALL,self.role,Targeting.SINGLE))

        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.NA, [AtkType.ULT], [self.element],
                       [0, 0], [0, 0], 5, self.scaling, 0, "PearlUlt"))
        bl.append(Buff("UltBanger", StatTypes.BANGER, 20, self.role, [AtkType.ALL], 2, 1, self.role, TickDown.END))
        if self.TotalElationChar == 2:
            al.append(Advance("PearlUltForward", self.targetRole, 0.10))
        elif self.TotalElationChar == 3:
            al.append(Advance("PearlUltForward", self.targetRole, 0.15))
        elif self.TotalElationChar == 4:
            al.append(Advance("PearlUltForward", self.targetRole, 0.30))
            Character.PearlUlt = True

        if self.ElationDPS == True:
            self.SpecialEnhanced = True
            self.EnhancedUses = 3
        else:
            self.SpecialEnhanced = False
            self.EnhancedUses = 3

        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)

        if result.turnName == "AhaPearlGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if self.TotalElationChar == 1:
            if self.eidolon >= 5:
                e5Mul = 0.11
            elif 5 > self.eidolon >= 3:
                e5Mul = 0.105
            else:
                e5Mul = 0.10
        elif self.TotalElationChar == 2:
            if self.eidolon >= 5:
                e5Mul = 0.165
            elif 5 > self.eidolon >= 3:
                e5Mul = 0.1575
            else:
                e5Mul = 0.15
        elif self.TotalElationChar == 3:
            if self.eidolon >= 5:
                e5Mul = 0.22
            elif 5 > self.eidolon >= 3:
                e5Mul = 0.21
            else:
                e5Mul = 0.20
        elif self.TotalElationChar == 4:
            if self.eidolon >= 5:
                e5Mul = 0.44
            elif 5 > self.eidolon >= 3:
                e5Mul = 0.42
            else:
                e5Mul = 0.40
        if result.turnName == "AhaPearlGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)
        if turn.charRole == self.ally1Role and turn.moveName not in bonusDMG and result.turnDmg > 0 and self.ally1Proc == True:
            if result.atkType == AtkType.ELAPUNCH:
                tl.append(Turn(self.name, self.role, self.bestEnemy(-1),
                               turn.targeting, [AtkType.ELAPUNCH], [self.element],
                               [e5Mul, 0], [0, 0], 0, Scaling.ELA, 0, "PearlELASkillBonusDMG"))
                self.ally1Proc = False
            else:
                tl.append(Turn(self.name, self.role, self.bestEnemy(-1),
                               turn.targeting, [AtkType.ELABANGER,turn.atkType], [self.element],
                               [e5Mul, 0], [0, 0], 0, Scaling.ELA, 0, "PearlELASkillBonusDMG"))
                self.ally1Proc = False
        if turn.charRole == self.ally2Role and turn.moveName not in bonusDMG and result.turnDmg > 0 and self.ally2Proc == True:
            if result.atkType == AtkType.ELAPUNCH:
                tl.append(Turn(self.name, self.role, self.bestEnemy(-1),
                               turn.targeting, [AtkType.ELAPUNCH], [self.element],
                               [e5Mul, 0], [0, 0], 0, Scaling.ELA, 0, "PearlELASkillBonusDMG"))
                self.ally2Proc = False
            else:
                tl.append(Turn(self.name, self.role, self.bestEnemy(-1),
                               turn.targeting, [AtkType.ELABANGER,turn.atkType], [self.element],
                               [e5Mul, 0], [0, 0], 0, Scaling.ELA, 0, "PearlELASkillBonusDMG"))
                self.ally2Proc = False
        if turn.charRole == self.ally3Role and turn.moveName not in bonusDMG and result.turnDmg > 0 and self.ally3Proc == True:
            if result.atkType == AtkType.ELAPUNCH:
                tl.append(Turn(self.name, self.role, self.bestEnemy(-1),
                               turn.targeting, [AtkType.ELAPUNCH], [self.element],
                               [e5Mul, 0], [0, 0], 0, Scaling.ELA, 0, "PearlELASkillBonusDMG"))
                self.ally3Proc = False
            else:
                tl.append(Turn(self.name, self.role, self.bestEnemy(-1),
                               turn.targeting, [AtkType.ELABANGER,turn.atkType], [self.element],
                               [e5Mul, 0], [0, 0], 0, Scaling.ELA, 0, "PearlELASkillBonusDMG"))
                self.ally3Proc = False

        return bl, dbl, al, dl, tl, hl

    def useElaSkill(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useElaSkill(enemyID)
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.NA, [AtkType.ELAPUNCH], [self.element],
                       [0, 0], [0, 0], 5, self.scaling, 0, "PearlELASkill"))
        self.ally1Proc = True
        self.ally2Proc = True
        self.ally3Proc = True

        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.AHASpdBuffAmount = specialRes.attr1
        self.TotalElationChar = specialRes.attr2
        self.ElaStat = specialRes.attr3
        self.CharDEF = specialRes.attr4
        self.Banger = specialRes.attr5
        self.ElationDPS = specialRes.attr6
        self.DPSName = specialRes.attr7
        self.ally1Role = specialRes.attr8[0]
        self.ally2Role = specialRes.attr8[1]
        self.ally3Role = specialRes.attr8[2]

        bl.append(Buff("AhaSpdBuff", StatTypes.SPD, self.AHASpdBuffAmount, Role.AHA, [AtkType.SPECIAL], 1, 1, Role.AHA,
                       TickDown.START))
        bl.append(Buff("PearlDEFtoELA", StatTypes.ELA, 0.32 + min(max(floor((self.CharDEF-2400)/100)*0.03, 0), 1.08), self.role, [AtkType.ALL], 1, 1,Role.SELF, TickDown.END))

        # Talent: "When an ally target's current HP percentage is 50% or
        # lower, DMG taken is reduced by 30%." Checked live every tick
        # against each ally's actual currHP/maxHP, applied individually per
        # ally (not team-wide) — self-corrects as HP crosses the threshold
        # in either direction since it's only re-applied while the
        # condition holds; nothing refreshes it once it stops qualifying,
        # so the 1-turn buff just expires on its own.
        for ally in (Character._current_player_team or []):
            if getattr(ally, "maxHP", 0) > 0 and ally.currHP / ally.maxHP <= 0.5:
                bl.append(Buff("PearlRepellencyLowHPReduction", StatTypes.DMG_REDUCTION, 0.30, ally.role,
                               [AtkType.ALL], 1, 1, self.role, TickDown.PERM))

        if self.tech:
            self.tech = False
            bl.append(Buff("BangerTech", StatTypes.BANGER, 20, self.role, [AtkType.ALL], 2, 1, self.role,
                           TickDown.END))
            self.EnhancedUses = 2

        return bl, dbl, al, dl, tl, hl

    def takeTurn(self) -> str:
        return super().takeTurn()