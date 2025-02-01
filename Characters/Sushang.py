import logging
from Simulator.Buff  import *
from Simulator.Character import Character
from Simulator.Delay_Text import *
from Simulator.RelicStats import RelicStats
from Simulator.Result import Special
from Simulator.Turn_Text import Turn
from Simulator.Enemy import *
from Simulator.MainFunctions import *

logger = logging.getLogger(__name__)

class Sushang(Character):
    # Standard Character Properties
    name = "Sushang"
    path = Path.HUNT
    element = Element.PHYSICAL
    scaling = "ATK"
    baseHP = 917.3
    baseATK = 564.48
    baseDEF = 418.95
    baseSPD = 107.0
    maxEnergy = 120.0
    ultCost = 120.0
    currEnergy = 60
    currAV = 100.0
    aggro = 75
    rotation = ["E"]
    dmgDct = {AtkType.BSC: 0.0, AtkType.SKL: 0.0, AtkType.ULT: 0.0, AtkType.BRK: 0.0, AtkType.SBK: 0.0}
    hasSummon = False
    specialEnergy = False
    basics = 0
    skills = 0
    ults = 0
    turn = 0
    lightcone = None
    relic1 = None
    relic2 = None
    planar = None
    enemyStatus = []

    # Unique Character Properties

    # Relic Settings

    def __init__(self, pos: int, role: Role, defaultTarget: int, lc = None, r1 = None, r2 = None, pl = None, subs = None, eidolon = 6, targetPrio = Priority.BROKEN, rotation = None) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc
        self.relic1 = r1
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)#Temporary
        self.planar = pl
        self.relicStats = subs if subs else RelicStats(2, 2, 2, 2, 2, 11, 2, 2, 2, 2, 5, 12, StatTypes.CR_PERCENT, StatTypes.Spd,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["E", "A", "A"]

    def equip(self):  # function to add base buffs to wearer
        bl, dbl, al, dl = super().equip()
        bl.append(Buff("SushangTraceATK",StatTypes.ATK_PERCENT,0.28,self.role))
        bl.append(Buff("SushangTraceHP",StatTypes.ATK_PERCENT,0.18,self.role))
        bl.append(Buff("SushangTraceDEF",StatTypes.ATK_PERCENT,0.125,self.role))
        if self.eidolon >= 4:
            bl.append(Buff("SushangE4BE", StatTypes.BE_PERCENT, 0.40, self.role))
        return bl, dbl, al, dl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl = super().useBsc(enemyID)
        e5Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e5Mul, 0], [10, 0], 20, self.scaling, 1, "SushangBasic"))
        return bl, dbl, al, dl, tl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl = super().useSkl(enemyID)
        e3Mul = 2.31 if self.eidolon >= 3 else 2.1
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.SKL], [self.element],
                       [e3Mul, 0], [20, 0], 30, self.scaling, -1, "SushangSkill"))
        return bl, dbl, al, dl, tl

    def useUlt(self, enemyID=-1):
        self.ults = self.ults + 1
        return *self.parseEquipment(AtkType.ULT, enemyID=enemyID), []

    def special(self):
        return self.name

    def handleSpecialStart(self, specialRes: Special):
        self.enemyStatus = specialRes.enemies
        return *self.parseEquipment("SPECIALS", special=specialRes), []

    def handleSpecialEnd(self, specialRes: Special):
        return *self.parseEquipment("SPECIALE", special=specialRes), []

    def allyTurn(self, turn: Turn, result: Result):
        return *self.parseEquipment("ALLY", turn=turn, result=result), []
