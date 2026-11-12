from Turn_Text import Turn
from Result import *
from Attributes import *
from Buff import *
import logging

logger = logging.getLogger(__name__)

class Memosprite:
    """Base class for memosprites (summoned allies of a Remembrance 'memomaster').

    Rules modelled here (see the memosprite research):
      * A memosprite is a separate ally with its own HP, own place in the action order and a fixed SPD.
      * It has no Energy bar of its own (subclasses may use currEnergy as a special resource, e.g. Mem's Charge).
      * It can be targeted by enemies ONLY while it is on the field (MemoActive).
      * Energy it would gain from being hit goes to its memomaster (handled in MainFunctions.addEnergy).
      * At 0 HP it disappears (it does not die): the engine calls disappear() and the memomaster must resummon it.
    """
    # Standard Character Properties
    name = "Memosprite"
    path = Path.REMEMBRANCE
    element = Element.LIGHTNING
    scaling = "ATK"
    MemoSummoner = None
    MemoSummonerName = None          # name of the memomaster character (used by the engine to route energy)
    baseHP = 0
    baseATK = 0
    baseDEF = 0
    baseELA = 0
    baseSPD = 100.0
    maxEnergy = 100.0
    EnergyCost = 100.0
    currEnergy = maxEnergy / 2
    currAV = 100.0
    currHP = 1.0
    maxHP = 1.0
    aggro = 0
    Banger = 0
    Punchline = 0
    MemoActive = False
    rotation = ["MemoAtk"]
    hasSummon = False
    specialEnergy = False
    isMemosprite = True
    pendingDisappear = False
    removeOnDisappear = ()           # buff names (on ANY target) that must be removed when this memosprite disappears

    basics = 0
    skills = 0
    ults = 0
    fuas = 0
    Adds = 0
    ElationSkills = 0
    JointAttacks = 0
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
        self.shields = []
        self.pendingDisappear = False
        # per-instance damage tracker (a class-level dict would be shared between every instance / run)
        self.dmgDct = {AtkType.MEMO: 0.0, AtkType.SPECIAL: 0.0, AtkType.BRK: 0.0}

    def __str__(self) -> str:
        res = f"{self.name} | {self.element.name}-{self.path.name} | {self.role.name} | POS:{self.pos}\n"
        res += f"{self.lightcone}\n"
        res += f"{self.relic1}" + (f"| {self.relic2}\n" if self.relic2 is not None else "\n")
        res += f"{self.planar}"
        return res

    # ------------------------------------------------------------------ actions
    # Every action returns the same 7-tuple the engine expects from a character:
    # (buffs, debuffs, advances, delays, turns, healings, shields)

    def equip(self):  # function to add base buffs to wearer (6-tuple, like Character.equip)
        if self.lightcone is not None:
            self.lightcone.wearer = self
        return self.parseEquipment("EQUIP")

    def useMemo(self, enemyID=-1):
        self.MemoAttack = self.MemoAttack + 1
        bl, dbl, al, dl, hl, sl = self.parseEquipment(AtkType.MEMO, enemyID=enemyID)
        return bl, dbl, al, dl, [], hl, sl

    def useUlt(self, enemyID=-1):
        self.ults = self.ults + 1
        bl, dbl, al, dl, hl, sl = self.parseEquipment(AtkType.ULT, enemyID=enemyID)
        return bl, dbl, al, dl, [], hl, sl

    def useHit(self, enemyID=-1):
        bl, dbl, al, dl, hl, sl = self.parseEquipment("HIT", enemyID=enemyID)
        return bl, dbl, al, dl, [], hl, sl

    def ownTurn(self, turn: Turn, result: Result):
        if result.atkType[0] in self.dmgDct:
            self.dmgDct[result.atkType[0]] = self.dmgDct[result.atkType[0]] + result.turnDmg + getattr(result, "ElationturnDMG", 0.0)
        self.dmgDct[AtkType.BRK] = self.dmgDct[AtkType.BRK] + result.wbDmg
        # NOTE: a memosprite has no Energy bar. Subclasses that use currEnergy as a special resource
        # (e.g. Mem's Charge) manage it themselves, so errGain is intentionally NOT added here.
        bl, dbl, al, dl, hl, sl = self.parseEquipment("OWN", turn=turn, result=result)
        return bl, dbl, al, dl, [], hl, sl

    def special(self):
        return self.name

    def handleSpecialStart(self, specialRes: Special):
        self.enemyStatus = specialRes.enemies
        bl, dbl, al, dl, hl, sl = self.parseEquipment("SPECIALS", special=specialRes)
        return bl, dbl, al, dl, [], hl, sl

    def handleSpecialEnd(self, specialRes: Special):
        bl, dbl, al, dl, hl, sl = self.parseEquipment("SPECIALE", special=specialRes)
        return bl, dbl, al, dl, [], hl, sl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl, sl = self.parseEquipment("ALLY", turn=turn, result=result)
        return bl, dbl, al, dl, [], hl, sl

    def disappear(self):
        """Called by the engine once pendingDisappear is set (HP reached 0). Subclasses extend this."""
        self.pendingDisappear = False
        self.MemoActive = False
        return [], [], [], [], [], [], []

    # --------------------------------------------------------------- equipment
    def parseEquipment(self, actionType, turn=None, result=None, special=None, enemyID=-1):
        buffList, debuffList, advList, delayList, healingList, shieldList = [], [], [], [], [], []
        equipmentList = [self.lightcone, self.relic1, self.planar]
        if self.relic2:
            equipmentList.append(self.relic2)

        for equipment in equipmentList:
            if actionType == AtkType.MEMO:
                buffs, debuffs, advs, delays, heals, shields = equipment.useMemo(enemyID)
            elif actionType == AtkType.ULT:
                buffs, debuffs, advs, delays, heals, shields = equipment.useUlt(enemyID)
            elif actionType == "EQUIP":
                buffs, debuffs, advs, delays, heals, shields = equipment.equip()
            elif actionType == "HIT":
                buffs, debuffs, advs, delays, heals, shields = equipment.useHit(enemyID)
            elif actionType == "SPECIALS":
                buffs, debuffs, advs, delays, heals, shields = equipment.specialStart(special)
            elif actionType == "SPECIALE":
                buffs, debuffs, advs, delays, heals, shields = equipment.specialEnd(special)
            elif actionType == "OWN":
                buffs, debuffs, advs, delays, heals, shields = equipment.ownTurn(turn, result)
            elif actionType == "ALLY":
                buffs, debuffs, advs, delays, heals, shields = equipment.allyTurn(turn, result)
            else:
                buffs, debuffs, advs, delays, heals, shields = [], [], [], [], [], []

            buffList.extend(buffs)
            debuffList.extend(debuffs)
            advList.extend(advs)
            delayList.extend(delays)
            healingList.extend(heals)
            shieldList.extend(shields)
        return buffList, debuffList, advList, delayList, healingList, shieldList

    # ------------------------------------------------------------------- state
    def addEnergy(self, amount: float):
        self.currEnergy = min(self.maxEnergy, self.currEnergy + amount)

    def addPunchLine(self, amount: float):
        self.Punchline = self.Punchline + amount

    def reduceAV(self, reduceValue: float):
        self.currAV = max(0.0, self.currAV - reduceValue)

    def ChangeHpValue(self, HPChangingValue: float):
        """Unlike a normal character (floored at 1 HP in this sim) a memosprite CAN reach 0 HP:
        it then flags pendingDisappear and the engine calls disappear()."""
        if not self.MemoActive:
            return  # not on the field: cannot be damaged or healed
        if HPChangingValue < 0:
            self.currHP = max(0.0, self.currHP + HPChangingValue)
            if self.currHP <= 0:
                self.pendingDisappear = True
        elif HPChangingValue > 0:
            self.currHP = min(self.maxHP, self.currHP + HPChangingValue)

    def getTotalShieldHP(self) -> float:
        if not self.shields:
            return 0.0
        return sum(s.currentAmount for s in self.shields)

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

    def getBaseStat(self, scaling: Scaling = None):
        scaling = scaling if scaling is not None else self.scaling
        if scaling == Scaling.ATK:
            baseStat = self.baseATK + self.lightcone.baseATK
            return baseStat, *self.getRelicScalingStats()
        elif scaling == Scaling.HP:
            baseStat = self.baseHP + self.lightcone.baseHP
            return baseStat, *self.getRelicScalingStats()
        elif scaling == Scaling.DEF:
            baseStat = self.baseDEF + self.lightcone.baseDEF
            return baseStat, *self.getRelicScalingStats()
        elif scaling == Scaling.ELA:
            return 0, 0, 0  # no base, no relic contribution for ELA
        else:
            return 0, 0, 0

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
    def extendLists(bl: list, dbl: list, al: list, dl: list, tl: list, hl: list, sl: list, nbl: list, ndbl: list, nal: list,
                    ndl: list, ntl: list, nhl: list, nsl: list):
        bl.extend(nbl)
        dbl.extend(ndbl)
        al.extend(nal)
        dl.extend(ndl)
        tl.extend(ntl)
        hl.extend(nhl)
        sl.extend(nsl)
        return bl, dbl, al, dl, tl, hl, sl