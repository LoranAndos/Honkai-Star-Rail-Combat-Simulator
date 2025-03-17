from Character import Character
from Lightcones.CruisingInTheStellarSea import CruisingInTheStellarSea
from Relics.ScholarLostInErudition import ScholarLostInErudition
from Planars.RutilantArena import RutilantArena
from RelicStats import RelicStats
from Buff import Buff
from Result import Result
from Turn_Text import Turn
from Attributes import *
from Healing import *


class Tingyun(Character):
    # Standard Character Settings
    name = "Tingyun"
    path = Path.HARMONY
    element = Element.LIGHTNING
    scaling = Scaling.ATK
    baseHP = 846.70
    baseATK = 529.20
    baseDEF = 396.90
    baseSPD = 112
    maxEnergy = 130
    ultCost = 130
    currEnergy = 130
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SPECIAL: 0, AtkType.BRK: 0}

    # Unique Character Properties

    # Relic Settings

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=6, beneTarget=None, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else CruisingInTheStellarSea(role, 5)
        self.relic1 = r1 if r1 else ScholarLostInErudition(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else RutilantArena(role)
        self.relicStats = subs if subs else RelicStats(14, 2, 0, 2, 4, 10, 4, 4, 4, 4, 0, 0, StatTypes.ATK_PERCENT, StatTypes.Spd,
                                                       StatTypes.ATK_PERCENT, StatTypes.ERR_PERCENT)
        self.beneTarget = beneTarget if beneTarget else Role.DPS
        self.rotation = rotation if rotation else ["E","A","A"]

    def equip(self):
        buffList, debuffList, advList, delayList, healList = super().equip()
        buffList.append(
            Buff("TingyunBasicDMG", StatTypes.DMG_PERCENT, 0.4, self.role, [AtkType.BSC], 1, 1, Role.SELF, TickDown.PERM))
        buffList.append(
            Buff("TingyunTraceATK", StatTypes.ATK_PERCENT, 0.28, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        buffList.append(
            Buff("TingyunTraceDEF", StatTypes.DEF_PERCENT, 0.225, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        buffList.append(
            Buff("TingyunTraceDMG", StatTypes.DMG_PERCENT, 0.08, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return buffList, debuffList, advList, delayList, healList

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        e5Mul = 0.66 if self.eidolon >= 5 else 0.6
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 25, self.scaling, 1, "TingyunBasic"))
        tl.append(Turn(self.name, self.beneTarget, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.SPECIAL],
                       [self.element], [e5Mul, 0], [0, 0], 0, Scaling.ATK, 0, "TYAllyBonus"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.SKL], [self.element], [0, 0], [0, 0], 35,
                       self.scaling, -1, "TingyunSkill"))
        bl.append(Buff("Benediction", StatTypes.ATK_PERCENT, 0.55, self.beneTarget, [AtkType.ALL], 3, 1, self.beneTarget,
                       TickDown.END))
        bl.append(
            Buff("TingyunSkillSPD", StatTypes.SPD_PERCENT, 0.2, self.role, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        self.currEnergy = self.currEnergy - self.ultCost
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        errGain = 60 if self.eidolon == 6 else 50
        e3Dmg = 0.56 if self.eidolon >= 3 else 0.50
        tl.append(
            Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ULT], [self.element], [0, 0], [0, 0], 5, self.scaling,
                 0, "TingyunUlt"))
        bl.append(Buff("TingyunUltEnergy", StatTypes.ERR_F, errGain, self.beneTarget, [AtkType.ALL], 1, 1, self.beneTarget,
                       TickDown.PERM))
        bl.append(Buff("TingyunUltDMG", StatTypes.DMG_PERCENT, e3Dmg, self.beneTarget, [AtkType.ALL], 2, 1, self.beneTarget,
                       TickDown.END))
        if self.eidolon >= 1:
            bl.append(Buff("TingyunE1UltSPD", StatTypes.SPD_PERCENT, 0.2, self.beneTarget, turns=1, tickDown=self.beneTarget,
                           tdType=TickDown.END))
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        e4BeneBonus = 0.2 if self.eidolon >= 4 else 0
        e5BeneBonus = 0.44 if self.eidolon >= 5 else 0.4
        if (turn.charRole == self.beneTarget) and (turn.moveName not in bonusDMG) and result.enemiesHit:
            tl.append(
                Turn(self.name, self.beneTarget, result.enemiesHit[0].enemyID, Targeting.SPECIAL, [AtkType.SPECIAL],
                     [self.element], [e5BeneBonus + e4BeneBonus, 0], [0, 0], 0, Scaling.ATK, 0, "TYBeneBonus"))
        return bl, dbl, al, dl, tl, hl