"""
Returns 4 lists:
- list of buffs added
- list of debuffs added
- list of adv% adjustments
- list of enemy debuffs to be applied
"""
from Turn_Text import *
from Result import *
from Attributes import *

class Equipment:
    def __init__(self, wearerRole: Role):
        self.wearerRole = wearerRole

    def equip(self):  # init function to add base buffs to wearer
        return [], [], [], [], []

    def useSkl(self, enemyID=-1):
        return [], [], [], [], []

    def useBsc(self, enemyID=-1):
        return [], [], [], [], []

    def useUlt(self, enemyID=-1):
        return [], [], [], [], []

    def useFua(self, enemyID=-1):
        return [], [], [], [], []

    def useAdd(self, enemyID=-1):
        return [], [], [], [], []

    def useMemo(self, enemyID=-1):
        return [], [], [], [], []

    def useHit(self, enemyID=-1):
        return [], [], [], [], []

    def allyTurn(self, turn: Turn, result: Result):
        return [], [], [], [], []

    def ownTurn(self, turn: Turn, result: Result):
        return [], [], [], [], []

    @staticmethod
    def specialStart(special: Special):
        return [], [], [], [], []

    # noinspection PyUnusedLocal
    @staticmethod
    def specialEnd(special: Special):
        return [], [], [], [], []

    @staticmethod
    def extendLists(bl: list, dbl: list, al: list, dl: list, hl: list, nbl: list, ndbl: list, nal: list, ndl: list, nhl: list):
        bl.extend(nbl)
        dbl.extend(ndbl)
        al.extend(nal)
        dl.extend(ndl)
        hl.extend(nhl)
        return bl, dbl, al, dl, hl