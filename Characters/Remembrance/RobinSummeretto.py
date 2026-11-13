import logging

from Lightcones.Hunt.CruisingInTheStellarSea import CruisingInTheStellarSea
from Relics.ScholarLostInErudition import ScholarLostInErudition
from Planars.RutilantArena import RutilantArena
from Buff import *
from Character import Character
from Delay_Text import *
from RelicStats import RelicStats
from Result import *
from Turn_Text import Turn
from Healing import *

logger = logging.getLogger(__name__)

class RobinSummeretto(Character):
    # Standard Character Properties
    name = "RobinSummeretto"
    path = Path.REMEMBRANCE
    element = Element.WIND
    scaling = Scaling.HP
    baseHP = 1203
    baseATK = 602
    baseDEF = 485
    baseSPD = 95
    maxEnergy = 140
    ultCost = 140
    currEnergy = 70
    currAV = 0
    aggro = 100
    buffList = []

    # Unique Character Properties
    hasMemosprite = True

    # Relic Settings

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc = None, r1 = None, r2 = None, pl = None, subs = None, eidolon = 6, targetPrio = Priority.BROKEN, rotation = None) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else CruisingInTheStellarSea(self.role)
        self.relic1 = r1 if r1 else ScholarLostInErudition(self.role,4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else RutilantArena(self.role)
        self.relicStats = subs if subs else RelicStats(2, 2, 2, 2, 2, 11, 2, 2, 2, 2, 5, 12, StatTypes.CR_PERCENT, StatTypes.SPD,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["A"]

    def equip(self):  # function to add base buffs to wearer
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("RobinSummerettoTraceCR", StatTypes.CR_PERCENT, 0.067, self.role))
        bl.append(Buff("RobinSummerettoTraceSPD", StatTypes.SPD, 14, self.role))
        bl.append(Buff("RobinSummerettoTraceHP", StatTypes.HP_PERCENT, 0.18, self.role))
        return bl, dbl, al, dl, hl, sl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useBsc(enemyID)

        return bl, dbl, al, dl, tl, hl, sl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useSkl(enemyID)

        return bl, dbl, al, dl, tl, hl, sl

    def useUlt(self, enemyID=-1):
        self.currEnergy = self.currEnergy - self.ultCost
        bl, dbl, al, dl, tl, hl, sl = super().useUlt(enemyID)

        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)

        return bl, dbl, al, dl, tl, hl, sl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().ownTurn(turn, result)

        return bl, dbl, al, dl, tl, hl, sl

    def takeTurn(self) -> str:
        res = super().takeTurn()

        return res

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)   # also stores enemyStatus for bestEnemy()

        return bl, dbl, al, dl, tl, hl, sl