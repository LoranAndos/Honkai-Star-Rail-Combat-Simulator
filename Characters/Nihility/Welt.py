import logging

from Buff import *
from Character import Character
from Attributes import *
from Lightcones.Nihility.ResolutionShinesAsPearlsOfSweat import ResolutionMortenaxBlade, ResolutionWelt
from Lightcones.Nihility.LiesDanceOnTheBreeze import LiesDanceOnTheBreeze
from Planars.LushakaTheSunkenSeas import LushakaTheSunkenSeas
from RelicStats import RelicStats
from Relics.DivineQueryingMasterSmith import DivineQueryMasterSmith
from Result import *
from Turn_Text import Turn
from Delay_Text import Delay
from Healing import *
from math import floor

logger = logging.getLogger(__name__)


class Welt(Character):
    # Standard Character Settings
    name = "Welt"
    path = Path.NIHILITY
    element = Element.IMAGINARY
    scaling = Scaling.ATK
    baseHP = 1125
    baseATK = 621
    baseDEF = 509
    baseSPD = 102
    maxEnergy = 120
    currEnergy = 60
    ultCost = 120
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.ADD: 0,}  # Adjust accordingly

    # Unique Character Properties
    EHR = 0.0
    Tech = True

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else ResolutionWelt(role, 5)
        self.relic1 = r1 if r1 else DivineQueryMasterSmith(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else LushakaTheSunkenSeas(role)
        self.relicStats = subs if subs else RelicStats(12, 2, 2, 2, 2, 2, 2, 2, 4, 2, 10, 2, StatTypes.EHR_PERCENT, StatTypes.SPD,
                                                       StatTypes.DMG_PERCENT, StatTypes.ERR_PERCENT)
        self.rotation = rotation if rotation else ["E"]

        # Weightless tracking (Ult passive) — fully self-contained, no engine changes.
        self._weightlessTurns = {}   # enemyID -> turns of Weightless remaining
        self._weightlessHits = {}    # enemyID -> hits landed since that enemy's last own turn
        self._lastEnemyAV = {}       # enemyID -> last observed currAV, used to detect an enemy's turn boundary

        # Slowed tracking (Skill's -10% SPD debuff). "Slowed" for the Additional DMG
        # passive below = currently under Weightless OR under this Skill SPD debuff.
        self._skillSlowTurns = {}    # enemyID -> turns of Skill-applied Slow remaining

        # Cache of live enemies, refreshed from specialRes.enemies every AV tick
        # in handleSpecialStart. self.enemyStatus was assumed to serve this role
        # but was found empty at useUlt()-time in testing, so the Weightless kit
        # tracks its own copy instead of depending on it.
        self._enemyStatusCache = []

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("WeltTraceERS", StatTypes.ERS_PERCENT, 0.10, self.role))
        bl.append(Buff("WeltTraceEHR", StatTypes.EHR_PERCENT, 0.28, self.role))
        bl.append(Buff("WeltTraceDMG", StatTypes.DMG_PERCENT, 0.144, self.role))
        bl.append(Buff("WeltTalent1", StatTypes.ERR_T, 30, self.role))
        if self.Tech:
            self.Tech = False
            dbl.append(Debuff("WeltTechSPD", self.role, StatTypes.SPD_PERCENT, -0.10, Role.ALL, [AtkType.ALL], 1))
            dl.append(Delay("WeltTechDelay", 0.20, Role.ALL, False, True))
        return bl, dbl, al, dl, hl, sl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        e5TalentMul = 1.1 if self.eidolon >= 5 else 1.0
        targetID = self.bestEnemy(enemyID)
        tl.append(Turn(self.name, self.role, targetID, Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20, self.scaling, 1, "WeltBasic"))
        if self._isSlowed(targetID):
            tl.append(Turn(self.name, self.role, targetID, Targeting.SINGLE, [AtkType.ADD], [self.element],
                           [e5TalentMul, 0], [0, 0], 0, self.scaling, 0, "WeltSlowedAdditionalDMG"))
            if self.eidolon >= 2:
                bl.append(Buff("WeltE2Err", StatTypes.ERR_T, 3, self.role))
                logger.debug(f"Welt E2 has been Triggered")
        tl.append(Turn(self.name, self.role, targetID, Targeting.SINGLE, [AtkType.ADD], [self.element],
                       [0.8*e3Mul, 0], [0, 0], 0, self.scaling, 0, "WeltAdditionalDMG"))
        return bl, dbl, al, dl, tl, hl, sl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useSkl(enemyID)
        e3Mul = 0.792 if self.eidolon >= 3 else 0.72
        e5TalentMul = 1.1 if self.eidolon >= 5 else 1.0
        e5UltMul = 1.62 if self.eidolon >= 5 else 1.50
        targetID = self.bestEnemy(enemyID)

        # Check "already Slowed" BEFORE this Skill's own SPD debuff is applied/
        # tracked below, so this use doesn't trigger the bonus off its own Slow.
        wasSlowed = self._isSlowed(targetID)

        if wasSlowed and self.eidolon == 6:
            bl.append(Buff("WeltE6CR", StatTypes.CR_PERCENT, 0.30, self.role,[AtkType.SKL, AtkType.ULT], 1, 1, self.role, TickDown.START))
            bl.append(Buff("WeltE6CD", StatTypes.CR_PERCENT, 0.60, self.role, [AtkType.SKL, AtkType.ULT], 1, 1, self.role, TickDown.START))

        tl.append(Turn(self.name, self.role, targetID, Targeting.SINGLE, [AtkType.SKL], [self.element],
                       [e3Mul, 0], [10, 0], 6, self.scaling, -1, "WeltSkill"))
        if wasSlowed:
            tl.append(Turn(self.name, self.role, targetID, Targeting.SINGLE, [AtkType.ADD], [self.element],
                           [e5TalentMul, 0], [0, 0], 0, self.scaling, 0, "WeltSlowedAdditionalDMG"))
            if self.eidolon >= 2:
                bl.append(Buff("WeltE2Err", StatTypes.ERR_T, 3, self.role))
                logger.debug(f"Welt E2 has been Triggered")

        dbl.append(Debuff("WeltSpdDebuff", self.role, StatTypes.SPD_PERCENT, -0.10, Role.ALL, [AtkType.ALL], 2))
        for i in range(4):
            tl.append(Turn(self.name, self.role, targetID, Targeting.SINGLE, [AtkType.SKL], [self.element],
                     [e3Mul, 0], [10, 0], 6, self.scaling, 0, "WeltSkillExtra"))
            if wasSlowed:
                tl.append(Turn(self.name, self.role, targetID, Targeting.SINGLE, [AtkType.ADD], [self.element],
                               [e5TalentMul, 0], [0, 0], 0, self.scaling, 0, "WeltSlowedAdditionalDMG"))
                if self.eidolon >= 2:
                    bl.append(Buff("WeltE2Err", StatTypes.ERR_T, 3, self.role))
                    logger.debug(f"Welt E2 has been Triggered")
        tl.append(Turn(self.name, self.role, targetID, Targeting.SINGLE, [AtkType.ADD], [self.element],
                       [1.2*e3Mul, 0], [0, 0], 0, self.scaling, 0, "WeltAdditionalDMG"))

        if self.eidolon >= 1 and targetID in self._weightlessTurns:
            tl.append(Turn(self.name, self.role, targetID, Targeting.SINGLE, [AtkType.ADD], [self.element],
                           [0.4 * e5UltMul, 0], [0, 0], 0, self.scaling, 0, "WeltE1AdditionalDMG"))


        # Skill's SPD debuff hits all enemies (Role.ALL) — refresh Skill-Slow
        # tracking for every currently-known enemy to match.
        for enemy in self._enemyStatusCache:
            self._skillSlowTurns[enemy.enemyID] = 2

        return bl, dbl, al, dl, tl, hl, sl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e5Mul = 1.62 if self.eidolon >= 5 else 1.50
        e5TalentMul = 1.1 if self.eidolon >= 5 else 1.0
        E2Happened = True

        if self.eidolon == 6:
            for enemy in self._enemyStatusCache:
                if enemy.enemyID in self._weightlessTurns:
                    bl.append(Buff("WeltE6CR", StatTypes.CR_PERCENT, 0.30, self.role, [AtkType.SKL, AtkType.ULT], 1, 1,
                                   self.role, TickDown.START))
                    bl.append(Buff("WeltE6CD", StatTypes.CR_PERCENT, 0.60, self.role, [AtkType.SKL, AtkType.ULT], 1, 1,
                                   self.role, TickDown.START))
                    break

        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT], [self.element],
                       [e5Mul, 0], [20, 0], 10, self.scaling, 0, "WeltUlt"))

        dbl.append(Debuff("WeltImprisonSPD", self.role, StatTypes.SPD_PERCENT, -0.10, Role.ALL, [AtkType.ALL], 1))
        dl.append(Delay("WeltImprisonDelay", 0.12, Role.ALL, False, True))

        dbl.append(Debuff("WeltWeightlessSPD", self.role, StatTypes.SPD_PERCENT, -0.05, Role.ALL, [AtkType.ALL], 2))
        dbl.append(Debuff("WeltWeightlessShred", self.role, StatTypes.SHRED, 0.40, Role.ALL, [AtkType.ALL], 2))
        if self.eidolon >= 4:
            dbl.append(Debuff("WeltE4Pen", self.role, StatTypes.PEN, 0.30, Role.ALL, [AtkType.ALL], 2, 1))

        for enemy in self._enemyStatusCache:
            if self._isSlowed(enemy.enemyID):
                tl.append(Turn(self.name, self.role, enemy.enemyID, Targeting.SINGLE, [AtkType.ADD], [self.element],
                               [e5TalentMul, 0], [0, 0], 0, self.scaling, 0, "WeltSlowedAdditionalDMG"))
                if self.eidolon >= 2 and E2Happened == True:
                    bl.append(Buff("WeltE2Err", StatTypes.ERR_T, 3, self.role))
                    logger.debug(f"Welt E2 has been Triggered")
                    E2Happened = False

        if self.eidolon >= 1:
            for enemy in self._enemyStatusCache:
                if enemy.enemyID in self._weightlessTurns:
                    tl.append(Turn(self.name, self.role, enemy.enemyID, Targeting.SINGLE, [AtkType.ADD], [self.element],
                                   [0.4 * e5Mul, 0], [0, 0], 0, self.scaling, 0, "WeltE1AdditionalDMG"))
                    break

        # Weightless: tracked entirely on Welt himself (no engine-visible debuff
        # needed). Seed/refresh 2 turns of Weightless on every currently-known
        # enemy, resetting each one's hit counter. self._enemyStatusCache is kept
        # fresh every AV tick by handleSpecialStart (from specialRes.enemies),
        # and since that fires before this method runs on Welt's own turn, it
        # already reflects the live enemy team.
        for enemy in self._enemyStatusCache:
            self._weightlessTurns[enemy.enemyID] = 2
            self._weightlessHits[enemy.enemyID] = 0
        logger.debug(f"[WeltAllyBuff] Ult seeded weightlessTurns={dict(self._weightlessTurns)}")

        return bl, dbl, al, dl, tl, hl, sl

    def _isSlowed(self, enemyID: int) -> bool:
        """Slowed = currently under Weightless (from Ult) or under the Skill's
        SPD debuff. Both are tracked entirely on Welt himself (see useUlt/useSkl
        and the per-enemy-turn decrement in handleSpecialStart)."""
        return enemyID in self._weightlessTurns or enemyID in self._skillSlowTurns

    def _weightlessTrigger(self, turn: Turn, result: Result) -> list:
        """Return the Delay objects (0-N) produced by this Turn against enemies
        currently under Weightless. Fires from both ownTurn and allyTurn so it
        catches every attack in the sim, not just Welt's own.

        - Excludes bonusDMG moves (extra/bonus hits) per the ability text ("the
          only attacks that count").
        - Only counts Turns that actually dealt damage (turnDmg/ElationturnDMG > 0),
          so pure-break/no-damage Turns don't trigger it.
        - Uses result.enemiesHit directly, so it's correct regardless of whether
          targetID was pre-resolved (e.g. via self.bestEnemy()) or resolved later
          inside handleTurn (e.g. via findBestEnemy on a -1 target).
        - Capped at 8 triggers per enemy since that enemy's own last turn (see
          handleSpecialStart for the turn-boundary reset).
        """
        if result.turnName in bonusDMG or (result.turnDmg + result.ElationturnDMG) <= 0:
            return []

        newDelays = []
        for enemy in result.enemiesHit:
            eid = enemy.enemyID
            if eid in self._weightlessTurns and self._weightlessHits.get(eid, 0) < 8:
                self._weightlessHits[eid] = self._weightlessHits.get(eid, 0) + 1
                newDelays.append(Delay("WeltWeightlessDelay", 0.04, eid, False, True))
        return newDelays

    def _allyWeightlessDMGBuff(self, turn: Turn, result: Result) -> list:
        if (result.turnDmg + result.ElationturnDMG) <= 0:
            logger.debug("[WeltAllyBuff] skipped: no damage on this turn")
            return []
        if any(enemy.enemyID in self._weightlessTurns for enemy in result.enemiesHit):
            logger.debug("[WeltAllyBuff] TRIGGERED - granting WeltAllyWeightlessDMG")
            return [Buff("WeltAllyWeightlessDMG", StatTypes.DMG_PERCENT, 0.10, turn.charRole,
                         [AtkType.ALL], 2, 10, turn.charRole, TickDown.END)]
        logger.debug("[WeltAllyBuff] skipped: none of enemiesHit are in weightlessTurns")
        return []

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().ownTurn(turn, result)
        dl.extend(self._weightlessTrigger(turn, result))

        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result):
        logger.debug(f"[WeltAllyBuff] allyTurn() invoked for attacker={turn.charRole}, move={result.turnName}")
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)
        dl.extend(self._weightlessTrigger(turn, result))
        bl.extend(self._allyWeightlessDMGBuff(turn, result))

        return bl, dbl, al, dl, tl, hl, sl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)
        self.EHR = specialRes.attr1
        self._enemyStatusCache = specialRes.enemies or []
        bl.append(Buff("WeltTalent3ATK", StatTypes.ATK_PERCENT, min(max(floor((self.EHR-0.4)/0.1)*0.20, 0), 0.8), self.role,[AtkType.ALL], 1, 1, self.role, TickDown.PERM))

        for enemy in (specialRes.enemies or []):
            eid = enemy.enemyID
            prevAV = self._lastEnemyAV.get(eid)
            currAV = enemy.currAV
            if prevAV is not None and prevAV <= 0.01 and currAV > prevAV:
                logger.debug(f"[WeltAllyBuff] enemy turn-boundary detected for eid={eid} "
                             f"(prevAV={prevAV}, currAV={currAV}); "
                             f"weightlessTurns before={dict(self._weightlessTurns)}")
                self._weightlessHits[eid] = 0
                if eid in self._weightlessTurns:
                    self._weightlessTurns[eid] -= 1
                    if self._weightlessTurns[eid] <= 0:
                        del self._weightlessTurns[eid]
                logger.debug(f"[WeltAllyBuff] weightlessTurns after={dict(self._weightlessTurns)}")
                if eid in self._skillSlowTurns:
                    self._skillSlowTurns[eid] -= 1
                    if self._skillSlowTurns[eid] <= 0:
                        del self._skillSlowTurns[eid]
            self._lastEnemyAV[eid] = currAV

        return bl, dbl, al, dl, tl, hl, sl