import logging

from Buff import *
from Character import Character
from Lightcones.Destruction.IAmAsYouBehold import IAmAsYouBehold
from Planars.CosmicLifeSciencesInstitute import CosmicLifeSciencesInstitute
from Planars.TengokuLivestream import TengokuLivestream
from RelicStats import RelicStats
from Relics.ScholarLostInErudition import ScholarLostInErudition
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
    InterestOld = 0
    InterestTally = 0
    InterestPiqued = False
    GoldenRule = 0
    JointCounter = 0
    SaberInTeam = False
    Tech = True
    ally1Energy = 0
    ally1Role = 0
    ally2Energy = 0
    ally2Role = 0
    ally3Energy = 0
    ally3Role = 0

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope
    # With Sparkle:
    # self.relicStats = subs if subs else RelicStats(2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 14, 9, StatTypes.CR_PERCENT, StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT)

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else IAmAsYouBehold(role, 1)
        self.relic1 = r1 if r1 else ScholarLostInErudition(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else CosmicLifeSciencesInstitute(role)
        self.relicStats = subs if subs else RelicStats(2, 2, 2, 2, 2, 3, 2, 2, 2, 2, 12, 11, StatTypes.CR_PERCENT, StatTypes.ATK_PERCENT,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["E"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("GilgameshTraceATK", StatTypes.ATK, 0.18, self.role))
        bl.append(Buff("GilgameshTraceCR", StatTypes.CR_PERCENT, 0.187, self.role))
        bl.append(Buff("GilgameshTraceDMG", StatTypes.DMG_PERCENT, 0.08, self.role))
        bl.append(Buff("GilgameshTrace3ATK", StatTypes.ATK_PERCENT, 0.20, Role.ALL))
        bl.append(Buff("GilgameshTrace3CD", StatTypes.CD_PERCENT, 0.20, Role.ALL))
        bl.append(Buff("GilgameshTrace3SelfATK", StatTypes.ATK_PERCENT, 1.00, self.role))
        bl.append(Buff("GilgameshTrace3SelfCD", StatTypes.CD_PERCENT, 1.00, self.role))
        if self.eidolon >= 4:
            bl.append(Buff("GilgameshE4ERR", StatTypes.ERR_PERCENT, 0.20, self.role))
        if self.eidolon >= 6:
            bl.append(Buff("GilgameshE6PEN", StatTypes.PEN, 0.20, Role.ALL))
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
        e1Role = Role.ALL if self.eidolon >= 1 else self.role
        e2MainExtraDamage = 2.0 if self.eidolon >= 2 else 1.0
        e2SideExtraDamage = 1.5 if self.eidolon >= 2 else 1.0
        bl.append(Buff("GilgameshSKLShred", StatTypes.SHRED, e3Shred, e1Role, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
        if self.eidolon >= 1:
            bl.append(Buff("GilgameshE1ATK", StatTypes.ATK_PERCENT, 0.60, self.role, [AtkType.ALL], 3, 1, Role.SELF,TickDown.END))
            bl.append(Buff("GilgameshE1ERR", StatTypes.ERR_F, 40, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.END))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.BLAST, [AtkType.SKL], [self.element],
                       [e3MulMain*e2MainExtraDamage, e3MulSide*e2SideExtraDamage], [20, 10], 30, self.scaling, 0, "GilgameshSkill"))
        self.Interest = 0
        self.JointCounter += 1
        logger.debug(f"Gilgamesh JointCounter increased by one, current count: {self.JointCounter}")
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e5MulAll = 4.40 if self.eidolon >= 5 else 4.00
        e5MulExtra = 1.10 if self.eidolon >= 5 else 1.0
        e6ExtraDamage = 0.80 if self.eidolon == 6 else 0.00
        if self.eidolon == 6:
            bl.append(Buff("GilgameshE6UltCD", StatTypes.CD_PERCENT, 1.00*self.GoldenRule, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
            self.GoldenRule = 0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT], [self.element],
                       [e5MulAll, 0], [40, 0], 0, self.scaling, 0, "GilgameshUltAll"))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ULT], [self.element],
                       [(e5MulExtra + e6ExtraDamage)*10, 0], [2*10, 0], 5, self.scaling, 0, "GilgameshUltSingle"))
        self.Interest += 2
        logger.debug(f"Gilgamesh Obtained 2 Interest from Ult, Current count: {self.Interest}")
        if self.eidolon >= 2:
            self.Interest += 5
            logger.debug(f"Gilgamesh Obtained 3 Interest from E2, Current count: {self.Interest}")
        self.GoldenRule += 1
        self.JointCounter += 1
        logger.debug(f"Gilgamesh JointCounter increased by one, current count: {self.JointCounter}")
        return bl, dbl, al, dl, tl, hl

    def useJointAttack(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useJointAttack(enemyID)
        e3Mult = 4.4 if self.eidolon>= 3 else 4.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.FUA],
                       [self.element], [e3Mult, 0], [20, 0], 10, self.scaling, 0, "GilgameshJointAttack"))
        self.Interest += 3
        logger.debug(f"Gilgamesh Obtained 3 Interest from Joint Attack, Current count: {self.Interest}")
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        if self.Interest >= 10 and not self.InterestPiqued:
            self.InterestPiqued = True
        bl.append(Buff("GilgameshInterestSPD", StatTypes.SPD_PERCENT, 0.1*self.Interest, self.role, [AtkType.ALL], 1, 1, self.ally2Role, TickDown.PERM))
        if self.JointCounter >= 8 and self.SaberInTeam:
            bl, dbl, al, dl, tl, hl = self.extendLists(bl, dbl, al, dl, tl, hl, *self.useJointAttack(-1))
            self.JointCounter = 0
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        e5Dmg = 0.44 if self.eidolon >= 5 else 0.40
        if turn.moveName in UltimateList:
            bl.append(Buff("GilgameshUltDmg", StatTypes.DMG_PERCENT, e5Dmg, self.role, [AtkType.ULT], 3, 1, Role.SELF, TickDown.END))
            self.Interest += 2
            logger.debug(f"Gilgamesh Obtained 2 Interest from Teammate Ult, Current count: {self.Interest}")
            self.GoldenRule = min(self.GoldenRule + 1, 3)
            if turn.charRole == self.ally1Role:
                bl.append(Buff("GilgameshTrace1ERRAlly1", StatTypes.ERR_F, 0.3*self.ally1Energy, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.END))
                logger.debug(f"Gilgamesh Obtained {0.3*self.ally1Energy} Energy from Teammate")
            if turn.charRole == self.ally2Role:
                bl.append(Buff("GilgameshTrace1ERRAlly2", StatTypes.ERR_F, 0.3*self.ally2Energy, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.END))
                logger.debug(f"Gilgamesh Obtained {0.3*self.ally2Energy} Energy from Teammate")
            if turn.charRole == self.ally3Role:
                bl.append(Buff("GilgameshTrace1ERRAlly3", StatTypes.ERR_F, 0.3*self.ally3Energy, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.END))
                logger.debug(f"Gilgamesh Obtained {0.3*self.ally3Energy} Energy from Teammate")
        if turn.charRole == self.ally1Role and self.ally1Energy > 140:
            bl.append(Buff("GilgameshTrace3AllyATK", StatTypes.ATK_PERCENT, min((self.ally1Energy - 140) * 0.01, 1.00), self.ally1Role, [AtkType.ALL], 1, 1, self.ally1Role, TickDown.PERM))
            bl.append(Buff("GilgameshTrace3AllyCD", StatTypes.CD_PERCENT, min((self.ally1Energy - 140) * 0.01, 1.00), self.ally1Role, [AtkType.ALL], 1, 1, self.ally1Role, TickDown.PERM))
        if turn.charRole == self.ally2Role and self.ally3Energy > 140:
            bl.append(Buff("GilgameshTrace3AllyATK", StatTypes.ATK_PERCENT, min((self.ally2Energy - 140) * 0.01, 1.00), self.ally2Role, [AtkType.ALL], 1, 1, self.ally2Role, TickDown.PERM))
            bl.append(Buff("GilgameshTrace3AllyCD", StatTypes.CD_PERCENT, min((self.ally2Energy - 140) * 0.01, 1.00), self.ally2Role, [AtkType.ALL], 1, 1, self.ally2Role, TickDown.PERM))
        if turn.charRole == self.ally3Role and self.ally3Energy > 140:
            bl.append(Buff("GilgameshTrace3AllyATK", StatTypes.ATK_PERCENT, min((self.ally3Energy - 140) * 0.01, 1.00), self.ally3Role, [AtkType.ALL], 1, 1, self.ally3Role, TickDown.PERM))
            bl.append(Buff("GilgameshTrace3AllyCD", StatTypes.CD_PERCENT, min((self.ally3Energy - 140) * 0.01, 1.00), self.ally3Role, [AtkType.ALL], 1, 1, self.ally3Role, TickDown.PERM))
        if turn.moveName not in bonusDMG:
            self.Interest += 1
            logger.debug(f"Gilgamesh Obtained 1 Interest from Teammate, Current count: {self.Interest}")
        if self.Interest >= 10 and not self.InterestPiqued:
            self.InterestPiqued = True
        bl.append(Buff("GilgameshInterestSPD", StatTypes.SPD_PERCENT, 0.1*self.Interest, self.role, [AtkType.ALL], 1, 1, self.ally2Role, TickDown.PERM))
        if turn.charName == "Saber" and turn.moveName not in bonusDMG and turn.moveName != "SaberJointAttack":
            self.JointCounter += 1
            logger.debug(f"Gilgamesh JointCounter increased by one, current count: {self.JointCounter}")
        if self.JointCounter >= 8 and self.SaberInTeam:
            bl, dbl, al, dl, tl, hl = self.extendLists(bl, dbl, al, dl, tl, hl, *self.useJointAttack(-1))
            self.JointCounter = 0
        if self.eidolon == 6 and result.turnName == "GilgameshUltSingle":
            bl.append(Buff("GilgameshE6UltCD", StatTypes.CD_PERCENT, 0, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.SaberInTeam = specialRes.attr1
        self.ally1Energy = specialRes.attr2[0]
        self.ally1Role = specialRes.attr2[1]
        self.ally2Energy = specialRes.attr3[0]
        self.ally2Role = specialRes.attr3[1]
        self.ally3Energy = specialRes.attr4[0]
        self.ally3Role = specialRes.attr4[1]
        if self.Tech:
            self.Tech = False
            tl.append(Turn(self.name, self.role, self.bestEnemy(-1), Targeting.AOE, [AtkType.SPECIAL],
                           [self.element], [2.00, 0], [0, 0], 0, self.scaling, 0, "GilgameshTechnique"))
            self.Interest += 3
            logger.debug(f"Gilgamesh Obtained 3 Interest from Technique, Current count: {self.Interest}")
            if self.eidolon >= 2:
                self.Interest += 5
                logger.debug(f"Gilgamesh Obtained 5 Interest from E2, Current count: {self.Interest}")
        Interest_diff = self.Interest - self.InterestOld
        if Interest_diff > 0:
            self.InterestTally = min(self.InterestTally + Interest_diff, 6)
        self.InterestOld = self.Interest
        bl.append(Buff("Trace2CDExtra", StatTypes.CD_PERCENT, 0.25 * self.InterestTally, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("GilgameshInterestSPD", StatTypes.SPD_PERCENT, 0.1*self.Interest, self.role, [AtkType.ALL], 1, 1, self.ally2Role, TickDown.PERM))
        return bl, dbl, al, dl, tl, hl

    def takeTurn(self) -> str:
        return "E" if self.InterestPiqued else "A"