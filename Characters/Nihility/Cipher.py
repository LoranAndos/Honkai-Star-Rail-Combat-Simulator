import logging

from Buff import *
from Character import Character
from Attributes import *
from Lightcones.Nihility.ReforgedInHellfire import ReforgedInHellfire
from Lightcones.Nihility.ResolutionShinesAsPearlsOfSweat import ResolutionMortenaxBlade
from Lightcones.Nihility.LiesDanceOnTheBreeze import LiesDanceOnTheBreeze
from Planars.LushakaTheSunkenSeas import LushakaTheSunkenSeas
from RelicStats import RelicStats
from Relics.PioneerDiverOfDeadWaters import PioneerCipher
from Result import *
from Turn_Text import Turn
from Healing import *

logger = logging.getLogger(__name__)


class Cipher(Character):
    # Standard Character Settings
    name = "Cipher"
    path = Path.NIHILITY
    element = Element.LIGHTNING
    scaling = Scaling.ATK
    baseHP = 931
    baseATK = 640
    baseDEF = 509
    baseSPD = 106
    maxEnergy = 130
    currEnergy = 65
    ultCost = 130
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.FUA: 0}  # Adjust accordingly

    # Unique Character Properties
    SpdStat = 0.0
    TallyMultiplier = 1.0
    TallyReturned = 0.0
    patronEnemyID = -1       # which enemy is currently the "Patron"
    tally = 0.0              # accumulated 12% of non-True-DMG ally damage to Patron
    fuaUsedThisTurn = False  # FUA can trigger only once per Cipher turn
    pendingTrueDmg = 0.0     # True Damage dealt this turn, flushed to dmgTracker by processTurnList
    Tech = True

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
        self.rotation = rotation if rotation else ["A"]
        self.E1TallyMultiplier = 1.5 if self.eidolon >= 1 else 1.0
        self.E6TalentIncrease = 3.5 if self.eidolon >= 6 else 0.0
        self.E6TallyIncrease = 0.16 if self.eidolon >= 6 else 0.0

    def _splitTally(self, turn: Turn, result: Result):
        """Returns (patronDmg, nonPatronDmg) by weighting turnDmg via dmgSplit ratios.

        - SINGLE / SPECIAL: all damage goes to the one target hit.
        - BLAST: main target gets dmgSplit[0] share, adjacent get dmgSplit[1] share each.
          Total weight = dmgSplit[0] + adjCount * dmgSplit[1].
        - AOE: every enemy gets an equal share (turnDmg / numHit).
        """
        enemiesHit = result.enemiesHit
        if not enemiesHit:
            return 0.0, 0.0

        totalDmg = result.turnDmg
        patronID = self.patronEnemyID

        if turn.targeting == Targeting.AOE:
            perEnemy = totalDmg / len(enemiesHit)
            patronDmg    = sum(perEnemy for e in enemiesHit if e.enemyID == patronID)
            nonPatronDmg = sum(perEnemy for e in enemiesHit if e.enemyID != patronID)
            return patronDmg, nonPatronDmg

        if turn.targeting == Targeting.BLAST:
            mainID = turn.targetID
            adjCount = sum(1 for e in enemiesHit if e.enemyID != mainID)
            mainWeight = turn.dmgSplit[0]
            adjWeight  = turn.dmgSplit[1]
            totalWeight = mainWeight + adjCount * adjWeight
            if totalWeight == 0:
                return 0.0, 0.0
            patronDmg    = 0.0
            nonPatronDmg = 0.0
            for e in enemiesHit:
                w = mainWeight if e.enemyID == mainID else adjWeight
                share = totalDmg * (w / totalWeight)
                if e.enemyID == patronID:
                    patronDmg += share
                else:
                    nonPatronDmg += share
            return patronDmg, nonPatronDmg

        # SINGLE / SPECIAL / anything else — all damage to the one target
        if any(e.enemyID == patronID for e in enemiesHit):
            return totalDmg, 0.0
        return 0.0, totalDmg

    def _applyTally(self, patronDmg: float, nonPatronDmg: float):
        """Add the split damage amounts to the tally at the correct rates."""
        patron = next((e for e in self.enemyStatus if e.enemyID == self.patronEnemyID), None)
        if not patron:
            return
        maxTally = patron.maxHP
        if patronDmg > 0:
            gain = patronDmg * (0.12 + self.E6TallyIncrease) * self.TallyMultiplier * self.E1TallyMultiplier
            self.tally = min(maxTally, self.tally + gain)
            logger.debug(f"    TALLY  - {self.name} +{gain:.1f} tally (patron {patronDmg:.1f}) → total {self.tally:.1f}")
        if nonPatronDmg > 0:
            gain = nonPatronDmg * (0.08 + self.E6TallyIncrease) * self.TallyMultiplier * self.E1TallyMultiplier
            self.tally = min(maxTally, self.tally + gain)
            logger.debug(f"    TALLY  - {self.name} +{gain:.1f} tally (non-patron {nonPatronDmg:.1f}) → total {self.tally:.1f}")

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("CipherTraceSPD", StatTypes.SPD, 14, self.role))
        bl.append(Buff("CipherTraceEHR", StatTypes.EHR_PERCENT, 0.10, self.role))
        bl.append(Buff("CipherTraceDMG", StatTypes.DMG_PERCENT, 0.144, self.role))
        bl.append(Buff("Talent3CD", StatTypes.CD_PERCENT, 1.00, self.role, [AtkType.FUA], 1, 1, Role.SELF, TickDown.PERM))
        dbl.append(Debuff("CipherTrace3Vuln", self.role, StatTypes.VULN, 0.40, Role.ALL, [AtkType.ALL], 1000,1,Targeting.AOE))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20, self.scaling, 1, "CipherBasic"))
        if self.eidolon >= 2:
            dbl.append(Debuff("CipherE2Vuln", self.role, StatTypes.VULN, 0.30, enemyID, [AtkType.ALL], 2, 1, Targeting.SINGLE))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e5MulMain = 2.2 if self.eidolon >= 5 else 2.0
        e5MulSide = 1.1 if self.eidolon >= 5 else 1.0
        # Skill primary target becomes the Patron
        self.patronEnemyID = self.bestEnemy(enemyID)
        logger.debug(f"{self.name} Skill: enemy {self.patronEnemyID} is now the Patron")
        dbl.append(Debuff("CipherSkillDmgReduction", self.role, StatTypes.ENEMY_DMG_REDUCTION, 0.10, enemyID, [AtkType.ALL], 2,1,Targeting.BLAST))
        bl.append(Buff("CipherSkillAttack", StatTypes.ATK_PERCENT, 0.30, self.role, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.BLAST, [AtkType.SKL], [self.element],
                       [e5MulMain, e5MulSide], [20, 10], 30, self.scaling, -1, "CipherSkill"))
        if self.eidolon >= 2:
            dbl.append(Debuff("CipherE2Vuln", self.role, StatTypes.VULN, 0.30, enemyID, [AtkType.ALL], 2, 1, Targeting.BLAST))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost

        # Ult primary target becomes the Patron
        target = self.bestEnemy(enemyID)
        self.patronEnemyID = target
        logger.debug(f"{self.name} Ult: enemy {target} is now the Patron")

        e3MulST = 1.32 if self.eidolon >= 3 else 1.20
        e3MulBLAST = 0.44 if self.eidolon >= 3 else 0.40

        # Phase 1: 120% ATK ST hit
        tl.append(Turn(self.name, self.role, target, Targeting.SINGLE, [AtkType.ULT], [self.element],
                       [e3MulST, 0], [10, 0], 5, self.scaling, 0, "CipherUltST"))

        # Phase 2: 25% of tally as True Damage to primary target (flat, stored on char)
        # Dealt via ownTurn after CipherUltST resolves — see ownTurn
        # Phase 3: 40% ATK + 75% tally True Damage to primary + adjacent (AOE)
        tl.append(Turn(self.name, self.role, target, Targeting.BLAST, [AtkType.ULT], [self.element],
                       [e3MulBLAST, e3MulBLAST], [20, 20], 0, self.scaling, 0, "CipherUltAOE"))
        if self.eidolon >= 2:
            dbl.append(Debuff("CipherE2Vuln", self.role, StatTypes.VULN, 0.30, enemyID, [AtkType.ALL], 2, 1, Targeting.BLAST))
        return bl, dbl, al, dl, tl, hl

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useFua(enemyID)
        e5Mul = 1.65 if self.eidolon >= 5 else 1.5
        tl.append(Turn(self.name, self.role, self.patronEnemyID, Targeting.SINGLE, [AtkType.FUA],
                       [self.element], [e5Mul + self.E6TalentIncrease, 0], [20, 0], 5, self.scaling, 0, "CipherTalentFUA"))
        if self.eidolon >= 1:
            bl.append(Buff("CipherE1Attack", StatTypes.ATK_PERCENT, 0.80, self.role, [AtkType.ALL], 2, 1, Role.SELF,TickDown.END))
        if self.eidolon >= 2:
            dbl.append(Debuff("CipherE2Vuln", self.role, StatTypes.VULN, 0.30, enemyID, [AtkType.ALL], 2, 1, Targeting.SINGLE))
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)

        if result.turnDmg > 0 and self.patronEnemyID != -1 and turn.moveName not in ("CipherUltST", "CipherUltAOE"):
            patronDmg, nonPatronDmg = self._splitTally(turn, result)
            self._applyTally(patronDmg, nonPatronDmg)

        if result.turnDmg > 0 and result.turnName == "CipherTech" and self.patronEnemyID != -1:
            # Technique grants double tally — apply the patron portion again at full rate
            patron = next((e for e in self.enemyStatus if e.enemyID == self.patronEnemyID), None)
            if patron:
                patronDmg, _ = self._splitTally(turn, result)
                gain = patronDmg * (0.12 + self.E6TallyIncrease) * self.TallyMultiplier * self.E1TallyMultiplier
                self.tally = min(patron.maxHP, self.tally + gain)
                logger.debug(f"    TALLY  - {self.name} +{gain:.1f} extra tally from CipherTech (total: {self.tally:.1f})")

        # After the ST ult hit lands: deal 25% tally as True Damage to the Patron
        if result.turnName == "CipherUltST" and self.patronEnemyID != -1 and self.tally > 0:
            trueDmg25 = self.tally * 0.25
            patron = next((e for e in self.enemyStatus if e.enemyID == self.patronEnemyID), None)
            if patron:
                patron.takeHit(trueDmg25)
                self.pendingTrueDmg += trueDmg25
                self.dmgDct[AtkType.ULT] = self.dmgDct.get(AtkType.ULT, 0) + trueDmg25
                logger.warning(f"    TRUE   - {self.name} Ult 25% tally True DMG: {trueDmg25:.1f} to enemy {self.patronEnemyID}")

        # After the AOE ult hit lands: deal 75% tally as True Damage split evenly across all enemies, then clear tally
        if result.turnName == "CipherUltAOE" and self.tally > 0:
            trueDmg75 = self.tally * 0.75
            aliveEnemies = [e for e in self.enemyStatus if not e.isDead()]
            if aliveEnemies:
                perEnemy = trueDmg75 / len(aliveEnemies)
                for enemy in aliveEnemies:
                    enemy.takeHit(perEnemy)
                    logger.warning(f"    TRUE   - {self.name} Ult 75% tally True DMG: {perEnemy:.1f} to enemy {enemy.enemyID}")
            self.pendingTrueDmg += trueDmg75
            self.dmgDct[AtkType.ULT] = self.dmgDct.get(AtkType.ULT, 0) + trueDmg75
            logger.warning(f"    TALLY  - {self.name} tally cleared after Ult (was {self.tally:.1f})")
            if self.eidolon >= 6:
                self.TallyReturned = 0.20 * self.tally
            self.tally = 0.0 + self.TallyReturned

        if result.turnDmg > 0 and self.eidolon >= 4 and turn.moveName not in bonusDMG:
            patron = next((e for e in self.enemyStatus if e.enemyID == self.patronEnemyID), None)
            if patron:
                tl.append(Turn(self.name, self.role, self.patronEnemyID, Targeting.SINGLE, [AtkType.ADD],
                               [self.element], [0.50, 0], [0, 0], 0, self.scaling, 0, "CipherE4Add"))

        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)

        if self.patronEnemyID == -1:
            return bl, dbl, al, dl, tl, hl

        # FUA only triggers when the Patron is hit
        hitPatron = any(e.enemyID == self.patronEnemyID for e in result.enemiesHit)

        if result.turnDmg > 0:
            patronDmg, nonPatronDmg = self._splitTally(turn, result)
            self._applyTally(patronDmg, nonPatronDmg)

        # FUA: trigger once per Cipher turn when an ally (not Cipher) attacks the Patron
        if hitPatron and not self.fuaUsedThisTurn and turn.charRole != self.role and turn.moveName not in bonusDMG and result.turnDmg > 0:
            self.fuaUsedThisTurn = True
            bl, dbl, al, dl, tl, hl = self.extendLists(bl, dbl, al, dl, tl, hl, *self.useFua(-1))
            logger.debug(f"    FUA    - {self.name} Talent FUA triggered on enemy {self.patronEnemyID}")

        if hitPatron and result.turnDmg > 0 and self.eidolon >= 4 and turn.moveName not in bonusDMG:
            patron = next((e for e in self.enemyStatus if e.enemyID == self.patronEnemyID), None)
            if patron:
                tl.append(Turn(self.name, self.role, self.patronEnemyID, Targeting.SINGLE, [AtkType.ADD],
                               [self.element], [0.50, 0], [0, 0], 0, self.scaling, 0, "CipherE4Add"))
        return bl, dbl, al, dl, tl, hl

    def useHit(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useHit(enemyID)
        return bl, dbl, al, dl, tl, hl

    def takeTurn(self) -> str:
        self.fuaUsedThisTurn = False
        return super().takeTurn()

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.SpdStat = specialRes.attr1

        # Talent: if no Patron on battlefield, assign the enemy with the highest max HP
        if self.patronEnemyID == -1 and self.enemyStatus:
            topEnemy = max(self.enemyStatus, key=lambda e: e.maxHP)
            self.patronEnemyID = topEnemy.enemyID
            logger.debug(f"{self.name} Talent: initial Patron set to enemy {self.patronEnemyID} (max HP: {topEnemy.maxHP:.0f})")

        if 170 > self.SpdStat >= 140:
            bl.append(Buff("Talent1CR", StatTypes.CR_PERCENT, 0.25, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
            self.TallyMultiplier = 1.50
        elif self.SpdStat >= 170:
            bl.append(Buff("Talent1CR", StatTypes.CR_PERCENT, 0.50, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
            self.TallyMultiplier = 2.0

        if self.Tech:
            self.Tech = False
            tl.append(Turn(self.name, self.role, self.patronEnemyID, Targeting.SINGLE, [AtkType.TECH],
                           [self.element], [1.0, 0], [0 , 0], 0, self.scaling, 0, "CipherTech"))
        return bl, dbl, al, dl, tl, hl