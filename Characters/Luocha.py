import logging

from Buff import *
from Healing import *
from Character import Character
from Delay_Text import *
from Lightcones.CruisingInTheStellarSea import CruisingInTheStellarSea
from Planars.RutilantArena import RutilantArena
from RelicStats import RelicStats
from Relics.ScholarLostInErudition import ScholarLostInErudition
from Result import Result, Special
from Turn_Text import Turn

logger = logging.getLogger(__name__)


class Luocha(Character):
    # Standard Character Settings
    name = "Luocha"
    path = Path.ABUNDANCE
    element = Element.IMAGINARY
    scaling = Scaling.ATK
    baseHP = 1280.7
    baseATK = 756.76
    baseDEF = 363.82
    baseSPD = 101
    maxEnergy = 100
    currEnergy = 50
    ultCost = 100
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.ULT: 0, AtkType.BRK: 0}  # Adjust accordingly

    # Unique Character Properties
    stackCount = 2
    canStack = True

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else CruisingInTheStellarSea(role, 5)
        self.relic1 = r1 if r1 else ScholarLostInErudition(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else RutilantArena(role)
        self.relicStats = subs if subs else RelicStats(13, 2, 3, 2, 4, 8, 4, 4, 4, 4, 0, 0, StatTypes.OGH_PERCENT, StatTypes.Spd,
                                                       StatTypes.ATK_PERCENT, StatTypes.ERR_PERCENT)
        self.rotation = rotation if rotation else ["A"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(
            Buff("LuochaTraceATK", StatTypes.ATK_PERCENT, 0.28, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("LuochaTraceHP", StatTypes.HP_PERCENT, 0.18, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(
            Buff("LuochaTraceDEF", StatTypes.DEF_PERCENT, 0.125, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        if self.turn % 3 == 1:
            tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 30,
                           self.scaling, 0, "LuochaAutohealERR"))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20, self.scaling, 1, "LuochaBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        if self.canStack == 0:
            self.stackCount += 1
        tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.SKL], [self.element], [0, 0], [0, 0], 30,
                       self.scaling, -1, "LuochaSkill"))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        e5Mul = 2.16 if self.eidolon >= 5 else 2.0
        self.currEnergy = self.currEnergy - self.ultCost
        if self.canStack == 0:
            self.stackCount += 1
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT], [self.element],
                       [e5Mul, 0], [20, 0], 5, self.scaling, 0, "LuochaUlt"))
        if self.eidolon == 6:
            dbl.append(Debuff("LuochaE6PEN", self.role, StatTypes.PEN, 0.20, Role.ALL, [AtkType.ALL], 2))
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        if result.turnName != "LuochaAutohealERR" and self.turn % 3 == 1:
            if self.canStack == 0:
                self.stackCount += 1
        if self.stackCount >= 2:
            self.stackCount = 0
            self.canStack = 2
            atk = 0.2 if self.eidolon >= 1 else 0
            bl.append(Buff("LuochaField", StatTypes.ATK_PERCENT, atk, Role.ALL))
            if self.eidolon >= 4:
                dbl.append(Debuff("LuochaE4Weaken", self.role, StatTypes.GENERIC, 0.12, Role.ALL, [AtkType.ALL], 1000))
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        return super().handleSpecialStart(specialRes)

    def handleSpecialEnd(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialEnd(specialRes)
        self.canStack = max(0, self.canStack - 1)
        if self.canStack == 0:
            bl.append(Buff("LuochaField", StatTypes.ATK_PERCENT, 0, Role.ALL))
            if self.eidolon >= 4:
                dbl.append(Debuff("LuochaE4Weaken", self.role, StatTypes.GENERIC, 0, Role.ALL, [AtkType.ALL], 1000))
        return bl, dbl, al, dl, tl, hl

