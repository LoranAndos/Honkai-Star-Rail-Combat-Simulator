from Turn import Turn
from Result import *
from Misc import *
import logging

logger = logging.getLogger(__name__)


class Character:
    # Standard Character Properties
    name = "Character"
    path = Path.HUNT
    element = Element.LIGHTNING
    scaling = "ATK"
    baseHP = 0
    baseATK = 0
    baseDEF = 0
    baseSPD = 100.0
    maxEnergy = 100.0
    ultCost = 100.0
    currEnergy = maxEnergy / 2
    currAV = 100.0
    rotation = ["E", "A", "A"]
    dmgDct = {AtkType.BSC: 0.0, AtkType.SKL: 0.0, AtkType.ULT: 0.0, AtkType.BRK: 0.0, AtkType.FUA: 0.0, AtkType.ADD: 0.0, AtkType.MEMO: 0.0}
    hasSummon = False
    specialEnergy = False
    basics = 0
    skills = 0
    ults = 0
    fuas = 0
    Adds = 0
    MemoAttack = 0
    turn = 0
    lightcone = None
    relic1 = None
    relic2 = None
    planar = None
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
        res = f"{self.name} E{self.eidolon} | {self.element.name}-{self.path.name} | {self.role.name} | POS:{self.pos}\n"
        res += f"{self.lightcone}\n"
        res += f"{self.relic1}" + (f"| {self.relic2}\n" if self.relic2 is not None else "\n")
        res += f"{self.planar}"
        return res

    def equip(self):  # function to add base buffs to wearer
        return self.parseEquipment("EQUIP")

    def useSkl(self, enemyID=-1):
        self.skills = self.skills + 1
        return *self.parseEquipment(AtkType.SKL, enemyID=enemyID), []

    def useBsc(self, enemyID=-1):
        self.basics = self.basics + 1
        return *self.parseEquipment(AtkType.BSC, enemyID=enemyID), []

    def useUlt(self, enemyID=-1):
        self.ults = self.ults + 1
        return *self.parseEquipment(AtkType.ULT, enemyID=enemyID), []

    def useFua(self, enemyID=-1):
        self.fuas = self.fuas + 1
        return *self.parseEquipment(AtkType.FUA, enemyID=enemyID), []

    def useAdd(self, enemyID=-1):
        self.Adds = self.Adds + 1
        return *self.parseEquipment(AtkType.ULT, enemyID=enemyID), []

    def useMemo(self, enemyID=-1):
        self.MemoAttack = self.MemoAttack + 1
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

    def parseEquipment(self, actionType, turn=None, result=None, special=None, enemyID=-1):
        buffList, debuffList, advList, delayList = [], [], [], []
        equipmentList = [self.lightcone, self.relic1, self.planar]
        if self.relic2:
            equipmentList.append(self.relic2)

        for equipment in equipmentList:
            if actionType == AtkType.BSC:
                buffs, debuffs, advs, delays = equipment.useBsc(enemyID)
            elif actionType == AtkType.SKL:
                buffs, debuffs, advs, delays = equipment.useSkl(enemyID)
            elif actionType == AtkType.ULT:
                buffs, debuffs, advs, delays = equipment.useUlt(enemyID)
            elif actionType == AtkType.FUA:
                buffs, debuffs, advs, delays = equipment.useFua(enemyID)
            elif actionType == AtkType.ADD:
                buffs, debuffs, advs, delays = equipment.useAdd(enemyID)
            elif actionType == AtkType.MEMO:
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

    def getRelicScalingStats(self) -> tuple[float, float]:
        return self.relicStats.getScalingValue(self.scaling)

    def getSPD(self) -> float:
        return self.relicStats.getSPD()

    def canUseUlt(self) -> bool:
        return self.currEnergy >= self.ultCost

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
            baseStat = self.baseATK + self.lightcone.baseATK
        elif self.scaling == Scaling.HP:
            baseStat = self.baseHP + self.lightcone.baseHP
        elif self.scaling == Scaling.DEF:
            baseStat = self.baseDEF + self.lightcone.baseDEF
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


