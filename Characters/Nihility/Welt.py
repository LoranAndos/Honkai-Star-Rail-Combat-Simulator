import logging

from Buff import *
from Character import Character
from Attributes import *
from Lightcones.Nihility.ResolutionShinesAsPearlsOfSweat import ResolutionMortenaxBlade
from Lightcones.Nihility.LiesDanceOnTheBreeze import LiesDanceOnTheBreeze
from Planars.LushakaTheSunkenSeas import LushakaTheSunkenSeas
from RelicStats import RelicStats
from Relics.PioneerDiverOfDeadWaters import PioneerCipher
from Result import *
from Turn_Text import Turn
from Delay_Text import Delay
from Healing import *

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

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else ResolutionMortenaxBlade(role, 5)
        self.relic1 = r1 if r1 else PioneerCipher(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else LushakaTheSunkenSeas(role)
        self.relicStats = subs if subs else RelicStats(12, 2, 2, 2, 2, 2, 2, 2, 4, 2, 10, 2, StatTypes.EHR_PERCENT, StatTypes.SPD,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["E"]

        # Weightless tracking (Ult passive) — fully self-contained, no engine changes.
        self._weightlessTurns = {}   # enemyID -> turns of Weightless remaining
        self._weightlessHits = {}    # enemyID -> hits landed since that enemy's last own turn
        self._lastEnemyAV = {}       # enemyID -> last observed currAV, used to detect an enemy's turn boundary

        # Slowed tracking (Skill's -10% SPD debuff). "Slowed" for the Additional DMG
        # passive below = currently under Weightless OR under this Skill SPD debuff.
        self._skillSlowTurns = {}    # enemyID -> turns of Skill-applied Slow remaining

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("WeltTraceERS", StatTypes.ERS_PERCENT, 0.10, self.role))
        bl.append(Buff("WeltTraceEHR", StatTypes.EHR_PERCENT, 0.28, self.role))
        bl.append(Buff("WeltTraceDMG", StatTypes.DMG_PERCENT, 0.144, self.role))
        dbl.append(Debuff("WeltTechImprisonSPD", self.role, StatTypes.SPD_PERCENT, -0.10, Role.ALL, [AtkType.ALL], 1))
        dl.append(Delay("WeltTechImprisonDelay", 0.20, Role.ALL, False, True))

        return bl, dbl, al, dl, hl, sl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        e5TalentMul = 1.1 if self.eidolon >= 5 else 1.0
        targetID = self.bestEnemy(enemyID)
        tl.append(Turn(self.name, self.role, targetID, Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20, self.scaling, 1, "WeltBasic"))

        # Passive: attacking an already-Slowed enemy additionally deals Imaginary
        # Additional DMG equal to 100% of Welt's ATK. Triggers once per attack
        # action (not once per individual multi-hit) — see useSkl for the same.
        if self._isSlowed(targetID):
            tl.append(Turn(self.name, self.role, targetID, Targeting.SINGLE, [AtkType.ADD], [self.element],
                           [e5TalentMul, 0], [0, 0], 0, self.scaling, 0, "WeltSlowedAdditionalDMG"))
        return bl, dbl, al, dl, tl, hl, sl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useSkl(enemyID)
        e3Mul = 0.792 if self.eidolon >= 3 else 0.72
        e5TalentMul = 1.1 if self.eidolon >= 5 else 1.0
        targetID = self.bestEnemy(enemyID)

        # Check "already Slowed" BEFORE this Skill's own SPD debuff is applied/
        # tracked below, so this use doesn't trigger the bonus off its own Slow.
        wasSlowed = self._isSlowed(targetID)

        tl.append(Turn(self.name, self.role, targetID, Targeting.SINGLE, [AtkType.SKL], [self.element],
                       [e3Mul, 0], [10, 0], 6, self.scaling, -1, "WeltSkill"))
        if wasSlowed:
            tl.append(Turn(self.name, self.role, targetID, Targeting.SINGLE, [AtkType.ADD], [self.element],
                           [e5TalentMul, 0], [0, 0], 0, self.scaling, 0, "WeltSlowedAdditionalDMG"))
        dbl.append(Debuff("WeltSpdDebuff", self.role, StatTypes.SPD_PERCENT, -0.10, Role.ALL, [AtkType.ALL], 2))
        for i in range(4):
            tl.append(Turn(self.name, self.role, targetID, Targeting.SINGLE, [AtkType.SKL], [self.element],
                     [e3Mul, 0], [10, 0], 6, self.scaling, 0, "WeltSkillExtra"))
            if wasSlowed:
                tl.append(Turn(self.name, self.role, targetID, Targeting.SINGLE, [AtkType.ADD], [self.element],
                               [e5TalentMul, 0], [0, 0], 0, self.scaling, 0, "WeltSlowedAdditionalDMG"))

        # Skill's SPD debuff hits all enemies (Role.ALL) — refresh Skill-Slow
        # tracking for every currently-known enemy to match.
        for enemy in (self.enemyStatus or []):
            self._skillSlowTurns[enemy.enemyID] = 2

        return bl, dbl, al, dl, tl, hl, sl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e5Mul = 1.62 if self.eidolon >= 5 else 1.50
        e5TalentMul = 1.1 if self.eidolon >= 5 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT], [self.element],
                       [e5Mul, 0], [20, 0], 5, self.scaling, 0, "WeltUlt"))

        dbl.append(Debuff("WeltImprisonSPD", self.role, StatTypes.SPD_PERCENT, -0.10, Role.ALL, [AtkType.ALL], 1))
        dl.append(Delay("WeltImprisonDelay", 0.12, Role.ALL, False, True))

        dbl.append(Debuff("WeltWeightlessSPD", self.role, StatTypes.SPD_PERCENT, -0.05, Role.ALL, [AtkType.ALL], 2))
        dbl.append(Debuff("WeltWeightlessShred", self.role, StatTypes.SHRED, 0.40, Role.ALL, [AtkType.ALL], 2))

        # Passive: attacking an already-Slowed enemy additionally deals Imaginary
        # Additional DMG equal to 100% of Welt's ATK. Checked per-enemy BEFORE the
        # Weightless seeding below, so an enemy isn't considered "already Slowed"
        # purely because of the Weightless this same Ult is about to apply.
        for enemy in (self.enemyStatus or []):
            if self._isSlowed(enemy.enemyID):
                tl.append(Turn(self.name, self.role, enemy.enemyID, Targeting.SINGLE, [AtkType.ADD], [self.element],
                               [e5TalentMul, 0], [0, 0], 0, self.scaling, 0, "WeltSlowedAdditionalDMG"))

        # Weightless: tracked entirely on Welt himself (no engine-visible debuff
        # needed). Seed/refresh 2 turns of Weightless on every currently-known
        # enemy, resetting each one's hit counter. self.enemyStatus is kept fresh
        # every AV tick by handleSpecialStart, and since that fires before this
        # method runs on Welt's own turn, it already reflects the live enemy team.
        for enemy in (self.enemyStatus or []):
            self._weightlessTurns[enemy.enemyID] = 2
            self._weightlessHits[enemy.enemyID] = 0

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

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().ownTurn(turn, result)
        dl.extend(self._weightlessTrigger(turn, result))

        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)
        dl.extend(self._weightlessTrigger(turn, result))


        return bl, dbl, al, dl, tl, hl, sl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)

        for enemy in (specialRes.enemies or []):
            eid = enemy.enemyID
            prevAV = self._lastEnemyAV.get(eid)
            currAV = enemy.currAV
            if prevAV is not None and prevAV <= 0.01 and currAV > prevAV:
                self._weightlessHits[eid] = 0
                if eid in self._weightlessTurns:
                    self._weightlessTurns[eid] -= 1
                    if self._weightlessTurns[eid] <= 0:
                        del self._weightlessTurns[eid]
                if eid in self._skillSlowTurns:
                    self._skillSlowTurns[eid] -= 1
                    if self._skillSlowTurns[eid] <= 0:
                        del self._skillSlowTurns[eid]
            self._lastEnemyAV[eid] = currAV

        return bl, dbl, al, dl, tl, hl, sl