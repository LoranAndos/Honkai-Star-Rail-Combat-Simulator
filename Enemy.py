# actionOrder = [1,1,2] means single attack, single attack, double attack
from Attributes import *

# ── Global switch ──────────────────────────────────────────────────────────────
# True  → enemies have fixed HP; they "die", reset, and the killer earns energy.
# False → enemies have infinite HP (original behaviour).
FINITE_ENEMY_HP = False

# Kill-energy rewards per enemy type
KILL_ENERGY = {
    EnemyType.BOSS:  20,
    EnemyType.ELITE: 10,
    EnemyType.ADD:    5,
}

class Enemy:
    broken = False
    role = Role.ENEMY

    def __init__(self, enemyID: int, level: int, enemyType: EnemyType, spd: float, toughness: int, actionOrder: list,
                 weakness: list, adjacent: list, CanDoDamage: bool, maxHP: float = 1_000_000,
                 numAttacksPerTurn: int = None):
        self.enemyID = enemyID
        self.name = f"Enemy {self.enemyID}"
        self.level = level
        self.enemyType = enemyType
        self.spd = spd
        self.atk = 718
        self.currSPD = self.spd
        self.toughness = toughness
        self.gauge = self.toughness
        self.actionOrder = actionOrder
        self.weakness = weakness
        self.adjacent = adjacent
        self.CanDoDamage = CanDoDamage
        self.currAV = 10000 / self.spd
        self.turn = 0
        self.maxToughnessMul = 0.5 + (self.toughness / 40)
        self.priority = 0
        self.debuffDMG = 0
        self.maxHP = maxHP
        self.currHP = maxHP
        self.overkillDMG = 0.0   # total damage that exceeded the enemy's max HP
        # Override how many individual attacks this enemy makes each turn.
        # If None, uses the value returned by takeTurn() (i.e. actionOrder).
        self.numAttacksPerTurn = numAttacksPerTurn
        # Global damage multiplier for all outgoing attacks. Change freely per enemy.
        # e.g. enemy.dmgPercent = 0.5 makes all hits deal 50% of normal damage.
        self.dmgPercent = 5.0

    def __str__(self) -> str:
        res = f"Enemy {self.enemyID} | LVL: {self.level} | SPD: {self.spd} | "
        res += f"Weakness: {[w.name for w in self.weakness]} | Toughness: {self.gauge}"
        return res

    def getUniMul(self) -> float:
        return 1.0 if self.broken else 0.9

    def redToughness(self, toughness: float) -> bool:
        self.gauge = max(self.gauge - toughness, 0)
        if self.gauge > 0:
            return False
        if not self.broken:
            self.broken = True
            return True
        return False

    def recover(self):
        if self.broken:
            self.gauge = self.toughness
            self.broken = False

    def takeTurn(self) -> int:
        self.recover()
        res = self.turn
        self.turn = self.turn + 1
        base = self.actionOrder[res % len(self.actionOrder)]
        # numAttacksPerTurn overrides the actionOrder count if set
        return self.numAttacksPerTurn if self.numAttacksPerTurn is not None else base

    # ── HP ratio helpers (for use in lightcones) ──────────────────────────────

    def getHPRatio(self) -> float:
        """Returns currHP / maxHP (0.0 – 1.0). Safe when maxHP is 0."""
        return (self.currHP / self.maxHP) if self.maxHP > 0 else 1.0

    def getHPPercent(self) -> float:
        """Returns HP as a percentage (0 – 100)."""
        return self.getHPRatio() * 100.0

    def calcDamageTo(self, targetDef: float, targetLevel: int, energyGiven: float = 10.0) -> float:
        """Outgoing damage this enemy deals to a character, scaled by how much
        energy the hit gave that character, and also by self.dmgPercent.

        Energy → hit scaling:
            10 energy  →  100% ATK  (single-target / blast)
             5 energy  →   50% ATK  (AOE)
        self.dmgPercent applies on top (default 1.0 = no change).

        DEF formula: defMul = 1 - charDEF / (charDEF + 200 + 10 * enemyLevel)
        """
        hitScale = energyGiven / 10.0
        base = self.atk * hitScale * self.dmgPercent
        defMul = 1 - (targetDef / (targetDef + 200 + 10 * self.level))
        return base * defMul

    @staticmethod
    def isChar() -> bool:
        return False

    @staticmethod
    def isSummon() -> bool:
        return False

    def reduceAV(self, reduceValue: float):
        self.currAV = max(0.0, self.currAV - reduceValue)

    def hasAdj(self) -> bool:
        return len(self.adjacent) > 0

    def getRes(self, element) -> float:
        return 0 if element in self.weakness else 0.2

    def standardAVred(self, av: float):
        self.currAV = max(0.0, self.currAV - av)

    def addDebuffDMG(self, dmg: float):
        self.debuffDMG = self.debuffDMG + dmg

    # ── HP / kill helpers ──────────────────────────────────────────────────────

    def takeHit(self, dmg: float) -> bool:
        """Remove dmg from currHP (only when FINITE_ENEMY_HP is on).
        Tracks overkill. Returns True if the enemy just died."""
        if not FINITE_ENEMY_HP:
            return False
        if self.currHP <= 0:
            return False                     # already dead / waiting for respawn
        self.currHP -= dmg
        if self.currHP <= 0:
            self.overkillDMG += abs(self.currHP)   # how far below 0 we went
            self.currHP = 0
            return True
        return False

    def isDead(self) -> bool:
        return FINITE_ENEMY_HP and self.currHP <= 0

    def respawn(self):
        """Reset to full HP and advance AV by 100% (instant next turn)."""
        self.currHP = self.maxHP
        self.currAV = 0.0          # 100% AV forward = act immediately

    def getDefMul(self, attackerLevel: int) -> float:
        """DEF multiplier for incoming attacks from a unit of attackerLevel."""
        return 1 - (self.level / (self.level + 200 + 10 * attackerLevel))



class EnemyModule:
    def __init__(self, numEnemies: int, enemyLevel: list[int], enemyTypes: list[EnemyType], enemySPD: list[float],
                 toughness: list[int], attackRatios: list[float], weaknesses: list[Element], actionOrder: list[int]):
        self.numEnemies = numEnemies
        self.enemyLevel = enemyLevel
        self.enemyTypes = enemyTypes
        self.enemySPD = enemySPD
        self.toughness = toughness
        self.attackRatios = attackRatios
        self.weaknesses = weaknesses
        self.actionOrder = actionOrder