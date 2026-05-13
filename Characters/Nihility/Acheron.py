import logging

from Buff import *
from Character import Character
from Lightcones.Nihility.AlongThePassingShore import AlongThePassingShore
from Planars.IzumoGenseiAndTakamaDivineRealm import IzumoGenseiAndTakamaDivineRealm
from RelicStats import RelicStats
from Relics.PioneerDiverOfDeadWaters import PioneerAcheron
from Result import *
from Turn_Text import Turn
from Healing import *

logger = logging.getLogger(__name__)


class Acheron(Character):
    # Standard Character Settings
    name = "Acheron"
    path = Path.NIHILITY
    element = Element.LIGHTNING
    scaling = Scaling.ATK
    baseHP = 1125
    baseATK = 699
    baseDEF = 437
    baseSPD = 101
    maxEnergy = 9
    currEnergy = 5
    ultCost = 9
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0}

    # Unique Character Properties
    specialEnergy = True
    NihilityBoost = 1.00
    ultActive = False      # blocks Crimson Knot application during Ultimate
    QuadrivalentStacks = 0 # Quadrivalent Ascendance stacks (max 3)
    Tech = True

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else AlongThePassingShore(role, 1)
        self.relic1 = r1 if r1 else PioneerAcheron(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else IzumoGenseiAndTakamaDivineRealm(role, True)
        self.relicStats = subs if subs else RelicStats(2, 2, 7, 2, 2, 2, 2, 2, 2, 2, 12, 8, StatTypes.CR_PERCENT, StatTypes.ATK_PERCENT,
                                                       StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["E"]
        self.crimsonKnot: dict[int, int] = {}
        self.QuadrivalentStacks = 0
        self.ultActive = False

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("AcheronTraceCD", StatTypes.CD_PERCENT, 0.24, self.role))
        bl.append(Buff("AcheronTraceATK", StatTypes.ATK_PERCENT, 0.28, self.role))
        bl.append(Buff("AcheronTraceDMG", StatTypes.DMG_PERCENT, 0.08, self.role))
        if self.eidolon >= 1:
            bl.append(Buff("AcheronE1CR", StatTypes.CR_PERCENT, 0.18, self.role))
        if self.eidolon >= 4:
            dbl.append(Debuff("AcheronE4Vul", self.role, StatTypes.VULN, 0.08, Role.ALL, [AtkType.ULT], 1000))
        if self.eidolon >= 6:
            bl.append(Buff("AcheronE6UltPen", StatTypes.PEN, 0.20, self.role, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl

    # ---------------------------------------------------------------------------
    # Crimson Knot helpers
    # ---------------------------------------------------------------------------

    def _knotTarget(self) -> int:
        """Return the enemyID with the most Crimson Knot stacks.
        Falls back to the first known enemy if no stacks exist yet."""
        if not self.crimsonKnot:
            return list(self.enemyStatus)[0].enemyID if self.enemyStatus else 0
        return max(self.crimsonKnot, key=lambda k: self.crimsonKnot[k])

    def _addKnot(self, enemyID: int):
        if self.ultActive:
            return  # Crimson Knot cannot be applied during Ultimate
        totalKnots = sum(self.crimsonKnot.values())
        if totalKnots >= 9:
            return  # global cap reached
        self.crimsonKnot[enemyID] = self.crimsonKnot.get(enemyID, 0) + 1
        logger.debug(
            f"{self.name} Crimson Knot on enemy {enemyID}: {self.crimsonKnot[enemyID]} (total: {totalKnots + 1})")

    def _addSlashedDream(self, amount: int):
        """Add Slashed Dream points. Overflow beyond maxEnergy converts to
        Quadrivalent Ascendance stacks (capped at 3) per Trace 1."""
        newEnergy = self.currEnergy + amount
        if newEnergy > self.maxEnergy and self.ultActive == False:
            overflow = newEnergy - self.maxEnergy
            self.currEnergy = self.maxEnergy
            self.QuadrivalentStacks = min(3, self.QuadrivalentStacks + int(overflow))
            logger.debug(f"{self.name} Slashed Dream overflow: +{int(overflow)} Quadrivalent (total {self.QuadrivalentStacks})")
        else:
            self.currEnergy = newEnergy

    def _transferKnots(self, deadEnemyID: int):
        """Transfer knots from a dead enemy to the enemy with the most stacks."""
        if deadEnemyID not in self.crimsonKnot or self.crimsonKnot[deadEnemyID] == 0:
            return
        stacks = self.crimsonKnot.pop(deadEnemyID)
        if not self.crimsonKnot:
            return
        target = max(self.crimsonKnot, key=lambda k: self.crimsonKnot[k])
        self.crimsonKnot[target] = self.crimsonKnot.get(target, 0) + stacks
        logger.debug(f"{self.name} transferred {stacks} Crimson Knot from enemy {deadEnemyID} to enemy {target}")

    def _debuffWasApplied(self, result: Result) -> bool:
        """Return True if the ability applied at least one debuff to any enemy."""
        return len(result.debuffsApplied) > 0

    # ---------------------------------------------------------------------------
    # Actions
    # ---------------------------------------------------------------------------

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        if self.eidolon == 6:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC, AtkType.ULT], [self.element],
                     [e3Mul * self.NihilityBoost, 0], [10, 0], 0, self.scaling, 1, "AcheronBasic", omniBreak=True))
        else:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                     [e3Mul * self.NihilityBoost, 0], [10, 0], 0, self.scaling, 1, "AcheronBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e5MulMain = 1.76 if self.eidolon >= 5 else 1.6
        e5MulSide = 0.66 if self.eidolon >= 5 else 0.6
        if self.eidolon == 6:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.BLAST, [AtkType.SKL, AtkType.ULT], [self.element],
                     [e5MulMain * self.NihilityBoost, e5MulSide * self.NihilityBoost], [20, 10], 0, self.scaling, -1,
                     "AcheronSkill", omniBreak=True))
        else:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.BLAST, [AtkType.SKL], [self.element],
                     [e5MulMain * self.NihilityBoost, e5MulSide * self.NihilityBoost], [20, 10], 0, self.scaling, -1,
                     "AcheronSkill"))
        # Skill always applies a debuff — grant 1 Slashed Dream
        self._addSlashedDream(1)
        knotTarget = self._knotTarget()
        self._addKnot(knotTarget)
        logger.debug(f"{self.name} Skill: +1 Slashed Dream ({self.currEnergy}/{self.maxEnergy}), Knot on enemy {knotTarget}")
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        self.ultActive = True

        e3RainbladeST = 0.264 if self.eidolon >= 3 else 0.24
        e3KnotAOE     = 0.165 if self.eidolon >= 3 else 0.15
        e3Resurge     = 1.32  if self.eidolon >= 3 else 1.20

        target = self.bestEnemy(enemyID)

        e5Respen = 0.22 if self.eidolon >= 5 else 0.20
        self.crimsonKnot = {e.enemyID: 9 for e in self.enemyStatus}

        # AOE RES reduction during ult
        bl.append(Buff("AcheronUltPen", StatTypes.PEN, e5Respen, self.role,[AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))

        # Phase 1: 3 Rainblades
        rainbladeKnotHits = 0  # count how many Rainblades hit a target with Knots (for Trace 3 DMG stack)
        for i in range(3):
            tl.append(Turn(self.name, self.role, target, Targeting.SINGLE, [AtkType.ULT], [self.element],
                           [e3RainbladeST * self.NihilityBoost, 0], [10, 0], 0, self.scaling, 0, f"AcheronRainblade{i+1}", omniBreak=True))

            knots = self.crimsonKnot.get(target, 0)
            if knots > 0:
                rainbladeKnotHits += 1
                knotsRemoved = min(knots, 3)
                self.crimsonKnot[target] = knots - knotsRemoved
                bonusMul = min(knotsRemoved * 0.20, 0.60)
                knotAOEMul = e3KnotAOE * knotsRemoved * (1 + bonusMul)
                tl.append(Turn(self.name, self.role, target, Targeting.AOE, [AtkType.ULT], [self.element],
                               [knotAOEMul * self.NihilityBoost, 0], [5, 0], 0, self.scaling, 0, f"AcheronRainbladeKnot{i+1}", omniBreak=True))

        # Trace 3: Rainblade hitting a target with Knots gives 30% DMG per hit, up to 3 stacks, 3 turns
        if rainbladeKnotHits > 0:
            trace3DMG = 0.30 * min(rainbladeKnotHits, 3)
            bl.append(Buff("AcheronTrace3DMG", StatTypes.DMG_PERCENT, trace3DMG, self.role,[AtkType.ALL], 3, 1, Role.SELF, TickDown.END))

        # Phase 2: Stygian Resurge — AOE
        tl.append(Turn(self.name, self.role, target, Targeting.AOE, [AtkType.ULT], [self.element],
                       [e3Resurge * self.NihilityBoost, 0], [20, 0], 0, self.scaling, 0, "AcheronUlt", omniBreak=True))

        # Trace 3: Stygian Resurge triggers 6 additional single-target hits at 25% ATK each
        e3ResurgeBounce = 0.275 if self.eidolon >= 3 else 0.25
        for i in range(6):
            tl.append(Turn(self.name, self.role, target, Targeting.SINGLE, [AtkType.ULT], [self.element],
                           [e3ResurgeBounce * self.NihilityBoost, 0], [0, 0], 0, self.scaling, 0, f"AcheronResurgeBounce{i+1}", omniBreak=True))

        # Clear all Crimson Knots after ult
        self.crimsonKnot = {e.enemyID: 0 for e in self.enemyStatus}
        self.currEnergy = 0
        self.ultActive = False

        # Quadrivalent Ascendance: after ult, gain 1 Slashed Dream and 1 Knot on random enemy
        # (handled in ownTurn after "AcheronStygianResurge" result so energy is correct)
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        # Handle knot transfer on kills from own attacks
        if result.numKills > 0:
            for enemy in result.enemiesHit:
                if enemy.isDead():
                    self._transferKnots(enemy.enemyID)
        # Quadrivalent Ascendance: after ult ends, gain 1 Slashed Dream + 1 Knot per stack
        if result.turnName == "AcheronResurgeBounce6" and self.QuadrivalentStacks > 0:
            for _ in range(self.QuadrivalentStacks):
                self._addSlashedDream(1)
                knotTarget = self._knotTarget()
                self._addKnot(knotTarget)
                logger.debug(f"{self.name} Quadrivalent: +1 Slashed Dream, Knot on enemy {knotTarget}")
            self.QuadrivalentStacks = 0
            bl.append(Buff("AcheronUltPen", StatTypes.PEN, 0, self.role, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        if self._debuffWasApplied(result) and result.turnName not in bonusDMG and result.turnName != "AcheronUlt":
            self._addSlashedDream(1)
            knotTarget = self._knotTarget()
            self._addKnot(knotTarget)
            logger.debug(f"{self.name} allyTurn debuff triggered: +1 Slashed Dream ({self.currEnergy}/{self.maxEnergy}), Knot on enemy {knotTarget}")
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)

        # Handle knot transfer on kills from allies
        if result.numKills > 0:
            for enemy in result.enemiesHit:
                if enemy.isDead():
                    self._transferKnots(enemy.enemyID)

        # Slashed Dream: gain 1 stack if the ability applied any debuff,
        # but only once per ability use (debuffsApplied already deduplicates at the Result level)
        if self._debuffWasApplied(result):
            self._addSlashedDream(1)
            knotTarget = self._knotTarget()
            self._addKnot(knotTarget)
            logger.debug(f"{self.name} allyTurn debuff triggered: +1 Slashed Dream ({self.currEnergy}/{self.maxEnergy}), Knot on enemy {knotTarget}")

        return bl, dbl, al, dl, tl, hl

    def takeTurn(self) -> str:
        if self.eidolon >= 2:
            self._addSlashedDream(1)
            knotTarget = self._knotTarget()
            self._addKnot(knotTarget)
            logger.debug(f"{self.name} Skill: +1 Slashed Dream ({self.currEnergy}/{self.maxEnergy}), Knot on enemy {knotTarget}")
        return super().takeTurn()

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        E2ExtraNihility = 1 if self.eidolon >= 2 else 0
        self.NihilityCount = specialRes.attr1 + E2ExtraNihility

        if self.NihilityCount == 1:
            self.NihilityBoost = 1.15
        if self.NihilityCount >= 2:
            self.NihilityBoost = 1.60

        # Initialize Crimson Knot tracker for each enemy
        self.crimsonKnot = {e.enemyID: 0 for e in self.enemyStatus}

        # Technique: AOE hit, omniBreak, then gain Quadrivalent Ascendance
        if self.Tech:
            self.Tech = False
            tl.append(Turn(self.name, self.role, self.bestEnemy(-1), Targeting.AOE, [AtkType.TECH], [self.element],
                           [2.0, 0], [20, 0], 0, self.scaling, 0, "AcheronTech", omniBreak=True))
            # Quadrivalent Ascendance granted by Technique (triggers after next ult)
            self.QuadrivalentStacks = min(3, self.QuadrivalentStacks + 1)
            logger.debug(f"{self.name} Technique: Quadrivalent Ascendance gained ({self.QuadrivalentStacks})")
            import random
            knotEnemy = random.choice(list(self.enemyStatus)).enemyID
            for _ in range(5):
                self._addKnot(knotEnemy)
            logger.debug(f"{self.name} Trace 1: applied 5 Crimson Knot to enemy {knotEnemy}")

        return bl, dbl, al, dl, tl, hl