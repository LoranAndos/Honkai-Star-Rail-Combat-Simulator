import logging

from Buff import *
from Character import Character
from Delay_Text import *
from Lightcones import Mirror
from Lightcones.MemoriesOfThePast import MOTP
from Planars.Lushaka import Lushaka
from Planars.Vonwacq import Vonwacq
from RelicStats import RelicStats
from Relics.Messenger import Messenger
from Relics.Thief import Thief
from Result import *
from Result import Special
from Turn_Text import Turn

logger = logging.getLogger(__name__)


# noinspection DuplicatedCode
class RuanMei(Character):
    # Standard Character Settings
    name = "RuanMei"
    path = Path.HARMONY
    element = Element.ICE
    scaling = Scaling.ATK
    baseHP = 1086.6
    baseATK = 659.74
    baseDEF = 485.10
    baseSPD = 104
    maxEnergy = 130
    currEnergy = 65
    ultCost = 130
    currAV = 0
    dmgDct = {AtkType.BSC: 0, AtkType.BRK: 0, AtkType.SBK: 0}  # Adjust accordingly

    # Unique Character Properties
    beStat = 0

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, targetPrio=Priority.DEFAULT, rotation=None) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else MOTP(role)
        self.relic1 = r1 if r1 else Thief(role, 2)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else Messenger(role, 2))
        self.planar = pl if pl else Vonwacq(role)
        self.relicStats = subs if subs else RelicStats(10, 4, 0, 4, 4, 0, 4, 14, 4, 4, 0, 0, StatTypes.HP_PERCENT, StatTypes.Spd,
                                                       StatTypes.DEF_PERCENT, StatTypes.ERR_PERCENT)
        self.rotation = rotation if rotation else ["A", "A", "E"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        teamSPD = 0.104 if self.eidolon >= 3 else 0.10
        bl.append(Buff("RuanSPD", StatTypes.SPD_PERCENT, teamSPD, Role.ALL))
        bl.append(Buff("RuanNerfSPD", StatTypes.SPD_PERCENT, -teamSPD, self.role))
        bl.append(Buff("RuanTech", StatTypes.ERR_T, 30, self.role))
        bl.append(Buff("RuanDMG", StatTypes.DMG_PERCENT, 0.68, Role.ALL, [AtkType.ALL], 3, 1, self.role, TickDown.START))
        bl.append(Buff("RuanWBE", StatTypes.WB_EFF, 0.50, Role.ALL, [AtkType.ALL], 3, 1, self.role, TickDown.START))
        bl.append(Buff("RuanTraceBE", StatTypes.BE_PERCENT, 0.20, self.role))
        bl.append(Buff("RuanTraceDEF", StatTypes.DEF_PERCENT, 0.225, self.role))
        bl.append(Buff("RuanTraceSPD", StatTypes.Spd, 5, self.role))
        bl.append(Buff("RuanTeamBE", StatTypes.BE_PERCENT, 0.20, Role.ALL))
        if self.eidolon >= 2:
            bl.append(Buff("RuanE2ATK", StatTypes.ATK_PERCENT, 0.4, Role.ALL, [AtkType.ALL], reqBroken= True))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e5Bonus = 1.1 if self.eidolon >= 5 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],[e5Bonus, 0], [10, 0], 25, self.scaling, 1, "RuanBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e5Bonus = 0.352 if self.eidolon >= 5 else 0.32
        tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.SKL], [self.element], [0, 0], [0, 0], 35,
                       self.scaling, -1, "RuanSkill"))
        bl.append(
            Buff("RuanDMG", StatTypes.DMG_PERCENT, e5Bonus + 0.36, Role.ALL, [AtkType.ALL], 3, 1, self.role, TickDown.START))
        bl.append(Buff("RuanWBE", StatTypes.WB_EFF, 0.50, Role.ALL, [AtkType.ALL], 3, 1, self.role, TickDown.START))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        ultTurns = 3 if self.eidolon == 6 else 2
        pen = 0.27 if self.eidolon >= 3 else 0.25
        bl.append(Buff("RuanUltPEN", StatTypes.PEN, pen, Role.ALL, [AtkType.ALL], ultTurns, 1, self.role, TickDown.START))
        breakMul = 0.54 if self.eidolon >= 3 else 0.50
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOEBREAK, [AtkType.BRK], [self.element],[breakMul, 0], [0, 0], 5, self.scaling, 0, "RuanUltBreak"))
        if self.eidolon >= 1:
            bl.append(
                Buff("RuanE1Shred", StatTypes.SHRED, 0.20, Role.ALL, [AtkType.ALL], ultTurns, 1, self.role, TickDown.START))
        dl.append(Delay("RuanThanatoplum", 0.1 + self.beStat * 0.2, Role.ALL, True, False))
        return bl, dbl, al, dl, tl, hl

    # noinspection DuplicatedCode
    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        if result.brokenEnemy and self.eidolon >= 4:
            bl.append(Buff("RuanE4BE", StatTypes.BE_PERCENT, 1.0, self.role, turns=4, tdType=TickDown.END))
        for enemy in result.brokenEnemy:
            breakMul = 1.32 if self.eidolon >= 3 else 1.2
            e6 = 2.0 if self.eidolon == 6 else 0
            tl.append(Turn(self.name, self.role, enemy.enemyID, Targeting.STBREAK, [AtkType.BRK], [self.element], [breakMul + e6, 0], [0, 0], 0, self.scaling, 0, "RuanAllyBreak"))
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if result.brokenEnemy and self.eidolon >= 4:
            bl.append(Buff("RuanE4BE", StatTypes.BE_PERCENT, 1.0, self.role, turns=3, tdType=TickDown.END))
        for enemy in result.brokenEnemy:
            breakMul = 1.32 if self.eidolon >= 3 else 1.2
            e6 = 2.0 if self.eidolon == 6 else 0
            tl.append(Turn(self.name, self.role, enemy.enemyID, Targeting.STBREAK, [AtkType.BRK], [self.element], [breakMul + e6, 0], [0, 0], 0, self.scaling, 0, "RuanAllyBreak"))
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.beStat = specialRes.attr1
        return bl, dbl, al, dl, tl, hl