import logging

from Buff import *
from Character import Character
from Lightcones.Nihility.ReforgedInHellfire import ReforgedInHellfire
from Lightcones.Nihility.ResolutionShinesAsPearlsOfSweat import ResolutionMortenaxBlade
from Lightcones.Nihility.GoodNightAndSleepWell import GoodNightAndSleepWell
from Planars.BoneCollectionsSereneDemesne import BoneCollectionsSereneDemesne
from RelicStats import RelicStats
from Relics.DivineQueryingMasterSmith import DivineQueryMasterSmith
from Result import *
from Turn_Text import Turn
from Healing import *
from math import floor

logger = logging.getLogger(__name__)


class Ashveil(Character):
    # Standard Character Settings
    name = "MortenaxBlade"
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
    UltFUA = False
    Tech = True
    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else GoodNightAndSleepWell(role, 5)
        self.relic1 = r1 if r1 else DivineQueryMasterSmith(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else BoneCollectionsSereneDemesne(role)
        self.relicStats = subs if subs else RelicStats(6, 2, 2, 2, 7, 2, 2, 2, 2, 2, 12, 4, StatTypes.CR_PERCENT, StatTypes.SPD,
                                                       StatTypes.HP_PERCENT, StatTypes.ERR_PERCENT)
        self.rotation = rotation if rotation else ["E"]
        self.GluttonyCap = 18 if self.eidolon >= 2 else 12

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        e5DefShred = 0.44 if self.eidolon >= 5 else 0.4
        bl.append(Buff("AshveilTraceCD", StatTypes.CD_PERCENT, 0.373, self.role))
        bl.append(Buff("AshveilTraceATK", StatTypes.ATK_PERCENT, 0.10, self.role))
        bl.append(Buff("AshveilTraceDMG", StatTypes.DMG_PERCENT, 0.144, self.role))
        dbl.append(Debuff("AshveilBaitShred", self.role, StatTypes.SHRED, e5DefShred, Role.ALL, [AtkType.ALL], 1000))
        return bl, dbl, al, dl, hl

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
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e3UltMul = 4.4 if self.eidolon >= 3 else 4.0
        tl.append(Turn(self.name, self.role, self.LowestHPEnemyID, Targeting.SINGLE, [AtkType.ULT], [self.element],
                       [e3UltMul, 0], [30, 0], 5, self.scaling, 0, "AshveilUltimate"))
        self.UltFUA = True
        self.Charge = min(self.Charge + 3, 3)
        self.GluttonyExtraDamage = floor(self.Gluttony/4)
        self.Gluttony = max(self.Gluttony-self.GluttonyExtraDamage*4,0)
        return bl, dbl, al, dl, tl, hl

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useFua(enemyID)
        e3MulExtra = 2.2 if self.eidolon >= 3 else 2.0
        e5Mul = 2.2 if self.eidolon >= 5 else 2.0
        bl.append(Buff("AshveilFUAEnergy", StatTypes.ERR_F, 8,self.role, [AtkType.ALL], 1, 3, self.role, TickDown.START))
        if self.UltFUA == False:
            self.Charge = max(self.Charge-1,0)
        tl.append(Turn(self.name, self.role, self.LowestHPEnemyID, Targeting.SINGLE, [AtkType.FUA], [self.element],
                       [e5Mul + e3MulExtra*self.GluttonyExtraDamage, 0], [5, 0], 5, self.scaling, 0, "AshveilFUA"))
        self.GluttonyExtraDamage = 0
        self.UltFUA = False
        self.Gluttony = min(self.Gluttony+2,self.GluttonyCap)
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        if turn.moveName == "AshveilUltimate":
            return self.useFua(-1)
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if (turn.moveName not in bonusDMG) and result.enemiesHit and result.turnDmg > 0 and self.LowestHPEnemyID in result.enemiesHit and self.Charge > 0:
            return self.useFua(-1)
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.LowestHPEnemyID = specialRes.attr1
        if self.Tech:
            tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.TECH], [self.element], [1.0, 0], [0, 0], 0,self.scaling, 0, "AshveilTech"))
            self.Charge = min(self.Charge+1,3)
            self.Tech = False
        return bl, dbl, al, dl, tl, hl
