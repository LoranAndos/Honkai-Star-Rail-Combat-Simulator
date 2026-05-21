from Buff import Buff
from Character import Character
from Delay_Text import *
from Lightcones.Harmony.ButTheBattleIsntOver import ButTheBattleIsntOver
from Attributes import *
from Planars.LushakaTheSunkenSeas import LushakaTheSunkenSeas
from RelicStats import RelicStats
from Relics.MusketeerOfWildWheat import MusketeerOfWildWheat
from Relics.PrisonerInDeepConfinement import PrisonerInDeepConfinement
from Result import Result, Special
from Turn_Text import Turn


class Robin(Character):
    # Standard Character Settings
    name = "Robin"
    path = Path.HARMONY
    element = Element.PHYSICAL
    scaling = Scaling.ATK
    baseHP = 1280.7
    baseATK = 640.33
    baseDEF = 485.10
    baseSPD = 102
    maxEnergy = 160
    ultCost = 160
    currEnergy = 80
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SPECIAL: 0, AtkType.BRK: 0}

    # Unique Character Properties
    canBeAdv = True
    sameEleTeammates = []
    moonlessMidnight = 0
    atkStat = 0
    canUlt = False
    techErr = True

    # Relic Settings

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, eidolon=0, lc=None, r1=None, r2=None, pl=None,
                 subs=None, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else ButTheBattleIsntOver(role)
        self.relic1 = r1 if r1 else MusketeerOfWildWheat(role, 2)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else PrisonerInDeepConfinement(role, 2))
        self.planar = pl if pl else LushakaTheSunkenSeas(role, Role.DPS)
        self.relicStats = subs if subs else RelicStats(10, 4, 4, 4, 4, 10, 3, 3, 3, 3, 0, 0, StatTypes.ATK_PERCENT,
                                                       StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT, StatTypes.ERR_PERCENT)
        self.rotation = rotation if rotation else ["E", "A", "A"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(
            Buff("RobinCD", StatTypes.CD_PERCENT, 0.23 if self.eidolon >= 5 else 0.2, Role.ALL, [AtkType.ALL], 1, 1,
                 Role.SELF, TickDown.PERM))
        bl.append(
            Buff("RobinTraceATK", StatTypes.ATK_PERCENT, 0.28, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(
            Buff("RobinTraceHP", StatTypes.HP_PERCENT, 0.18, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("RobinTraceSPD", StatTypes.SPD, 5, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        al.append(Advance("RobinStartADV", self.role, 0.25))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e2ERR = 3 if self.eidolon >= 2 else 2
        e5Mul = 1.1 if self.eidolon >= 5 else 1
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e5Mul, 0], [10, 0], 20 + e2ERR, self.scaling, 1, "RobinBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e3Dmg = 0.55 if self.eidolon >= 3 else 0.5
        tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.SKL], [self.element], [0, 0], [0, 0], 35,
                       self.scaling, -1, "RobinSkill"))
        bl.append(Buff("RobinSklDMG", StatTypes.DMG_PERCENT, e3Dmg, Role.ALL, [AtkType.ALL], 3, 1, self.role, TickDown.START))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        self.currEnergy = self.currEnergy - self.ultCost
        self.canBeAdv = False
        self.currAV = 10000 / 90
        self.moonlessMidnight = 8
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        bl.append(Buff("RobinFuaCD", StatTypes.CD_PERCENT, 0.25, Role.ALL, [AtkType.FUA], 1, 1, self.role, TickDown.START))
        if self.eidolon >= 1:
            bl.append(Buff("RobinE1Pen", StatTypes.PEN, 0.24, Role.ALL, [AtkType.ALL], 1, 1, self.role, TickDown.START))
        if self.eidolon >= 2:
            bl.append(
                Buff("RobinE2SPD", StatTypes.SPD_PERCENT, 0.16, Role.ALL, [AtkType.FUA], 1, 1, self.role, TickDown.START))
        tl.append(
            Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ULT], [self.element], [0, 0], [0, 0], 5, self.scaling,
                 0, "RobinUlt"))
        al.append(Advance("RobinUltADV", Role.ALL, 1.0))
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        e2ERR = 3 if self.eidolon >= 2 else 2
        e3Mul = 1.296 if self.eidolon >= 3 else 1.2
        if (turn.moveName not in bonusDMG) and (turn.targeting != Targeting.NA):
            if self.canBeAdv:  # not in concerto state, only provide extra ERR
                tl.append(
                    Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], e2ERR,
                         self.scaling, 0, "RobinBonusERR"))
            else:  # in concerto state, provide both additional dmg and extra ERR
                if self.eidolon == 6 and self.moonlessMidnight > 0:
                    self.moonlessMidnight = self.moonlessMidnight - 1
                    tl.append(
                        Turn(self.name, self.role, result.enemiesHit[0].enemyID, Targeting.SPECIAL, [AtkType.SPECIAL],
                             [self.element], [e3Mul, 0], [0, 0], e2ERR, self.scaling, 0, "RobinMoonlessMidnight"))
                else:
                    tl.append(
                        Turn(self.name, self.role, result.enemiesHit[0].enemyID, Targeting.SPECIAL, [AtkType.SPECIAL],
                             [self.element], [e3Mul, 0], [0, 0], e2ERR, self.scaling, 0, "RobinConcertoDMG"))
        return bl, dbl, al, dl, tl, hl

    def reduceAV(self, reduceValue: float):
        if self.canBeAdv:
            self.currAV = max(0.0, self.currAV - reduceValue)

    def takeTurn(self) -> str:
        self.canBeAdv = True
        return super().takeTurn()

    def handleSpecialStart(self, specialRes: Special):
        self.atkStat = specialRes.attr1
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        e3Mul = 0.24332 if self.eidolon >= 3 else 0.228
        e3Flat = 230 if self.eidolon >= 3 else 200
        if self.techErr:
            self.techErr = False
            tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.BSC], [self.element], [0, 0], [0, 0], 5,
                           self.scaling, 0, "RobinTechEnergy"))
        if not self.canBeAdv:
            bl.append(
                Buff("RobinUltBuff", StatTypes.ATK, self.atkStat * e3Mul + e3Flat, Role.ALL, [AtkType.ALL], 1, 1, self.role,
                     TickDown.START))
            if self.eidolon >= 4:
                bl.append(Buff("RobinE4ERS", StatTypes.ERS_PERCENT, 0.5, Role.ALL, turns=1, tickDown=self.role,
                               tdType=TickDown.START))
        return bl, dbl, al, dl, tl, hl

    def handleSpecialEnd(self, specialRes: Special):
        self.canUlt = specialRes.attr1
        return super().handleSpecialEnd(specialRes)

    def canUseUlt(self) -> bool:
        if self.currEnergy >= self.ultCost and self.canUlt:
            return True
        return False