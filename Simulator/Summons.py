from Buff import *
from Delay_Text import *
from Result import *
from Turn_Text import Turn


class Summon:
    name = "Summon"
    element = None
    currSPD = 100
    currAV = 10000 / currSPD
    currEnergy = 0
    maxEnergy = 0

    def __init__(self, ownerRole: Role, role: Role) -> None:
        self.ownerRole = ownerRole
        self.role = role
        self.priority = 0

    @staticmethod
    def isChar() -> bool:
        return True

    @staticmethod
    def isSummon() -> bool:
        return True

    def takeTurn(self) -> tuple[list[Buff], list[Debuff], list[Advance], list[Delay], list[Turn]]:
        return [], [], [], [], []

    def standardAVred(self, av: float):
        self.currAV = max(0.0, self.currAV - av)

    def reduceAV(self, reduceValue: float):
        self.currAV = max(0.0, self.currAV - reduceValue)

    def allyTurn(self, turn: Turn, result: Result) -> tuple[
        list[Buff], list[Debuff], list[Advance], list[Delay], list[Turn]]:
        return [], [], [], [], []