from Buff import *
from Character import Character
from Delay_Text import *
from Lightcones.Hunt.Swordplay import Swordplay
from Planars.DuranDynastyOfRunningWolves import DuranDynastyOfRunningWolves
from RelicStats import RelicStats
from Relics.TheAshblazingGrandDuke import DukeTopaz
from Result import Result, Special
from Turn_Text import Turn


class Topaz(Character):
    # Standard Character Settings
    name = "Topaz"
    path = Path.HUNT
    element = Element.FIRE
    scaling = Scaling.ATK
    baseHP = 931.4
    baseATK = 620.93
    baseDEF = 412.33
    baseSPD = 110
    maxEnergy = 130
    currEnergy = 65
    ultCost = 130
    currAV = 0
    aggro = 75
    dmgDct = {AtkType.BSC: 0, AtkType.FUA: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0}  # Adjust accordingly

    # Unique Character Properties
    hasSummon = True
    foundFire = False
    windfallCount = 0
    DebtTarget = 0
    lastDebtTarget = 0
    ChangeTarget = False
    firstNumby = True
    canUlt = False

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, eidolon: int = 0, lc=None, r1=None, r2=None,
                 pl=None, subs=None, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else Swordplay(role)
        self.relic1 = r1 if r1 else DukeTopaz(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else DuranDynastyOfRunningWolves(role)
        self.relicStats = subs if subs else RelicStats(8, 0, 2, 2, 2, 2, 3, 3, 3, 3, 13, 7, StatTypes.CR_PERCENT, StatTypes.SPD,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)  # 4 spd default
        self.rotation = rotation if rotation else ["E", "A", "A"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(
            Buff("TopazTraceDMG", StatTypes.DMG_PERCENT, 0.224, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("TopazTraceCR", StatTypes.CR_PERCENT, 0.12, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("TopazTraceHP", StatTypes.HP_PERCENT, 0.10, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(
            Buff("WindfallCD", StatTypes.CD_PERCENT, 0.275 if self.eidolon >= 5 else 0.25, self.role, [AtkType.TOPAZULT], 1,
                 1, Role.SELF, TickDown.PERM))
        if self.eidolon == 6:
            bl.append(Buff("TopazE6Pen", StatTypes.PEN, 0.10, self.role, atkType=[AtkType.TOPAZULT]))
        dbl.append(Debuff("ProofOfDebt", self.role, StatTypes.VULN, 0.55 if self.eidolon >= 3 else 0.5, self.DebtTarget,
                          [AtkType.FUA], 1000, 1, Targeting.SINGLE ,False, [0, 0], False))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.DebtTarget, Targeting.SINGLE, [AtkType.BSC, AtkType.FUA],
                       [self.element], [e3Mul, 0], [10, 0], 20, self.scaling, 1, "TopazBasic"))
        if self.eidolon >= 1:
            dbl.append(
                Debuff("DebtorCD", self.role, StatTypes.CD_PERCENT, 0.25, self.DebtTarget, [AtkType.FUA], 1000, 2,
                       Targeting.SINGLE ,False, [0, 0], False))
        al.append(Advance("AdvanceNumby", Role.NUMBY, 0.5))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        al.append(Advance("AdvanceNumby", Role.NUMBY, 0.5))
        e3Mul = 1.65 if self.eidolon >= 3 else 1.5
        windfallMul = 1.65 if self.eidolon >= 5 else 1.5
        if self.eidolon >= 1:
            dbl.append(
                Debuff("DebtorCD", self.role, StatTypes.CD_PERCENT, 0.25, self.DebtTarget, [AtkType.FUA], 1000, 2,
                       Targeting.SINGLE ,False, [0, 0], False))
        if self.windfallCount > 0:
            self.windfallCount = self.windfallCount - 1
            tl.append(Turn(self.name, self.role, self.DebtTarget, Targeting.SINGLE,
                           [AtkType.SKL, AtkType.FUA, AtkType.TOPAZULT], [self.element], [e3Mul + windfallMul, 0],
                           [20, 0], 40, self.scaling, -1, "TopazEnhancedSkill"))
        else:
            tl.append(Turn(self.name, self.role, self.DebtTarget, Targeting.SINGLE,
                           [AtkType.SKL, AtkType.FUA, AtkType.TOPAZFUA], [self.element], [e3Mul, 0], [20, 0], 30,
                           self.scaling, -1, "TopazSkill"))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        self.windfallCount = 3 if self.eidolon == 6 else 2
        tl.append(
            Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 5, self.scaling,
                 0, "TopazUlt"))
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if (turn.targeting != Targeting.NA) and (turn.moveName not in bonusDMG) and any(e.enemyID == self.DebtTarget for e in result.enemiesHit):
            if self.windfallCount > 0:
                al.append(Advance("AdvanceWindFallNumby", Role.NUMBY, 0.5))
            elif AtkType.FUA in turn.atkType:
                if self.eidolon >= 1:
                    dbl.append(
                        Debuff("DebtorCD", self.role, StatTypes.CD_PERCENT, 0.25, self.DebtTarget, [AtkType.FUA], 1000, 2,
                               Targeting.SINGLE ,False, [0, 0], False))
                al.append(Advance("AdvanceNumby", Role.NUMBY, 0.5))
        if self.DebtTarget != self.lastDebtTarget:
            dbl.append(Debuff("ProofOfDebt", self.role, StatTypes.VULN, 0.0, self.lastDebtTarget,
                              [AtkType.FUA], 1000, 1, Targeting.SINGLE, False, [0, 0], False))
            dbl.append(Debuff("ProofOfDebt", self.role, StatTypes.VULN, 0.55 if self.eidolon >= 3 else 0.5, self.DebtTarget,
                              [AtkType.FUA], 1000, 1, Targeting.SINGLE, False, [0, 0], False))
            self.lastDebtTarget = self.DebtTarget
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        if result.turnName == "NumbyGoGo":
            errGain = 60 if self.firstNumby else 0
            self.firstNumby = False
            self.fuas = self.fuas + 1
            if self.eidolon >= 1:
                dbl.append(
                    Debuff("DebtorCD", self.role, StatTypes.CD_PERCENT, 0.25, self.DebtTarget, [AtkType.FUA], 1000, 2,
                           Targeting.SINGLE ,False, [0, 0], False))
            numbyERR = 5 if self.eidolon >= 2 else 0
            if self.eidolon >= 4:
                al.append(Advance("TopazE4", self.role, 0.20))
            e5Mul = 1.65 if self.eidolon >= 5 else 1.5
            windfallMul = 1.65 if self.eidolon >= 5 else 1.5
            if self.windfallCount > 0:
                self.windfallCount = self.windfallCount - 1
                tl.append(
                    Turn(self.name, self.role, self.DebtTarget, Targeting.SINGLE, [AtkType.FUA, AtkType.TOPAZULT],
                         [self.element], [e5Mul + windfallMul, 0], [20, 0], errGain + numbyERR + 10, self.scaling, 0,
                         "TopazEnhancedFUA"))
            else:
                tl.append(
                    Turn(self.name, self.role, self.DebtTarget, Targeting.SINGLE, [AtkType.FUA, AtkType.TOPAZFUA],
                         [self.element], [e5Mul, 0], [20, 0], errGain + numbyERR, self.scaling, 0, "TopazFUA"))
        if self.DebtTarget != self.lastDebtTarget:
            dbl.append(Debuff("ProofOfDebt", self.role, StatTypes.VULN, 0.0, self.lastDebtTarget,
                              [AtkType.FUA], 1000, 1, Targeting.SINGLE, False, [0, 0], False))
            dbl.append(Debuff("ProofOfDebt", self.role, StatTypes.VULN, 0.55 if self.eidolon >= 3 else 0.5, self.DebtTarget,
                              [AtkType.FUA], 1000, 1, Targeting.SINGLE, False, [0, 0], False))
            self.lastDebtTarget = self.DebtTarget
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        if specialRes.attr1 and not self.foundFire:
            self.foundFire = True
            bl.append(
                Buff("TopazFireDMG", StatTypes.DMG_PERCENT, 0.15, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        self.canUlt = specialRes.attr2
        self.DebtTarget = specialRes.attr3
        return bl, dbl, al, dl, tl, hl

    def canUseUlt(self) -> bool:
        return super().canUseUlt() if self.canUlt else False