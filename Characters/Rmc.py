import logging

from Lightcones.CruisingInTheStellarSea import CruisingInTheStellarSea
from Relics.ScholarLostInErudition import ScholarLostInErudition
from Planars.RutilantArena import RutilantArena
from Buff import *
from Character import Character
from Delay_Text import *
from RelicStats import RelicStats
from Result import *
from Turn_Text import Turn
from Enemy import *
from Healing import *

logger = logging.getLogger(__name__)

class Rmc(Character):
    # Standard Character Properties
    name = "Remembrance Trailblazer"
    path = Path.REMEMBRANCE
    element = Element.ICE
    scaling = Scaling.ATK
    baseHP = 1047.8
    baseATK = 543.31
    baseDEF = 630.63
    baseSPD = 103.0
    maxEnergy = 160.0
    ultCost = 160.0
    currEnergy = 80
    currAV = 100.0
    aggro = 100
    buffList = []
    dmgDct = {AtkType.BSC: 0.0,AtkType.SPECIAL: 0.0,AtkType.BRK: 0.0, AtkType.SBK: 0.0}

    # Unique Character Properties
    hasMemosprite = True
    firstTurn = True
    technique = True
    CanGetEnergy = False
    # Relic Settings

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc = None, r1 = None, r2 = None, pl = None, subs = None, eidolon = 6, targetPrio = Priority.BROKEN, rotation = None) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else CruisingInTheStellarSea(self.role)
        self.relic1 = r1 if r1 else ScholarLostInErudition(self.role,4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else RutilantArena(self.role)
        self.relicStats = subs if subs else RelicStats(2, 2, 2, 2, 2, 11, 2, 2, 2, 2, 5, 12, StatTypes.CR_PERCENT, StatTypes.Spd,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["A"]

    def equip(self):  # function to add base buffs to wearer
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("RmcTraceCD", StatTypes.CD_PERCENT, 0.373, self.role))
        bl.append(Buff("RmcTraceATK", StatTypes.ATK_PERCENT, 0.14, self.role))
        bl.append(Buff("RmcTraceHP", StatTypes.HP_PERCENT, 0.14, self.role))
        al.append(Advance("RmcStartADV", self.role, 0.30))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e5Mul = 1.1 if self.eidolon >= 5 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e5Mul, 0], [10, 0], 20, self.scaling, 1, "RmcBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SINGLE, [AtkType.SPECIAL], [self.element],
                     [0, 0], [0, 0], 30, self.scaling, -1, "MemSpawn"))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        self.currEnergy = self.currEnergy - self.ultCost
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SINGLE, [AtkType.ULT], [self.element],
                     [0, 0], [0, 0], 5, self.scaling, 0, "RmcUltimate"))
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if result.turnName == "MemBigSkill":
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SINGLE, [AtkType.ULT], [self.element],
                     [0, 0], [0, 0], 10, self.scaling, 0, "MemAttackEnergy"))
        if (turn.charRole == Role.MEMO1 or turn.charRole == Role.MEMO2 or turn.charRole == Role.MEMO3) and not turn.charName == "Mem" and self.CanGetEnergy == True and self.eidolon >= 2:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SINGLE, [AtkType.ULT], [self.element],
                     [0, 0], [0, 0], 8, self.scaling, 0, "MemAttackEnergy"))
            self.CanGetEnergy = False

        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        self.CanGetEnergy = True
        return bl, dbl, al, dl, tl, hl

    def takeTurn(self) -> str:
        res = super().takeTurn()
        if self.firstTurn:
            self.firstTurn = False
            return "E"
        return res

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialEnd(specialRes)
        if self.technique:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.AOE, [AtkType.SPECIAL], [self.element],
                     [1, 0], [0, 0], 0, self.scaling, 0, "RmcTechnique"))
            dl.append(Delay("RmcTechnique", 0.5,Role.ALL, False, False))
            self.technique = False
        return bl, dbl, al, dl, tl, hl