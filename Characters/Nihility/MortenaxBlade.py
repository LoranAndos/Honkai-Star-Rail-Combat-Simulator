import logging

from Buff import *
from Character import Character
from Lightcones.Elation.DazzledByAFloweryWorld import DazzledByAFloweryWorld
from Lightcones.Elation.MushyShroomyAdventures import MushyShroomysAdventuresSparxie
from Planars.TengokuLivestream import TengokuLivestream
from RelicStats import RelicStats
from Relics.EverGloriousMagicalGirl import EverGloriousMagicalGirl
from Result import *
from Turn_Text import Turn
from Healing import *
from random import random
from math import floor

logger = logging.getLogger(__name__)


class MortenaxBlade(Character):
    # Standard Character Settings
    name = "MortenaxBlade"
    path = Path.NIHILITY
    element = Element.FIRE
    scaling = Scaling.HP
    baseHP = 1358
    baseATK = 543
    baseDEF = 485
    baseSPD = 107
    maxEnergy = 80
    currEnergy = 40
    ultCost = 80
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.FUA: 0}  # Adjust accordingly

    # Unique Character Properties
    hasSummon = True

    EnhancedState = False
    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT,
                 elationParticipationID=144) -> None:  # SPARXIE ID: 144
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else MushyShroomysAdventuresSparxie(role, 5)
        self.relic1 = r1 if r1 else EverGloriousMagicalGirl(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else TengokuLivestream(role)
        self.relicStats = subs if subs else RelicStats(6, 2, 2, 2, 2, 8, 2, 2, 2, 2, 9, 9, StatTypes.CR_PERCENT, StatTypes.SPD,
                                                       StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["E"]
        self.elationParticipationID = elationParticipationID

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("MortenaxBladeTraceCR", StatTypes.CR_PERCENT, 0.12, self.role))
        bl.append(Buff("MortenaxBladeTraceHP", StatTypes.HP_PERCENT, 0.10, self.role))
        bl.append(Buff("MortenaxBladeTraceDMG", StatTypes.DMG_PERCENT, 0.224, self.role))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e5MulReg = 0.55 if self.eidolon >= 5 else 0.5
        e5MulEnhanced = 1.1 if self.eidolon >= 5 else 1.0
        if self.EnhancedState:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e5MulEnhanced, 0], [10, 0], 20, self.scaling, 1, "MortenaxBladeEnhancedBasic"))
        else:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                     [e5MulReg, 0], [10, 0], 20, self.scaling, 1, "MortenaxBladeBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e5MulAoe = 0.792 if self.eidolon >= 5 else 0.72
        e5MulBounce = 0.264 if self.eidolon >= 5 else 0.24
        if self.EnhancedState:
            if self.currHP >= 0.15*self.maxHP:
                self.currHP -= 0.15*self.maxHP
            else:
                self.currHP = 1
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.SKL], [self.element],
                           [e5MulAoe, 0], [10, 0], 30, self.scaling, 0, "MortenaxBladeAOESkill"))
            for i in range(4):
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.SKL], [self.element],
                               [e5MulBounce, 0], [5, 0], 0, self.scaling, 0, "MortenaxBladeBounceSkill"))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        if self.EnhancedState == False:
            self.EnhancedState = True
            self.maxEnergy = 160
            self.ultCost = 160
            e3DefShred = 0.32 if self.eidolon >= 3 else 0.30
            e3Vul = 0.54 if self.eidolon >= 3 else 0.50
            e3CD = 0.66 if self.eidolon >= 3 else 0.60
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.NA, [AtkType.ALL], [self.element],
                     [0, 0], [0, 0], 5, self.scaling, 0, "MortenaxBladeUlt"))
            dbl.append(Debuff("MortenaxBladeUltVul", self.role, StatTypes.VULN, e3Vul, Role.ALL, [AtkType.ALL], 2))
            dbl.append(Debuff("MortenaxBladeUltShred", self.role, StatTypes.SHRED, e3DefShred, Role.ALL, [AtkType.ALL], 2))
            if self.currHP >= 0.30*self.maxHP:
                self.currHP -= 0.30*self.maxHP
            else:
                self.currHP = 1
            bl.append(Buff("MortenaxBladeCRBoost", StatTypes.CR_PERCENT, 0.20, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
            bl.append(Buff("MortenaxBladeCRBoost", StatTypes.CD_PERCENT, e3CD, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        else:
            e3EnhancedUlt = 3.24 if self.eidolon >= 3 else 3.00
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT], [self.element],
                           [e3EnhancedUlt, 0], [20, 0], 5, self.scaling, 0, "MortenaxBladeEnhancedUlt"))
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        if result.turnName == "InfiniteFury":
            self.EnhancedState = False
            self.maxEnergy = 80
            self.ultCost = 80
            bl.append(Buff("MortenaxBladeCRBoost", StatTypes.CR_PERCENT, 0, self.role, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
            bl.append(Buff("MortenaxBladeCRBoost", StatTypes.CD_PERCENT, 0, self.role, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)

        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)

        return bl, dbl, al, dl, tl, hl

    def takeTurn(self) -> str:
        return "E" if self.EnhancedState else "A"

