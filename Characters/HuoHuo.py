from Buff import *
from Healing import *
from Character import Character
from Lightcones.PostOpConversation import PostOp
from Planars.Keel import Keel
from RelicStats import RelicStats
from Relics.Longevous import Longevous
from Relics.Messenger import Messenger
from Result import *
from Result import Result
from Turn_Text import Turn


class HuoHuo(Character):
    # Standard Character Settings
    name = "HuoHuo"
    path = Path.ABUNDANCE
    element = Element.WIND
    scaling = Scaling.HP
    baseHP = 1358.3
    baseATK = 601.52
    baseDEF = 509.36
    baseSPD = 98
    maxEnergy = 140
    currEnergy = 70
    ultCost = 140
    currAV = 0
    dmgDct = {AtkType.BSC: 0, AtkType.BRK: 0}  # Adjust accordingly

    # Unique Character Properties
    foundEnergy = False
    ally1Energy = 0
    ally2Energy = 0
    ally3Energy = 0
    ally1Role = 0
    ally2Role = 0
    ally3Role = 0
    divineTrigger = 0

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else PostOp(self.role, 5)
        self.relic1 = r1 if r1 else Messenger(self.role, 2, True)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else Longevous(self.role, 2))
        self.planar = pl if pl else Keel(self.role)
        self.relicStats = subs if subs else RelicStats(12, 0, 4, 4, 8, 4, 4, 4, 4, 4, 0, 0, StatTypes.OGH_PERCENT, StatTypes.Spd,
                                                       StatTypes.HP_PERCENT, StatTypes.ERR_PERCENT)
        self.rotation = rotation if rotation else (["E", "A", "A"] if eidolon >= 1 else ["E", "A"])

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("HHTraceHP", StatTypes.HP_PERCENT, 0.28, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("HHTraceERS", StatTypes.ERS_PERCENT, 0.18, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("HHTraceSPD", StatTypes.Spd, 5, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        if self.eidolon == 6:
            bl.append(Buff("HHE6DMG", StatTypes.DMG_PERCENT, 0.5, Role.ALL))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        e5Mul = 0.55 if self.eidolon >= 5 else 0.5
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e5Mul, 0], [10, 0], 20, self.scaling, 1, "HuoHuoBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        self.divineTrigger = 6
        tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.SKL], [self.element], [0, 0], [0, 0], 30,
                       self.scaling, -1, "HuoHuoSkill"))
        if self.eidolon >= 1:
            bl.append(Buff("HHDivineSPD", StatTypes.SPD_PERCENT, 0.16, Role.ALL, turns=3, tickDown=self.role,
                           tdType=TickDown.START))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        atkBuff = 0.432 if self.eidolon >= 3 else 0.4
        errMul = 0.21 if self.eidolon >= 3 else 0.2
        bl.append(
            Buff("HuoHuoUltATK", StatTypes.ATK_PERCENT, atkBuff, Role.ALL, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        bl.append(
            Buff("HuoHuoERR", StatTypes.ERR_F, self.ally1Energy * errMul, self.ally1Role, [AtkType.ALL], 1, 1, self.ally1Role,
                 TickDown.PERM))
        bl.append(
            Buff("HuoHuoERR", StatTypes.ERR_F, self.ally2Energy * errMul, self.ally2Role, [AtkType.ALL], 1, 1, self.ally2Role,
                 TickDown.PERM))
        bl.append(
            Buff("HuoHuoERR", StatTypes.ERR_F, self.ally3Energy * errMul, self.ally3Role, [AtkType.ALL], 1, 1, self.ally3Role,
                 TickDown.PERM))
        tl.append(
            Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ULT], [self.element], [0, 0], [0, 0], 5, self.scaling,
                 0, "HuoHuoULT"))
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        if not self.foundEnergy:
            self.foundEnergy = True
            self.ally1Energy = specialRes.attr1[0]
            self.ally1Role = specialRes.attr1[1]
            self.ally2Energy = specialRes.attr2[0]
            self.ally2Role = specialRes.attr2[1]
            self.ally3Energy = specialRes.attr3[0]
            self.ally3Role = specialRes.attr3[1]
        return super().handleSpecialStart(specialRes)

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if (
                "Skill" in turn.moveName or "Basic" in turn.moveName or "Ult" in turn.moveName) and turn.moveName not in bonusDMG and self.divineTrigger > 0:
            self.divineTrigger = max(0, self.divineTrigger - 1)
            tl.append(
                Turn(self.name, self.role, self.defaultTarget, Targeting.NA, [AtkType.SPECIAL], [self.element], [0, 0],
                     [0, 0], 2, self.scaling, 0, "HuoHuoAllyERR"))
        return bl, dbl, al, dl, tl, hl