# actionOrder = [1,1,2] means single attack, single attack, double attack
from Attributes import *


class Enemy:
    broken = False
    role = Role.ENEMY

    def __init__(self, enemyID: int, level: int, enemyType: EnemyType, spd: float, toughness: int, actionOrder: list,
                 weakness: list, adjacent: list, CanDoDamage: bool):
        self.enemyID = enemyID
        self.name = f"Enemy {self.enemyID}"
        self.level = level
        self.enemyType = enemyType
        self.spd = spd
        self.atk = 738
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
        return self.actionOrder[res % len(self.actionOrder)]

    def doDamage(self) -> int: #Still have to figure out how the enemy does damage, and making sure characters don't die.
        return True

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
