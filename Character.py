from Turn_Text import Turn
from Result import *
from Attributes import *
import logging

logger = logging.getLogger(__name__)


class CharacterMeta(type):
    """Metaclass that logs SharedPunchline changes"""

    @property
    def SharedPunchline(cls):
        return cls._SharedPunchline_value

    @SharedPunchline.setter
    def SharedPunchline(cls, value):
        old = getattr(cls, '_SharedPunchline_value', 0)
        cls._SharedPunchline_value = value
        logging.warning(f"    PUNCH  > SharedPunchline: {old:.1f} -> {value:.1f}")

class Character(metaclass=CharacterMeta):
    # Standard Character Properties
    name = "Character"
    path = Path.HUNT
    element = Element.LIGHTNING
    scaling = "ATK"
    baseHP = 0
    baseATK = 0
    baseDEF = 0
    baseELA = 0
    baseSPD = 100.0
    ElationID = 0
    maxEnergy = 100.0
    ultCost = 100.0
    currEnergy = maxEnergy / 2
    currAV = 100.0
    currHP = 1.0
    maxHP = 1.0
    aggro = 0
    # Elation Properties
    Banger = 0
    _SharedPunchline_value = 0
    ahaFixedPunchline = False
    ahaFixedPunchlineValue = 20
    ahaYaoGuangUlt = False
    EMCUlt = False
    PearlUlt = False
    ahaElaDMGBoost = 1.0
    savedPunchline = 0
    prePunchline = 0
    totalPunchline = 0
    # Standard Character Properties
    _current_enemy_team = None
    _current_player_team = None
    _elation_characters_registry = {}
    rotation = ["E", "A", "A"]
    dmgDct = {AtkType.BSC: 0.0, AtkType.SKL: 0.0, AtkType.ULT: 0.0, AtkType.BRK: 0.0, AtkType.FUA: 0.0, AtkType.ADD: 0.0, AtkType.ELABANGER: 0, AtkType.ELAPUNCH: 0, AtkType.MEMO: 0.0}
    hasSummon = False
    hasMemosprite = False
    specialEnergy = False
    basics = 0
    skills = 0
    ults = 0
    fuas = 0
    Adds = 0
    ElationSkills = 0
    JointAttacks = 0
    MemoAttack = 0
    turn = 0
    lightcone = None
    relic1 = None
    relic2 = None
    planar = None
    enemyStatus = []
    shields = []  # active Shield instances currently absorbing damage for this character

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
        self.shields = []  # per-instance list of active Shield objects
        # dmgDct is a mutable dict — without this, every instance shares the
        # single class-level dict object, so damage silently accumulates
        # across every Character ever instantiated in the process (all runs,
        # all teams) instead of resetting per-instance/per-run.
        self.dmgDct = {AtkType.BSC: 0.0, AtkType.SKL: 0.0, AtkType.ULT: 0.0, AtkType.BRK: 0.0, AtkType.SBK: 0.0, AtkType.FUA: 0.0,
                       AtkType.ADD: 0.0, AtkType.DOT: 0.0, AtkType.TECH: 0.0, AtkType.ELABANGER: 0.0, AtkType.ELAPUNCH: 0.0, AtkType.MEMO: 0.0,
                        AtkType.SPECIAL: 0.0}

    def __str__(self) -> str:
        res = f"{self.name} E{self.eidolon} | {self.element.name}-{self.path.name} | {self.role.name} | POS:{self.pos}\n"
        res += f"{self.lightcone}\n"
        res += f"{self.relic1}" + (f"| {self.relic2}\n" if self.relic2 is not None else "\n")
        res += f"{self.planar}"
        return res

    def equip(self):  # function to add base buffs to wearer
        self.lightcone.wearer = self
        return self.parseEquipment("EQUIP")

    def useSkl(self, enemyID=-1):
        self.skills = self.skills + 1
        bl, dbl, al, dl, hl, sl = self.parseEquipment(AtkType.SKL, enemyID=enemyID)
        return bl, dbl, al, dl, [], hl, sl

    def useBsc(self, enemyID=-1):
        self.basics = self.basics + 1
        bl, dbl, al, dl, hl, sl = self.parseEquipment(AtkType.BSC, enemyID=enemyID)
        return bl, dbl, al, dl, [], hl, sl

    def useUlt(self, enemyID=-1):
        self.ults = self.ults + 1
        bl, dbl, al, dl, hl, sl = self.parseEquipment(AtkType.ULT, enemyID=enemyID)
        return bl, dbl, al, dl, [], hl, sl

    def useFua(self, enemyID=-1):
        self.fuas = self.fuas + 1
        bl, dbl, al, dl, hl, sl = self.parseEquipment(AtkType.FUA, enemyID=enemyID)
        return bl, dbl, al, dl, [], hl, sl

    def useAdd(self, enemyID=-1):
        self.Adds = self.Adds + 1
        bl, dbl, al, dl, hl, sl = self.parseEquipment(AtkType.ADD, enemyID=enemyID)
        return bl, dbl, al, dl, [], hl, sl

    def useElaSkill(self, enemyID=-1):
        self.ElationSkills = self.ElationSkills + 1
        bl, dbl, al, dl, hl, sl = self.parseEquipment(AtkType.ELAPUNCH, enemyID=enemyID)
        return bl, dbl, al, dl, [], hl, sl

    def useJointAttack(self, enemyID=-1):
        self.JointAttacks = self.JointAttacks + 1
        bl, dbl, al, dl, hl, sl = self.parseEquipment(AtkType.FUA, enemyID=enemyID)
        return bl, dbl, al, dl, [], hl, sl

    def useMemo(self, enemyID=-1):
        self.MemoAttack = self.MemoAttack + 1
        bl, dbl, al, dl, hl, sl = self.parseEquipment(AtkType.MEMO, enemyID=enemyID)
        return bl, dbl, al, dl, [], hl, sl

    def useHit(self, enemyID=-1):
        bl, dbl, al, dl, hl, sl = self.parseEquipment("HIT", enemyID=enemyID)
        return bl, dbl, al, dl, [], hl, sl

    def ownTurn(self, turn: Turn, result: Result):
        if result.atkType[0] in self.dmgDct:
            self.dmgDct[result.atkType[0]] = self.dmgDct[result.atkType[0]] + result.turnDmg + result.ElationturnDMG
        self.dmgDct[AtkType.BRK] = self.dmgDct[AtkType.BRK] + result.wbDmg
        self.currEnergy = min(self.maxEnergy, self.currEnergy + result.errGain)
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

    def parseEquipment(self, actionType, turn=None, result=None, special=None, enemyID=-1):
        buffList, debuffList, advList, delayList, healingList, shieldList = [], [], [], [], [], []
        equipmentList = [self.lightcone, self.relic1, self.planar]
        if self.relic2:
            equipmentList.append(self.relic2)

        for equipment in equipmentList:
            if actionType == AtkType.BSC:
                buffs, debuffs, advs, delays, heals, shields = equipment.useBsc(enemyID)
            elif actionType == AtkType.SKL:
                buffs, debuffs, advs, delays, heals, shields = equipment.useSkl(enemyID)
            elif actionType == AtkType.ULT:
                buffs, debuffs, advs, delays, heals, shields = equipment.useUlt(enemyID)
            elif actionType == AtkType.FUA:
                buffs, debuffs, advs, delays, heals, shields = equipment.useFua(enemyID)
            elif actionType == AtkType.ADD:
                buffs, debuffs, advs, delays, heals, shields = equipment.useAdd(enemyID)
            elif actionType == AtkType.ELAPUNCH:
                buffs, debuffs, advs, delays, heals, shields = equipment.useElaSkill(enemyID)
            elif actionType == AtkType.MEMO:
                buffs, debuffs, advs, delays, heals, shields = equipment.useMemo(enemyID)
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

    def addEnergy(self, amount: float):
        self.currEnergy = min(self.maxEnergy, self.currEnergy + amount)

    def addPunchLine(self, amount: float):
        self.Punchline = self.Punchline + amount
        self.totalPunchline = self.totalPunchline + amount

    def reduceAV(self, reduceValue: float):
        self.currAV = max(0.0, self.currAV - reduceValue)

    def ChangeHpValue(self, HPChangingValue: float):
        if HPChangingValue < 0:
            self.currHP = max(1.0,self.currHP + HPChangingValue)
        if HPChangingValue > 0:
            self.currHP = min(self.maxHP, self.currHP + HPChangingValue)

    def get_alive_enemy_count(self):
        if Character._current_enemy_team is None:
            return 3
        alive = len([e for e in Character._current_enemy_team if hasattr(e, 'currHP') and e.currHP > 0])
        return max(1, alive)

    def getTotalShieldHP(self) -> float:
        """Sum of currentAmount across all active shields on this character."""
        if not hasattr(self, 'shields') or not self.shields:
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
            return 0, 0, 0  # ← no base, no relic contribution for ELA
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
    def extendLists(bl: list, dbl: list, al: list, dl: list, tl: list, hl: list, sl: list, nbl: list, ndbl: list, nal: list, ndl: list,
                    ntl: list, nhl: list, nsl: list):
        bl.extend(nbl)
        dbl.extend(ndbl)
        al.extend(nal)
        dl.extend(ndl)
        tl.extend(ntl)
        hl.extend(nhl)
        sl.extend(nsl)
        return bl, dbl, al, dl, tl, hl, sl

    @classmethod
    def set_combat_context(cls, enemy_team, player_team):
        """Set the combat context for all character instances during initialization"""
        cls._current_enemy_team = enemy_team
        cls._current_player_team = player_team
        logger.debug(f"Combat context set: {len(enemy_team)} enemies, {len(player_team)} players")

    @classmethod
    def register_elation_character(cls, character):
        """Register an Elation character for Banger conversion tracking"""
        if hasattr(character, 'elationParticipationID') and character.elationParticipationID is not None:
            cls._elation_characters_registry[character.elationParticipationID] = character
            logger.debug(f"Registered {character.name} (ID: {character.elationParticipationID})")

    @property
    def SharedPunchline(self):
        """Instance-level access to class SharedPunchline"""
        return Character._SharedPunchline_value

    @SharedPunchline.setter
    def SharedPunchline(self, value):
        """Instance-level setter that logs changes"""
        old = Character._SharedPunchline_value
        Character._SharedPunchline_value = value
        logging.warning(f"    PUNCH  > SharedPunchline: {old:.1f} -> {value:.1f}")