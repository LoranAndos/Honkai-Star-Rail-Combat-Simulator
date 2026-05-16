import logging

from Buff import *
from Character import Character
from Lightcones.Hunt.TheFinaleOfALie import TheFinaleOfALie
from Planars.CityOfConvergingStars import CityOfConvergingStars
from RelicStats import RelicStats
from Relics.TheAshblazingGrandDuke import DukeAshveil
from Result import *
from Turn_Text import Turn
from Healing import *
from math import floor
from HPChecks import getEnemyHPRatio

logger = logging.getLogger(__name__)


class Ashveil(Character):
    # Standard Character Settings
    name = "Ashveil"
    path = Path.HUNT
    element = Element.LIGHTNING
    scaling = Scaling.ATK
    baseHP = 854
    baseATK = 776
    baseDEF = 388
    baseSPD = 106
    maxEnergy = 150
    currEnergy = 75
    ultCost = 150
    currAV = 0
    aggro = 75
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.FUA: 0}  # Adjust accordingly

    # Unique Character Properties
    LowestHPEnemyID = 0
    Charge = 2
    ChargeCap = 3
    Gluttony = 0
    GluttonyExtraDamage = 0
    GluttonyObtained = 0
    Counter = 0
    UltFUA = False
    Tech = True
    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else TheFinaleOfALie(role, 1)
        self.relic1 = r1 if r1 else DukeAshveil(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else CityOfConvergingStars(role)
        self.relicStats = subs if subs else RelicStats(6, 2, 2, 2, 7, 2, 2, 2, 2, 2, 12, 4, StatTypes.CR_PERCENT, StatTypes.SPD,
                                                       StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["E"]
        self.GluttonyCap = 18 if self.eidolon >= 2 else 12

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        e5DefShred = 0.44 if self.eidolon >= 5 else 0.4
        bl.append(Buff("AshveilTraceCD", StatTypes.CD_PERCENT, 0.373, self.role))
        bl.append(Buff("AshveilTraceATK", StatTypes.ATK_PERCENT, 0.10, self.role))
        bl.append(Buff("AshveilTraceDMG", StatTypes.DMG_PERCENT, 0.144, self.role))
        bl.append(Buff("AshveilTrace2DMG", StatTypes.DMG_PERCENT, 0.8, self.role, [AtkType.FUA], 1, 1, self.role, TickDown.PERM))
        bl.append(Buff("AshveilTrace3CD", StatTypes.CD_PERCENT, 0.40, Role.ALL, [AtkType.ALL], 1, 1, self.role, TickDown.PERM))
        bl.append(Buff("AshveilTrace3FUACD", StatTypes.CD_PERCENT, 0.8, Role.ALL, [AtkType.FUA], 1, 1, self.role, TickDown.PERM))
        dbl.append(Debuff("AshveilBaitShred", self.role, StatTypes.SHRED, e5DefShred, Role.ALL, [AtkType.ALL], 1000))
        if self.eidolon >= 6:
            dbl.append(Debuff("AshveilE6SHRED", self.role, StatTypes.SHRED, 0.20, Role.ALL, [AtkType.ALL], 1000))
        return bl, dbl, al, dl, hl

    def _updateE1VULN(self, dbl: list):
        if self.eidolon < 1:
            return
        for enemy in self.enemyStatus:
            vulnVal = 0.36 if getEnemyHPRatio(enemy) <= 0.5 else 0.24
            dbl.append(Debuff(f"AshveilE1VULN_{enemy.enemyID}", self.role, StatTypes.VULN, vulnVal, enemy.enemyID, [AtkType.ALL], 1,1, Targeting.SINGLE))

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.LowestHPEnemyID, Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20, self.scaling, 1, "AshveilBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e5MulBig = 2.2 if self.eidolon >= 5 else 2.0
        e5MulSmall = 1.1 if self.eidolon >= 5 else 1.0
        tl.append(Turn(self.name, self.role, self.LowestHPEnemyID, Targeting.SINGLE, [AtkType.SKL], [self.element],
                       [e5MulBig+e5MulSmall, 0], [20, 0], 30, self.scaling, -1+1, "AshveilSkill"))
        self.Gluttony = min(self.Gluttony + 1, self.GluttonyCap)
        self.GluttonyObtained += 1
        logger.debug(f"{self.name} has obtained 1 gluttony stack from Skill.")
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e3UltMul = 4.4 if self.eidolon >= 3 else 4.0
        if self.eidolon >= 4:
            bl.append(Buff("AshveilE4Atk", StatTypes.ATK_PERCENT, 0.40, self.role, [AtkType.ALL], 3, 1, self.role, TickDown.END))
        tl.append(Turn(self.name, self.role, self.LowestHPEnemyID, Targeting.SINGLE, [AtkType.ULT], [self.element],
                       [e3UltMul, 0], [30, 0], 5, self.scaling, 0, "AshveilUlt"))
        self.UltFUA = True
        self.Charge = min(self.Charge + 3, 3)
        self.Gluttony = min(self.Gluttony + 2, self.GluttonyCap)
        self.GluttonyExtraDamage = floor(self.Gluttony/4)
        logger.debug(f"{self.name} has {self.Gluttony} gluttony stacks before ult.")
        self.GluttonyObtained += 2
        logger.debug(f"{self.name} has obtained 2 gluttony stacks from Ult.")
        self.Gluttony = max(self.Gluttony-self.GluttonyExtraDamage*4,0)
        return bl, dbl, al, dl, tl, hl

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useFua(enemyID)
        e3MulExtra = 2.2 if self.eidolon >= 3 else 2.0
        e5Mul = 2.2 if self.eidolon >= 5 else 2.0
        if self.UltFUA == False:
            self.Charge = max(self.Charge-1,0)
            bl.append(Buff("AshveilTrace2GluttonyDMG", StatTypes.DMG_PERCENT, min(0.1 * self.Gluttony, 0.1 * self.GluttonyCap), self.role, [AtkType.FUA], 1, 1, self.role, TickDown.END))
        else:
            bl.append(Buff("AshveilTrace2GluttonyDMG", StatTypes.DMG_PERCENT, 0.1*self.GluttonyExtraDamage*2, self.role, [AtkType.FUA], 1, 1, self.role,TickDown.END))
        tl.append(Turn(self.name, self.role, self.LowestHPEnemyID, Targeting.SINGLE, [AtkType.FUA], [self.element],
                       [e5Mul + e3MulExtra*self.GluttonyExtraDamage, 0], [5, 0], 5, self.scaling, 0, "AshveilFUA"))
        if self.eidolon >= 2:
            self.Gluttony = min(self.Gluttony+floor(0.35*self.GluttonyExtraDamage*4),12)
            self.GluttonyObtained += floor(0.35*self.GluttonyExtraDamage*4)
        self.GluttonyExtraDamage = 0
        self.UltFUA = False
        self.Gluttony = min(self.Gluttony+2,self.GluttonyCap)
        self.GluttonyObtained += 2
        logger.debug(f"{self.name} has obtained 2 gluttony stacks from FUA.")
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        self._updateE1VULN(dbl)
        if turn.moveName == "AshveilUlt":
            return self.useFua(-1)
        if result.turnName == "AshveilFUA" and result.numKills > 0:
            self.Gluttony = min(self.Gluttony + result.numKills, self.GluttonyCap)
            self.GluttonyObtained += result.numKills
            logger.debug(f"{self.name} has obtained {result.numKills} gluttony stacks from kill.")
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        self._updateE1VULN(dbl)
        if (turn.moveName not in bonusDMG) and result.enemiesHit and result.turnDmg > 0:
            bl.append(Buff(f"AshveilTalentEnergy{self.Counter}", StatTypes.ERR_F, 8, self.role, [AtkType.ALL], 1, 1, self.role, TickDown.END))
            self.Counter += 1
        if (turn.moveName not in bonusDMG) and result.enemiesHit and result.turnDmg > 0 and self.Charge > 0:
            bl, dbl, al, dl, tl, hl = self.extendLists(bl, dbl, al, dl, tl, hl, *self.useFua(-1))
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.LowestHPEnemyID = specialRes.attr1
        if self.Tech:
            tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.TECH], [self.element], [1.0, 0], [0, 0], 0,self.scaling, 0, "AshveilTech"))
            self.Charge = min(self.Charge+1,3)
            self.Tech = False
        if self.eidolon == 6:
            bl.append(Buff("AshveilE6GluttonyDMG", StatTypes.DMG_PERCENT, 0.04 * min(self.GluttonyObtained,30), self.role, [AtkType.ALL],1, 1, self.role, TickDown.PERM))
        return bl, dbl, al, dl, tl, hl

    def canUseUlt(self) -> bool:
        return super().canUseUlt() if self.Charge == 0 else False