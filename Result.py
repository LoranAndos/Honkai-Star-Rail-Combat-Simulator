from Attributes import *
from Enemy import Enemy

class Result:
    def __init__(self, charName: str, charRole: Role, atkType: list, eleType: list, broken: list[Enemy], turnDmg: float,
                 wbDmg: float, Healing: float,errGain: float, turnName: str, enemiesHit: list[Enemy], preHitStatus: list[bool]):
        self.charName = charName
        self.charRole = charRole
        self.atkType = atkType
        self.eleType = eleType
        self.brokenEnemy = broken
        self.turnDmg = turnDmg
        self.wbDmg = wbDmg
        self.Healing = Healing
        self.errGain = errGain
        self.turnName = turnName
        self.enemiesHit = enemiesHit
        self.preHitStatus = preHitStatus

    def __str__(self) -> str:
        eHit = [e.enemyID for e in self.enemiesHit]
        broken = [e.enemyID for e in self.brokenEnemy]
        return f"{self.turnName} | {self.charName} | {self.charRole.name} | DMG: {self.turnDmg:.3f} | Enemies Hit: {eHit} | Enemies Broken: {broken} | WB DMG: {self.wbDmg:.3f} | Energy: {self.errGain:.3f} | Amount HP Changed: {self.Healing:.3f}"


class Special:
    def __init__(self, name: str, enemies=None, attr1=None, attr2=None, attr3=None, attr4=None, attr5=None, attr6=None):
        self.specialName = name
        self.enemies = enemies
        self.attr1 = attr1
        self.attr2 = attr2
        self.attr3 = attr3
        self.attr4 = attr4
        self.attr5 = attr5
        self.attr6 = attr6

    def __str__(self) -> str:
        return f"{self.specialName} | Attr1: {self.attr1} | Attr2: {self.attr2} | Attr3: {self.attr3} | Attr4: {self.attr4} | Attr5: {self.attr5}"