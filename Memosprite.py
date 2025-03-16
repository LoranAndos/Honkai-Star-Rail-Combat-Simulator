from Turn_Text import Turn
from Result import *
from Attributes import *
import logging

logger = logging.getLogger(__name__)

class Memosprite:
    # Standard Character Properties
    name = "Memosprite"
    path = Path.REMEMBRANCE
    element = Element.LIGHTNING
    scaling = "ATK"
    MemoSummoner = None
    baseHP = 0
    baseATK = 0
    baseDEF = 0
    baseSPD = 100.0
    maxEnergy = 100.0
    EnergyCost = 100.0
    currEnergy = maxEnergy / 2
    currAV = 100.0
    currHP = 1.0
    maxHP = 1.0
    aggro = 0
    MemoActive = False
    rotation = ["MemoAtk"]
    dmgDct = {AtkType.MEMO: 0.0}
    hasSummon = False
    specialEnergy = False

    basics = 0
    skills = 0
    ults = 0
    fuas = 0
    Adds = 0
    MemoAttack = 0
    lightcone = None
    relic1 = None
    relic2 = None
    planar = None
    turn = 0
    enemyStatus = []

    # Unique Character Properties

    # Relic Settings

    def __init__(self, pos: int, role: Role, defaultTarget: int, eidolon: int, targetPrio: Priority) -> None:
        self.relicStats = None
        self.pos = pos
        self.role = role
        self.priority = 0
        self.currSPD = 100
        self.defaultTarget = defaultTarget
        self.eidolon = min(6, eidolon)
        self.targetPrio = targetPrio

    def __str__(self) -> str:
        res = f"{self.name} | {self.element.name}-{self.path.name} | {self.role.name} | POS:{self.pos}\n"
        res += f"{self.lightcone}\n"
        res += f"{self.relic1}" + (f"| {self.relic2}\n" if self.relic2 is not None else "\n")
        res += f"{self.planar}"
        return res

    def equip(self):  # function to add base buffs to wearer
        return self.parseEquipment("EQUIP")

    def useMemo(self, enemyID=-1):
        self.MemoAttack = self.MemoAttack + 1
        return *self.parseEquipment(AtkType.MEMO, enemyID=enemyID), []

    def useUlt(self, enemyID=-1):
        self.ults = self.ults + 1
        return *self.parseEquipment(AtkType.ULT, enemyID=enemyID), []

    def useHit(self, enemyID=-1):
        return *self.parseEquipment("HIT", enemyID=enemyID), []

    def ownTurn(self, turn: Turn, result: Result):
        if result.atkType[0] in self.dmgDct:
            self.dmgDct[result.atkType[0]] = self.dmgDct[result.atkType[0]] + result.turnDmg
        self.dmgDct[AtkType.BRK] = self.dmgDct[AtkType.BRK] + result.wbDmg
        self.currEnergy = min(self.maxEnergy, self.currEnergy + result.errGain)
        return *self.parseEquipment("OWN", turn=turn, result=result), []

    def special(self):
        return self.name

    def handleSpecialStart(self, specialRes: Special):
        self.enemyStatus = specialRes.enemies
        return *self.parseEquipment("SPECIALS", special=specialRes), []

    def handleSpecialEnd(self, specialRes: Special):
        return *self.parseEquipment("SPECIALE", special=specialRes), []

    def allyTurn(self, turn: Turn, result: Result):
        return *self.parseEquipment("ALLY", turn=turn, result=result), []

    def enemyTurn(self, turn: Turn, result: Result):
        return *self.parseEquipment("ENEMY", turn=turn, result=result), []

    def MemoAdd(self, MemoActive: MemoActive, result: Result, MemoSummoner: MemoSummoner):
        if MemoActive == False and result.turnName == "SummonMemo":
            return True

    def MemoActive(self, MemoActive: MemoActive):
        if MemoActive == True:
            return True

    def MemoRemove(self, MemoActive: MemoActive, result: Result):
        if MemoActive == True and result.turnName == "RemoveMemo":
            return True

    def parseEquipment(self, actionType, turn=None, result=None, special=None, enemyID=-1):
        buffList, debuffList, advList, delayList = [], [], [], []
        equipmentList = [self.lightcone, self.relic1, self.planar]
        if self.relic2:
            equipmentList.append(self.relic2)

        for equipment in equipmentList:
            if actionType == AtkType.MEMO:
                buffs, debuffs, advs, delays = equipment.useMemo(enemyID)
            elif actionType == "EQUIP":
                buffs, debuffs, advs, delays = equipment.equip()
            elif actionType == "HIT":
                buffs, debuffs, advs, delays = equipment.useHit(enemyID)
            elif actionType == "SPECIALS":
                buffs, debuffs, advs, delays = equipment.specialStart(special)
            elif actionType == "SPECIALE":
                buffs, debuffs, advs, delays = equipment.specialEnd(special)
            elif actionType == "OWN":
                buffs, debuffs, advs, delays = equipment.ownTurn(turn, result)
            elif actionType == "ALLY":
                buffs, debuffs, advs, delays = equipment.allyTurn(turn, result)
            elif actionType == "ENEMY":
                buffs, debuffs, advs, delays = equipment.enemyTurn(turn, result)
            else:
                buffs, debuffs, advs, delays = [], [], [], []

            buffList.extend(buffs)
            debuffList.extend(debuffs)
            advList.extend(advs)
            delayList.extend(delays)
        return buffList, debuffList, advList, delayList

    def addEnergy(self, amount: float):
        self.currEnergy = min(self.maxEnergy, self.currEnergy + amount)

    def reduceAV(self, reduceValue: float):
        self.currAV = max(0.0, self.currAV - reduceValue)

    def changeHP(self, HpChangeValue: float):
        if HpChangeValue > 0:
            self.currHP = min(self.maxHP, self.currHP + HpChangeValue)
        elif HpChangeValue < 0:
            self.currHP = max(1.0, self.currHP + HpChangeValue)

    def getRelicScalingStats(self) -> tuple[float, float]:
        return self.relicStats.getScalingValue(self.scaling)

    def getSPD(self) -> float:
        return self.relicStats.getSPD()

    def getHPFlat(self) -> float:
        return self.relicStats.getHPFlat()

    def getHPPercent(self) -> float:
        return self.relicStats.getHPPercent()

    def getOGH(self) -> float:
        return self.relicStats.getOGH()

    def canUseUlt(self) -> bool:
        return self.currEnergy >= self.EnergyCost

    def takeTurn(self) -> str:
        res = self.turn
        self.turn = self.turn + 1
        return self.rotation[res % len(self.rotation)]

    def getTotalDMG(self) -> tuple[str, float]:
        ttl = sum(self.dmgDct.values())
        res = ""
        for key, val in self.dmgDct.items():
            res += f"-{key.name}: {val:.3f} | {val / ttl * 100 if ttl > 0 else 0:.3f}%\n"
        return res, ttl

    def getBaseStat(self):
        if self.scaling == Scaling.ATK:
            baseStat = self.baseATK
        elif self.scaling == Scaling.HP:
            baseStat = self.baseHP
        elif self.scaling == Scaling.DEF:
            baseStat = self.baseDEF
        else:
            baseStat = 0.0
        return baseStat, *self.getRelicScalingStats()

    def standardAVred(self, av: float):
        self.currAV = max(0.0, self.currAV - av)

    def bestEnemy(self, enemyID) -> int:
        if enemyID != -1:
            return enemyID
        elif self.targetPrio == Priority.DEFAULT:
            return self.defaultTarget
        else:
            sorted_enemies = sorted(self.enemyStatus, key=lambda enemy: (
            enemy.gauge if self.targetPrio == Priority.BROKEN else -enemy.gauge, -len(enemy.adjacent)))
            return sorted_enemies[0].enemyID

    @staticmethod
    def isChar() -> bool:
        return True

    @staticmethod
    def isSummon() -> bool:
        return False

    @staticmethod
    def extendLists(bl: list, dbl: list, al: list, dl: list, tl: list, nbl: list, ndbl: list, nal: list, ndl: list,
                    ntl: list):
        bl.extend(nbl)
        dbl.extend(ndbl)
        al.extend(nal)
        dl.extend(ndl)
        tl.extend(ntl)
        return bl, dbl, al, dl, tl


