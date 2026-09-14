import logging

from Buff import *
from Delay_Text import Advance
from Character import Character
from Lightcones.Elation.MushyShroomyAdventures import MushyShroomysAdventuresPearl
from Lightcones.Elation.ColorsForTomorrow import ColorsForTomorrow
from Planars.SprightlyVonwacq import SprightlyVonwacq
from RelicStats import RelicStats
from Relics.DreamlitActor import DreamlitActor
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
    Trace3Energy = True


    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, targetRole=Role.DPS, rotation=None, targetPrio=Priority.DEFAULT,
                 elationParticipationID=104) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else MushyShroomysAdventuresPearl(role, 5)
        self.relic1 = r1 if r1 else DreamlitActor(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else SprightlyVonwacq(role)
        self.relicStats = subs if subs else RelicStats(10, 2, 2, 10, 2, 2, 2, 2, 2, 2, 2, 2, StatTypes.DEF_PERCENT,
                                                       StatTypes.SPD, StatTypes.DEF_PERCENT, StatTypes.ERR_PERCENT)
        self.targetRole = targetRole
        self.rotation = rotation if rotation else ["A","A","E"]
        self.masterFoxFiredCount = 0
        self.elationParticipationID = elationParticipationID

        # Ult targeting toggle: "energy" = YaoGuang whenever she has >=90
        # Energy, else DPS. "alternate" = strictly alternates between
        # YaoGuang and DPS on every Ult use, ignoring energy entirely.
        # "dps" = always targets DPS, ignoring YaoGuang entirely. Set
        # directly on the instance at team-construction time, e.g.
        # `pearl.ultTargetMode = "dps"`.
        self.ultTargetMode = "dps"
        # Alternation state: which target Ult used LAST time, so the next
        # Ult flips to the other one. Starts False so the very first Ult
        # in "alternate" mode goes to YaoGuang (mirrors "energy" mode's
        # default preference for her when nothing else has happened yet).
        self._lastUltTargetedYaoGuang = False
        # Raw ingredients cached fresh every tick by handleSpecialStart
        # (from handleSpec's "Pearl" case) — the actual decision is made
        # once per real Ult use in useUlt(), not every tick, since
        # alternation needs to flip exactly once per Ult rather than
        # potentially several times before she gets to act.
        self._yaoguangRole = None
        self._yaoguangEnergyOK = False
        self._dpsRole = Role.DPS

        # --- Talent: Certified Banger as Repellency ------------------------
        # A SEPARATE, persistent pool tracked as a single, never-expiring
        # StatTypes.BANGER Buff ("PearlCertifiedBanger", re-synced to
        # self.certifiedBanger's current value every time it changes) —
        # NOT a family of independently-decaying buffs. Every gain source
        # (equip's start-of-battle, useSkl, useUlt, the ally-turn-begins
        # Talent trigger, and any external source like Aha's summon buffs)
        # feeds into this ONE value instead of creating its own buff, so
        # there's never a separate object that can "expire" out from under
        # her and wrongly trigger Evanescia's expiry-side conversion for
        # CB that didn't actually leave Pearl's pool.
        # "1 point of CB = 200 Repellency" — Repellency itself is never
        # stored separately, it's always derived as certifiedBanger * 200.
        self.certifiedBanger = 0.0
        self.certifiedBangerCap = 50.0
        self.repellencyPerCB = 200.0
        self.repellencyBlockPct = 0.60

        # Talent: "When an ally target's turn begins, Pearl gains 5 CB, up
        # to a max of 50. The obtainable amount of CB resets at the start
        # of Pearl's turn." A SEPARATE per-cycle gain budget from the
        # certifiedBanger total above — assumed to mirror the 50-point cap
        # since the ability text doesn't give it its own number. Refilled
        # in _onOwnTurnBegins_Repellency(), spent in
        # _onAllyTurnBegins_Repellency() — both called from
        # Character.takeTurn().
        self.cbObtainableThisCycle = self.certifiedBangerCap

        # Buffer for the ally-turn-start gain: takeTurn() has no channel
        # back into buffList, so it can't call _addCertifiedBanger()
        # directly. It just accumulates the intended amount here;
        # handleSpecialStart (which DOES return a proper bl) applies it
        # on the next tick.
        self._pendingCBGain = 0.0

    def _addCertifiedBanger(self, amount: float, source: str, bl: list, notifyEvanescia: bool = True):
        """Central Talent gain-path for ALL of Pearl's own CB sources
        (equip/useSkl/useUlt/ally-turn-trigger). Credits self.certifiedBanger
        (capped), grants Evanescia her gain-side yoink DIRECTLY via
        receiveBangerFromTeammate — bypassing MainFunctions.handleBangerConversions'
        generic buffList scan, since that's built around one-shot buffs
        getting flagged once, not a single value that changes repeatedly —
        then re-syncs the single persistent stat buff.

        notifyEvanescia=False preserves BangerStartBattle's pre-existing
        behavior: MainFunctions.handleBangerConversions/handleBangerExpiry
        already explicitly excluded "BangerStartBattle" by name from
        Evanescia's conversions before any of this Talent existed, so
        routing it through here shouldn't newly start granting her a share.
        """
        room = self.certifiedBangerCap - self.certifiedBanger
        gain = max(0.0, min(amount, room))
        if gain <= 0:
            return
        self.certifiedBanger += gain

        if notifyEvanescia:
            evanescia = next((c for c in (Character._current_player_team or []) if c.name == "Evanescia"), None)
            if evanescia:
                evanescia.receiveBangerFromTeammate(gain, source, bl)

        self._syncCertifiedBangerBuff(bl)

    def _syncCertifiedBangerBuff(self, bl: list):
        """Re-emits the single, never-expiring 'PearlCertifiedBanger' buff
        at Pearl's CURRENT total. Same-name/target reuse means addBuffs
        overwrites its .val in place rather than creating a separate
        stacking buff (same pattern as WeltTalent3ATK's continuous-refresh
        buffs) — so this is the only Banger-type buff Pearl carries at any
        given moment, matching 'certain Elation damage scales off CB'
        against her true total rather than a fragmented multi-buff sum."""
        bl.append(Buff("PearlCertifiedBanger", StatTypes.BANGER, self.certifiedBanger, self.role,
                       [AtkType.ALL], 1, 1, self.role, TickDown.PERM))

    def _onOwnTurnBegins_Repellency(self):
        """Talent: 'The obtainable amount of Certified Banger resets at
        the start of Pearl's turn.' Called from Character.takeTurn() when
        it's Pearl's own turn starting."""
        self.cbObtainableThisCycle = self.certifiedBangerCap

    def _onAllyTurnBegins_Repellency(self):
        """Talent: 'When an ally target's turn begins, Pearl gains 5
        point(s) of Certified Banger, up to a max of 50.' Called from
        Character.takeTurn() when it's any OTHER character's turn
        starting. The actual gain is the smallest of: the flat 5, the
        remaining room in this cycle's obtainable budget, and the
        remaining room under her absolute 50-point pool cap — checked
        against certifiedBanger + any not-yet-applied pending amount, so
        several ally turns beginning before the next handleSpecialStart
        tick can't over-grant past the cap. Only records intent here;
        handleSpecialStart applies it via _addCertifiedBanger()."""
        effectiveTotal = self.certifiedBanger + self._pendingCBGain
        gain = min(5, self.cbObtainableThisCycle, self.certifiedBangerCap - effectiveTotal)
        if gain > 0:
            self._pendingCBGain += gain
            self.cbObtainableThisCycle -= gain
            logger.info(f"BANGER > {self.name} will gain {gain:.1f} Certified Banger from an ally turn beginning "
                       f"(pending: {self._pendingCBGain:.1f}, "
                       f"{self.cbObtainableThisCycle:.1f} obtainable remaining this cycle)")

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        self._addCertifiedBanger(20, "BangerStartBattle", bl, notifyEvanescia=False)
        bl.append(Buff("PearlTraceDEF", StatTypes.DEF_PERCENT, 0.225, self.role))
        bl.append(Buff("PearlTraceSPD", StatTypes.SPD, 9, self.role))
        bl.append(Buff("PearlTraceEFR", StatTypes.ERS_PERCENT, 0.10, self.role))
        bl.append(Buff("PearlTraceELA", StatTypes.ELA, 0.10, self.role))
        if self.eidolon >= 2:
            bl.append(Buff("PearlE2Merry", StatTypes.MERRY, 0.15, Role.ALL))

        return bl, dbl, al, dl, hl, sl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useBsc(enemyID)
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
            if self.eidolon == 6:
                tl.append(Turn(self.DPSName, self.targetRole, self.bestEnemy(enemyID),
                               Targeting.AOE, [AtkType.ELABANGER], [self.element],
                               [2.40, 0], [0, 0], 0, Scaling.ELA, 0, "PearlDPSE6ELABasic"))
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
                           Targeting.SINGLE, [AtkType.ELABANGER], [self.element],
                           [e3DPSElationMul, 0], [0, 0], 0, Scaling.ELA, 0, "PearlDPSELABasic"))
            if self.eidolon == 6:
                tl.append(Turn(self.DPSName, self.targetRole, self.bestEnemy(enemyID),
                               Targeting.AOE, [AtkType.ELABANGER], [self.element],
                               [2.40, 0], [0, 0], 0, Scaling.ELA, 0, "PearlDPSE6ELABasic"))
            self.EnhancedUses -= 1
        else:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                           Targeting.AOE, [AtkType.BSC], [self.element],
                           [e3Mul, 0], [10, 0], 20, self.scaling, 1, "PearlBasic"))
        return bl, dbl, al, dl, tl, hl, sl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useSkl(enemyID)
        e5HealingMult = 0.132 if self.eidolon >= 5 else 0.120
        e5HealingFlat = 264 if self.eidolon >= 5 else 240
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.NA, [AtkType.SKL], [self.element],
                       [0, 0], [0, 0], 30, self.scaling, -1, "PearlSkill"))
        self._addCertifiedBanger(15, "SkillBanger", bl)
        hl.append(Healing("PearlSkillHeal",[e5HealingMult,0],self.scaling,Role.ALL,self.role,Targeting.AOE))
        hl.append(Healing("PearlSkillHeal",[e5HealingFlat,0],Scaling.Other,Role.ALL,self.role,Targeting.AOE))
        hl.append(Healing("PearlExtraSkillHeal",[e5HealingMult,0],self.scaling,Role.ALL,self.role,Targeting.SINGLE))
        hl.append(Healing("PearlExtraSkillHeal",[e5HealingFlat,0],Scaling.Other,Role.ALL,self.role,Targeting.SINGLE))

        return bl, dbl, al, dl, tl, hl, sl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost

        # Ult targeting decision — made once here (not every tick), since
        # "alternate" mode needs to flip exactly once per real Ult use.
        if self.ultTargetMode == "alternate":
            if self._lastUltTargetedYaoGuang or self._yaoguangRole is None:
                self.targetRole = self._dpsRole
                self._lastUltTargetedYaoGuang = False
            else:
                self.targetRole = self._yaoguangRole
                self._lastUltTargetedYaoGuang = True
        elif self.ultTargetMode == "dps":
            self.targetRole = self._dpsRole
            self._lastUltTargetedYaoGuang = False
        else:  # "energy" mode
            if self._yaoguangRole is not None and self._yaoguangEnergyOK:
                self.targetRole = self._yaoguangRole
                self._lastUltTargetedYaoGuang = True
            else:
                self.targetRole = self._dpsRole
                self._lastUltTargetedYaoGuang = False

        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.NA, [AtkType.ULT], [self.element],
                       [0, 0], [0, 0], 5, self.scaling, 0, "PearlUlt"))
        self._addCertifiedBanger(20, "UltBanger", bl)
        if self.TotalElationChar == 2:
            if self.eidolon >= 2:
                al.append(Advance("PearlUltAlly1Forward", self.ally1Role, 0.10))
                al.append(Advance("PearlUltAlly2Forward", self.ally2Role, 0.10))
                al.append(Advance("PearlUltAlly2Forward", self.ally3Role, 0.10))
            else:
                al.append(Advance("PearlUltForward", self.targetRole, 0.10))
        elif self.TotalElationChar == 3:
            if self.eidolon >= 2:
                al.append(Advance("PearlUltAlly1Forward", self.ally1Role, 0.15))
                al.append(Advance("PearlUltAlly2Forward", self.ally2Role, 0.15))
                al.append(Advance("PearlUltAlly2Forward", self.ally3Role, 0.15))
            else:
                al.append(Advance("PearlUltForward", self.targetRole, 0.15))
        elif self.TotalElationChar >= 4:
            if self.eidolon >= 2:
                al.append(Advance("PearlUltAlly1Forward", self.ally1Role, 0.30))
                al.append(Advance("PearlUltAlly2Forward", self.ally2Role, 0.30))
                al.append(Advance("PearlUltAlly2Forward", self.ally3Role, 0.30))
            else:
                al.append(Advance("PearlUltForward", self.targetRole, 0.30))
            Character.PearlUlt = True
            if self.eidolon >= 2:
                Character.PearlE2Modifier = 2.0
            # Marker turn (0 DMG) so ElationMC/etc. can react to
            # Character.PearlUlt via result.turnName == "PearlUltimate" —
            # this was missing entirely, which is why the extra-turn
            # trigger wasn't firing for anyone regardless of the
            # Role.DPS -> pearl.targetRole change. Appended AFTER
            # self.targetRole is finalized above, so anything checking
            # pearl.targetRole in reaction to this marker sees the
            # correct, already-decided target.
            tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ALL], [self.element],
                           [0, 0], [0, 0], 0, self.scaling, 0, "PearlUltimate"))

        if self.ElationDPS == True:
            self.SpecialEnhanced = True
            self.EnhancedUses = 3
        else:
            self.SpecialEnhanced = False
            self.EnhancedUses = 3

        if self.ElationDPS:
            self.Trace3Energy = True

        return bl, dbl, al, dl, tl, hl, sl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().ownTurn(turn, result)

        if result.turnName == "AhaPearlGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)
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
        elif self.TotalElationChar >= 4:
            if self.eidolon >= 5:
                e5Mul = 0.44
            elif 5 > self.eidolon >= 3:
                e5Mul = 0.42
            else:
                e5Mul = 0.40
        e4ExtraMul = 2.0 if self.eidolon >= 4 else 1.0
        if result.turnName == "AhaPearlGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        # Diagnostic: log every damaging, non-bonus Turn from any of the 3
        # tracked ally roles, regardless of whether it ends up matching
        # anything below, so we can see exactly what's reaching this point.
        if turn.moveName not in bonusDMG and result.turnDmg > 0 and turn.charRole in (self.ally1Role, self.ally2Role, self.ally3Role):
            logger.debug(f"[PearlELABonus] saw {turn.charRole} moveName={turn.moveName} "
                        f"inElationSkillList={turn.moveName in ElationSkillList} "
                        f"ally1Role={self.ally1Role}(proc={self.ally1Proc}) "
                        f"ally2Role={self.ally2Role}(proc={self.ally2Proc}) "
                        f"ally3Role={self.ally3Role}(proc={self.ally3Proc})")

        if turn.charRole == self.ally1Role and (turn.moveName not in bonusDMG) and result.enemiesHit and result.turnDmg > 0 and self.ally1Proc == True or (turn.moveName in ElationSkillList and turn.moveName != "SilverWolf999NormalELASkill" and turn.charRole == self.ally1Role and self.ally1Proc == True):
            ally1Char = next((c for c in (Character._current_player_team or []) if c.role == self.ally1Role), None)
            ally1IsSilverWolf = ally1Char is not None and ally1Char.name == "SilverWolf999"
            if turn.moveName in ElationSkillList and turn.moveName != "SilverWolf999NormalELASkill":
                # This IS the ally's own chain-triggered Elation Skill —
                # "their next attack" per the ability text. Consume now.
                tl.append(Turn(turn.charName, turn.charRole, self.bestEnemy(-1),
                               turn.targeting, [AtkType.ELAPUNCH], turn.element,
                               [e5Mul*e4ExtraMul, 0], [0, 0], 0, Scaling.ELA, 0, "PearlELASkillBonusDMG"))
                logger.debug("[PearlELABonus] FIRED ELAPUNCH bonus for ally1")
                self.ally1Proc = False
            elif ally1IsSilverWolf:
                # SilverWolf999's own Elation Skill deals 0 DMG (never
                # satisfies result.turnDmg > 0 above), so per her
                # exception this consumes on her next real damaging turn
                # instead of waiting for an Elation Skill that can't fire.
                tl.append(Turn(turn.charName, turn.charRole, self.bestEnemy(-1),
                               turn.targeting, [AtkType.ELABANGER], turn.element,
                               [e5Mul*e4ExtraMul, 0], [0, 0], 0, Scaling.ELA, 0, "PearlELASkillBonusDMG"))
                logger.debug("[PearlELABonus] FIRED ELABANGER bonus for ally1")
                self.ally1Proc = False
            # else: this is the ally's real action, processed before their
            # own Elation Skill chain-fires this same cycle — leave
            # ally1Proc == True so it's still armed for their actual
            # Elation Skill Turn right after, instead of getting consumed
            # early by whatever they did to trigger it.
        if turn.charRole == self.ally2Role and (turn.moveName not in bonusDMG) and result.enemiesHit and result.turnDmg > 0 and self.ally2Proc == True or (turn.moveName in ElationSkillList and turn.moveName != "SilverWolf999NormalELASkill" and turn.charRole == self.ally2Role and self.ally2Proc == True):
            ally2Char = next((c for c in (Character._current_player_team or []) if c.role == self.ally2Role), None)
            ally2IsSilverWolf = ally2Char is not None and ally2Char.name == "SilverWolf999"
            if turn.moveName in ElationSkillList and turn.moveName != "SilverWolf999NormalELASkill":
                tl.append(Turn(turn.charName, turn.charRole, self.bestEnemy(-1),
                               turn.targeting, [AtkType.ELAPUNCH], turn.element,
                               [e5Mul*e4ExtraMul, 0], [0, 0], 0, Scaling.ELA, 0, "PearlELASkillBonusDMG"))
                logger.debug("[PearlELABonus] FIRED ELAPUNCH bonus for ally2")
                self.ally2Proc = False
            elif ally2IsSilverWolf:
                tl.append(Turn(turn.charName, turn.charRole, self.bestEnemy(-1),
                               turn.targeting, [AtkType.ELABANGER], turn.element,
                               [e5Mul*e4ExtraMul, 0], [0, 0], 0, Scaling.ELA, 0, "PearlELASkillBonusDMG"))
                logger.debug("[PearlELABonus] FIRED ELABANGER bonus for ally2")
                self.ally2Proc = False
        if turn.charRole == self.ally3Role and (turn.moveName not in bonusDMG) and result.enemiesHit and result.turnDmg > 0 and self.ally3Proc == True or (turn.moveName in ElationSkillList and turn.moveName != "SilverWolf999NormalELASkill" and turn.charRole == self.ally3Role and self.ally3Proc == True):
            ally3Char = next((c for c in (Character._current_player_team or []) if c.role == self.ally3Role), None)
            ally3IsSilverWolf = ally3Char is not None and ally3Char.name == "SilverWolf999"
            if turn.moveName in ElationSkillList and turn.moveName != "SilverWolf999NormalELASkill":
                tl.append(Turn(turn.charName, turn.charRole, self.bestEnemy(-1),
                               turn.targeting, [AtkType.ELAPUNCH], turn.element,
                               [e5Mul*e4ExtraMul, 0], [0, 0], 0, Scaling.ELA, 0, "PearlELASkillBonusDMG"))
                logger.debug("[PearlELABonus] FIRED ELAPUNCH bonus for ally3")
                self.ally3Proc = False
            elif ally3IsSilverWolf:
                tl.append(Turn(turn.charName, turn.charRole, self.bestEnemy(-1),
                               turn.targeting, [AtkType.ELABANGER], turn.element,
                               [e5Mul*e4ExtraMul, 0], [0, 0], 0, Scaling.ELA, 0, "PearlELASkillBonusDMG"))
                logger.debug("[PearlELABonus] FIRED ELABANGER bonus for ally3")
                self.ally3Proc = False
        if turn.charRole == self.targetRole and self.Trace3Energy and turn.moveName in UltimateList and self.ElationDPS:
            self.Trace3Energy = False
            bl.append(Buff("PearlTrace3ERR", StatTypes.ERR_F,90, self.role,[AtkType.ALL], 1, 1, Role.SELF, TickDown.END))

        return bl, dbl, al, dl, tl, hl, sl

    def useElaSkill(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useElaSkill(enemyID)
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.NA, [AtkType.ELAPUNCH], [self.element],
                       [0, 0], [0, 0], 5, self.scaling, 0, "PearlELASkill"))
        self.ally1Proc = True
        self.ally2Proc = True
        self.ally3Proc = True
        logger.debug(f"[PearlELABonus] useElaSkill() fired — armed ally1Proc/2/3=True "
                    f"(roles: {self.ally1Role}, {self.ally2Role}, {self.ally3Role})")

        return bl, dbl, al, dl, tl, hl, sl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)
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
        e5Mul = 0.33 if self.eidolon >= 5 else 0.30

        # Cache the raw ingredients every tick — the actual targeting
        # decision (mode-dependent) is made once per real Ult use in
        # useUlt(), not here, so alternation only flips once per Ult
        # rather than every tick before she gets to act.
        self._yaoguangRole = specialRes.attr9
        self._yaoguangEnergyOK = specialRes.attr10
        self._dpsRole = specialRes.attr11

        bl.append(Buff("AhaSpdBuff", StatTypes.SPD, self.AHASpdBuffAmount, Role.AHA, [AtkType.SPECIAL], 1, 1, Role.AHA,
                       TickDown.START))
        bl.append(Buff("PearlDEFtoELA", StatTypes.ELA, 0.32 + min(max(floor((self.CharDEF-2400)/100)*0.03, 0), 1.08), self.role, [AtkType.ALL], 1, 1,Role.SELF, TickDown.PERM))
        bl.append(Buff("PearlELAtoOGH", StatTypes.OGH_PERCENT, 0.2*self.ElaStat, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        if self.Banger >= 1:
           bl.append(Buff("PearlERS", StatTypes.ERS_PERCENT, 0.50, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))

        if self.eidolon >= 1:
            if self.TotalElationChar == 2:
                bl.append(Buff("PearlE1ELA", StatTypes.ELA, 0.1, Role.ALL,[AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
            elif self.TotalElationChar == 3:
                bl.append(Buff("PearlE1ELA", StatTypes.ELA, 0.2, Role.ALL,[AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
            elif self.TotalElationChar >= 4:
                bl.append(Buff("PearlE1ELA", StatTypes.ELA, 0.6, Role.ALL,[AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))

        if self.eidolon >= 6 and self.EnhancedUses != 0:
            bl.append(Buff("PearlE6PEN", StatTypes.PEN, 0.20, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        else:
            bl.append(Buff("PearlE6PEN", StatTypes.PEN, 0.0, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))


        # Talent: apply the ally-turn-start CB gain accumulated in
        # _onAllyTurnBegins_Repellency() via takeTurn() — routed through
        # the same central helper as every other CB source, so Evanescia
        # gets her normal gain-side share and the single persistent stat
        # buff reflects it.
        if self._pendingCBGain > 0:
            pending = self._pendingCBGain
            self._pendingCBGain = 0.0
            self._addCertifiedBanger(pending, "AllyTurnBegins", bl)

        # Unconditional re-sync every tick (not just on a fresh gain),
        # matching WeltTalent3ATK's continuous-refresh pattern, so
        # "PearlCertifiedBanger" never has a chance to lapse on a tick
        # where nothing else happened to trigger a gain.
        self._syncCertifiedBangerBuff(bl)

        # Talent: "When an ally target's current HP percentage is 50% or
        # lower, DMG taken is reduced by 30%." Checked live every tick
        # against each ally's actual currHP/maxHP, applied individually per
        # ally (not team-wide) — self-corrects as HP crosses the threshold
        # in either direction since it's only re-applied while the
        # condition holds; nothing refreshes it once it stops qualifying,
        # so the 1-turn buff just expires on its own.
        for ally in (Character._current_player_team or []):
            if getattr(ally, "maxHP", 0) > 0 and ally.currHP / ally.maxHP <= 0.5:
                bl.append(Buff("PearlRepellencyLowHPReduction", StatTypes.DMG_REDUCTION, e5Mul, ally.role,
                               [AtkType.ALL], 1, 1, self.role, TickDown.PERM))

        if self.tech:
            self.tech = False
            self._addCertifiedBanger(20, "TechBanger", bl)
            self.EnhancedUses = 2

        return bl, dbl, al, dl, tl, hl, sl