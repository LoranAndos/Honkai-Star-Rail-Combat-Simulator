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
    currAV = 0
    aggro = 100
    buffList = []

    # Unique Character Properties
    hasMemosprite = True
    firstTurn = True
    technique = True
    CanGetEnergy = False
    Epic = 0
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
        self.firstTurn = True
        self.technique = True
        self.CanGetEnergy = False
        self.Epic = 0

    def getMem(self):
        for c in (Character._current_player_team or []):
            if getattr(c, "isMemosprite", False) and getattr(c, "MemoSummonerName", None) == self.name:
                return c
        return None

    def equip(self):  # function to add base buffs to wearer
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("RmcTraceCD", StatTypes.CD_PERCENT, 0.373, self.role))
        bl.append(Buff("RmcTraceATK", StatTypes.ATK_PERCENT, 0.14, self.role))
        bl.append(Buff("RmcTraceHP", StatTypes.HP_PERCENT, 0.14, self.role))
        al.append(Advance("RmcStartADV", self.role, 0.30))      # A2: advance forward by 30% at the start of the battle
        return bl, dbl, al, dl, hl, sl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useBsc(enemyID)
        mem = self.getMem()
        if self.Epic > 0 and mem is not None and mem.MemoActive:
            e5Mul = 1.32 if self.eidolon >= 5 else 1.2
            self.Epic -= 1
            tl.append(Turn(self.name, self.role, -1, Targeting.AOE, [AtkType.BSC], [self.element],
                           [e5Mul, 0], [5, 0], 30, self.scaling, 1, "RmcEnhancedBasic"))
            tl.append(Turn(mem.name, mem.role, -1, Targeting.AOE, [AtkType.MEMO, AtkType.BSC], [mem.element],
                           [e5Mul, 0], [5, 0], 0, mem.scaling, 0, "MemJointBasic"))
        else:
            e5Mul = 1.1 if self.eidolon >= 5 else 1.0
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                           [e5Mul, 0], [10, 0], 20, self.scaling, 1, "RmcBasic"))
        return bl, dbl, al, dl, tl, hl, sl

    def useSkl(self, enemyID=-1):
        # Summons Mem; if Mem is already out it heals Mem and gives it 10% Charge (resolved in Mem.allyTurn)
        bl, dbl, al, dl, tl, hl, sl = super().useSkl(enemyID)
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.NA, [AtkType.SPECIAL], [self.element],
                     [0, 0], [0, 0], 30, self.scaling, -1, "MemSpawn"))
        return bl, dbl, al, dl, tl, hl, sl

    def useUlt(self, enemyID=-1):
        # Summons Mem if absent, gives it 40% Charge and Mem hits all enemies (resolved in Mem.allyTurn)
        self.currEnergy = self.currEnergy - self.ultCost
        bl, dbl, al, dl, tl, hl, sl = super().useUlt(enemyID)
        self.Epic = min(2, self.Epic + 1)
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.NA, [AtkType.ULT], [self.element],
                     [0, 0], [0, 0], 5, self.scaling, 0, "RmcUltimate"))
        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)
        # Every Memosprite skill of Mem (Baddies! Trouble! / Lemme! Help You!) gives Rmc 10 Energy
        if result.turnName in ("MemBigSkill", "MemSupport"):
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.NA, [AtkType.ULT], [self.element],
                     [0, 0], [0, 0], 10, self.scaling, 0, "MemAttackEnergy"))
        # E2: other memosprites acting give Rmc 8 Energy (once per turn)
        if (turn.charRole in (Role.MEMO1, Role.MEMO2, Role.MEMO3, Role.MEMO4) and not turn.charName == "Mem"
                and self.CanGetEnergy == True and self.eidolon >= 2):
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.NA, [AtkType.ULT], [self.element],
                     [0, 0], [0, 0], 8, self.scaling, 0, "RmcE2Energy"))
            self.CanGetEnergy = False
        return bl, dbl, al, dl, tl, hl, sl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().ownTurn(turn, result)
        self.CanGetEnergy = True
        return bl, dbl, al, dl, tl, hl, sl

    def takeTurn(self) -> str:
        res = super().takeTurn()
        mem = self.getMem()
        # first turn: summon Mem; later: re-summon it if it disappeared (0 HP)
        if self.firstTurn or (mem is not None and not mem.MemoActive):
            self.firstTurn = False
            return "E"
        return res

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)   # also stores enemyStatus for bestEnemy()
        if self.technique:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.AOE, [AtkType.TECH], [self.element],
                     [1, 0], [0, 0], 0, self.scaling, 0, "RmcTechnique"))
            dl.append(Delay("RmcTechnique", 0.5,Role.ALL, False, False))
            self.technique = False
        return bl, dbl, al, dl, tl, hl, sl