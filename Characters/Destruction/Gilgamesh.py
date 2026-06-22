import logging

from Buff import *
from Character import Character
from Lightcones.Erudition.FlickeringStars import FlickeringStars
from Lightcones.Erudition.EternalCalculus import EternalCalculus
from Planars.RutilantArena import RutilantArena
from Planars.TengokuLivestream import TengokuLivestream
from RelicStats import RelicStats
from Relics.GeniusOfBrilliantStars import GeniusOfBrilliantStars
from Result import *
from Turn_Text import Turn
from Delay_Text import Advance
from Healing import *

logger = logging.getLogger(__name__)


class Gilgamesh(Character):
    # Standard Character Settings
    name = "Gilgamesh"
    path = Path.DESTRUCTION
    element = Element.LIGHTNING
    scaling = Scaling.ATK
    baseHP = 1125
    baseATK = 718
    baseDEF = 509
    baseSPD = 97
    maxEnergy = 360
    currEnergy = 180
    ultCost = 360
    currAV = 0
    aggro = 125
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.FUA: 0}  # Adjust accordingly

    # Unique Character Properties
    Interest = 0
    InterestPiqued = False
    JointCounter = 0
    SaberInTeam = False
    Tech = True

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope
    # With Sparkle:
    # self.relicStats = subs if subs else RelicStats(2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 14, 9, StatTypes.CR_PERCENT, StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT)

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else EternalCalculus(role, 5)
        self.relic1 = r1 if r1 else GeniusOfBrilliantStars(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else RutilantArena(role)
        self.relicStats = subs if subs else RelicStats(8, 2, 2, 2, 2, 3, 2, 2, 2, 2, 14, 2, StatTypes.CR_PERCENT, StatTypes.SPD_PERCENT,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["E"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("GilgameshTraceATK", StatTypes.ATK, 0.18, self.role))
        bl.append(Buff("GilgameshTraceCR", StatTypes.CR_PERCENT, 0.187, self.role))
        bl.append(Buff("GilgameshTraceDMG", StatTypes.DMG_PERCENT, 0.08, self.role))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20, self.scaling, 1, "GilgameshBasic"))
        self.JointCounter += 1
        logger.debug(f"Gilgamesh JointCounter increased by one, current count: {self.JointCounter}")
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e3Shred = 0.33 if self.eidolon >= 3 else 0.30
        e3MulMain = 3.08 if self.eidolon >= 3 else 2.80
        e3MulSide = 1.54 if self.eidolon >= 3 else 1.40
        bl.append(Buff("GilgameshSKLShred", StatTypes.SHRED, e3Shred, self.role, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.BLAST, [AtkType.SKL], [self.element],
                       [e3MulMain, e3MulSide], [20, 10], 30, self.scaling, 0, "GilgameshSkill"))
        self.JointCounter += 1
        logger.debug(f"Gilgamesh JointCounter increased by one, current count: {self.JointCounter}")
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        e5MulAll = 4.40 if self.eidolon >= 5 else 4.00
        e5MulExtra = 1.10 if self.eidolon >= 5 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT], [self.element],
                       [e5MulAll, 0], [40, 0], 0, self.scaling, 0, "GilgameshUltAll"))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ULT], [self.element],
                       [e5MulExtra*10, 0], [2*10, 0], 5, self.scaling, 0, "GilgameshUltSingle"))
        self.JointCounter += 1
        logger.debug(f"Gilgamesh JointCounter increased by one, current count: {self.JointCounter}")
        return bl, dbl, al, dl, tl, hl

    def useJointAttack(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useJointAttack(enemyID)
        e3Mult = 3.3 if self.eidolon>= 3 else 3.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.FUA],
                       [self.element], [e3Mult, 0], [20, 0], 10, self.scaling, 0, "GilgameshJointAttack"))
        self.Interest += 3
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        if self.Interest >= 10 and not self.InterestPiqued:
            self.InterestPiqued = True
            al.append(Advance("GilgameshAdvance", self.role, 1.00))
            self.Interest -= 10
        elif self.Interest >= 10 and self.InterestPiqued:
            al.append(Advance("GilgameshAdvance", self.role, 1.00))
            self.Interest -= 10
        if self.JointCounter >= 8 and self.SaberInTeam:
            bl, dbl, al, dl, tl, hl = self.extendLists(bl, dbl, al, dl, tl, hl, *self.useJointAttack(-1))
            self.JointCounter = 0
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        e5Dmg = 0.44 if self.eidolon >= 5 else 0.40
        if turn.moveName in UltimateList:
            bl.append(Buff("GilgameshUltDmg", StatTypes.DMG_PERCENT, e5Dmg, self.role, [AtkType.ULT], 3, 1, Role.SELF, TickDown.END))
        if turn.moveName not in bonusDMG:
            self.Interest += 1
        if self.Interest >= 10 and not self.InterestPiqued:
            self.InterestPiqued = True
            al.append(Advance("GilgameshAdvance", self.role, 1.00))
            self.Interest -= 10
        elif self.Interest >= 10 and self.InterestPiqued:
            al.append(Advance("GilgameshAdvance", self.role, 1.00))
            self.Interest -= 10
        if turn.charName == "Saber" and turn.moveName not in bonusDMG and turn.moveName != "SaberJointAttack":
            self.JointCounter += 1
        if self.JointCounter >= 8 and self.SaberInTeam:
            bl, dbl, al, dl, tl, hl = self.extendLists(bl, dbl, al, dl, tl, hl, *self.useJointAttack(-1))
            self.JointCounter = 0
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.SaberInTeam = specialRes.attr1
        if self.Tech:
            self.Tech = False
            tl.append(Turn(self.name, self.role, self.bestEnemy(-1), Targeting.AOE, [AtkType.SPECIAL],
                           [self.element], [2.00, 0], [0, 0], 0, self.scaling, 0, "GilgameshTechnique"))
            self.Interest += 3
        return bl, dbl, al, dl, tl, hl

    def takeTurn(self) -> str:
        return "E" if self.InterestPiqued else "A"