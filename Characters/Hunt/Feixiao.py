import logging

from Buff import *
from Character import Character
from Lightcones.Hunt.IVentureForthToHunt import VentureForthFeixiao
from Attributes import *
from Planars.DuranDynastyOfRunningWolves import DuranDynastyOfRunningWolves
from RelicStats import RelicStats
from Relics.TheWindSoaringValorous import WindSoaringYunli
from Result import Result, Special
from Turn_Text import Turn

logger = logging.getLogger(__name__)


class Feixiao(Character):
    # Standard Character Settings
    name = "Feixiao"
    path = Path.HUNT
    element = Element.WIND
    scaling = Scaling.ATK
    baseHP = 1047.8
    baseATK = 601.52
    baseDEF = 388.08
    baseSPD = 112
    maxEnergy = 12
    currEnergy = 3
    ultCost = 6
    currAV = 0
    aggro = 75
    dmgDct = {AtkType.BSC: 0, AtkType.FUA: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0,
              AtkType.TECH: 0}  # Adjust accordingly
    specialEnergy = True

    # Unique Character Properties
    fuaTrigger = True
    technique = True
    canUlt = False
    firstTurn = True
    e2Count = 6

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, eidolon: int = 0, lc=None, r1=None, r2=None,
                 pl=None, subs=None, rotation=None, targetPrio=Priority.DEFAULT):
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else VentureForthFeixiao(role)
        self.relic1 = r1 if r1 else WindSoaringYunli(role, setType=4)  # same as yunli, ult also counts as FuA
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else DuranDynastyOfRunningWolves(role)
        self.relicStats = subs if subs else RelicStats(2, 2, 2, 2, 2, 9, 2, 2, 2, 2, 10, 10, StatTypes.CR_PERCENT, StatTypes.SPD,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)  # 0 spd default
        self.rotation = rotation if rotation else ["E"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(
            Buff("FeixiaoTraceCR", StatTypes.CR_PERCENT, 0.12, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(
            Buff("FeixiaoTraceATK", StatTypes.ATK_PERCENT, 0.28, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(
            Buff("FeixiaoTraceDEF", StatTypes.DEF_PERCENT, 0.125, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("FeixiaoFuaCD", StatTypes.CD_PERCENT, 0.36, self.role, [AtkType.FUA], 1, 1, Role.SELF, TickDown.PERM))
        if self.eidolon == 6:
            bl.append(Buff("FeixiaoE6PEN", StatTypes.PEN, 0.20, self.role, [AtkType.ULT], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        basicMul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [basicMul, 0], [10, 0], 0.5, self.scaling, 1, "FeixiaoBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e2Bonus = 0.5 if self.eidolon >= 2 else 0
        e4Bonus = 5 if self.eidolon >= 4 else 0
        sklMul = 2.2 if self.eidolon >= 5 else 2.0
        fuaMul = 1.21 if self.eidolon >= 5 else 1.1
        e6Bonus = 1.4 if self.eidolon == 6 else 0
        atkType = [AtkType.FUA, AtkType.ULT, AtkType.DUKEFUA] if self.eidolon == 6 else [AtkType.FUA, AtkType.DUKEFUA]
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.SKL], [self.element],
                       [sklMul, 0], [20, 0], 0.5, self.scaling, -1, "FeixiaoSkill"))
        self.fuas = self.fuas + 1
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, atkType, [self.element],
                       [fuaMul + e6Bonus, 0], [5 + e4Bonus, 0], 0.5 + e2Bonus, self.scaling, 0, "FeixiaoSkillFUA"))
        bl.append(
            Buff("FeixiaoSkillATK", StatTypes.ATK_PERCENT, 0.48, self.role, [AtkType.ALL], 4, 1, Role.SELF, TickDown.END))
        bl.append(Buff("FeixiaoFuaDMG", StatTypes.DMG_PERCENT, 0.60, self.role, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
        if self.eidolon >= 4:
            bl.append(
                Buff("FeixiaoE4SPD", StatTypes.SPD_PERCENT, 0.08, self.role, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        dmgMul = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5] if self.eidolon >= 1 else [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        boltMul = 0.978 if self.eidolon >= 3 else 0.9
        finalMul = 1.728 if self.eidolon >= 3 else 1.6
        for i in range(6):
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE,
                           [AtkType.ULT, AtkType.FUA, AtkType.DUKEULT], [self.element], [boltMul * dmgMul[i], 0],
                           [10, 0], 0, self.scaling, 0, "FeixiaoUlt"))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE,
                       [AtkType.ULT, AtkType.FUA, AtkType.DUKEULT], [self.element], [finalMul * dmgMul[5], 0], [0, 0],
                       0, self.scaling, 0, "FeixiaoUltFinal"))
        return bl, dbl, al, dl, tl, hl

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useFua(enemyID)
        e2Bonus = 0.5 if self.eidolon >= 2 else 0
        e4Bonus = 5 if self.eidolon >= 4 else 0
        fuaMul = 1.21 if self.eidolon >= 5 else 1.1
        e6Bonus = 1.4 if self.eidolon == 6 else 0
        atkType = [AtkType.FUA, AtkType.ULT, AtkType.DUKEFUA] if self.eidolon == 6 else [AtkType.FUA, AtkType.DUKEFUA]
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, atkType, [self.element],
                       [fuaMul + e6Bonus, 0], [5 + e4Bonus, 0], 0.5 + e2Bonus, self.scaling, 0, "FeixiaoFua"))
        bl.append(Buff("FeixiaoFuaDMG", StatTypes.DMG_PERCENT, 0.60, self.role, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        if self.eidolon >= 4:
            bl.append(
                Buff("FeixiaoE4SPD", StatTypes.SPD_PERCENT, 0.08, self.role, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if turn.targeting != Targeting.NA and turn.moveName not in bonusDMG and result.turnDmg > 0:
            if self.fuaTrigger:
                self.fuaTrigger = False
                bl, dbl, al, dl, tl, hl = self.useFua(result.enemiesHit[0].enemyID)
            if AtkType.FUA in turn.atkType and self.eidolon >= 2 and self.e2Count > 0:
                self.e2Count = max(0, self.e2Count - 1)
                tl.append(
                    Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 1.0,
                         self.scaling, 0, "FeixiaoAllyEnergy(E2FUA)"))
            else:
                tl.append(
                    Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0.5,
                         self.scaling, 0, "FeixiaoAllyEnergy"))
        return bl, dbl, al, dl, tl, hl

    def takeTurn(self) -> str:
        self.fuaTrigger = True  # reset fuaTrigger on turn start
        self.firstTurn = False
        self.e2Count = 4
        return super().takeTurn()

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.canUlt = specialRes.attr1
        if self.technique:
            self.technique = False
            tl.append(
                Turn(self.name, self.role, self.bestEnemy(-1), Targeting.AOE, [AtkType.TECH], [self.element], [2.0, 0],
                     [20, 0], 1.5, self.scaling, 0, "FeixiaoTech"))
        elif specialRes.specialName == "Feixiao":
            if self.fuaTrigger and specialRes.attr2 and not self.firstTurn:
                tl.append(
                    Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0.5,
                         self.scaling, 0, "FeixiaoPityEnergy"))
        return bl, dbl, al, dl, tl, hl

    def canUseUlt(self) -> bool:
        return super().canUseUlt() if self.canUlt else False




