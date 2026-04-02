from Buff import *
from Character import Character
from Lightcones.Abundance.PostOpConversation import PostOpConversation
from Planars.BrokenKeel import BrokenKeel
from RelicStats import RelicStats
from Relics.WarriorGoddessOfSunAndThunder import WarriorGoddessOfSunAndThunder
from Result import *
from Result import Result
from Turn_Text import Turn
from Healing import Healing


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
    ally1MaxHP = 0
    ally1HPRole = 0
    ally1CurrentHP = 0
    ally2MaxHP = 0
    ally2HPRole = 0
    ally2CurrentHP = 0
    ally3MaxHP = 0
    ally3HPRole = 0
    ally3CurrentHP = 0
    ally4MaxHP = 0
    ally4HPRole = 0
    ally4CurrentHP = 0
    divineTrigger = 0


    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else PostOpConversation(self.role, 5)
        self.relic1 = r1 if r1 else WarriorGoddessOfSunAndThunder(self.role, 4, True)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else BrokenKeel(self.role)
        self.relicStats = subs if subs else RelicStats(12, 0, 4, 4, 8, 4, 4, 4, 4, 4, 0, 0, StatTypes.OGH_PERCENT, StatTypes.SPD,
                                                       StatTypes.HP_PERCENT, StatTypes.ERR_PERCENT)
        self.rotation = rotation if rotation else (["E", "A", "A", "A"] if eidolon >= 1 else ["E", "A", "A"])

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("HHTraceHP", StatTypes.HP_PERCENT, 0.28, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("HHTraceERS", StatTypes.ERS_PERCENT, 0.18, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("HHTraceSPD", StatTypes.SPD, 5, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("HHTraceERR", StatTypes.ERR_T, 30, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        self.divineTrigger = 6
        if self.eidolon >= 1:
            bl.append(Buff("HHDivineSPD", StatTypes.SPD_PERCENT, 0.12, Role.ALL, turns=2, tickDown=self.role,
                           tdType=TickDown.START))
            bl.append(Buff("HHDivineOGH", StatTypes.OGH_PERCENT, 0.20, Role.ALL, turns=2, tickDown=self.role,
                           tdType=TickDown.START))
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
        E5BigHealScale = 0.256 if self.eidolon >= 5 else 0.24
        E5BigHealFlat = 712 if self.eidolon >= 5 else 640
        E5SmallHealScale = 0.2048 if self.eidolon >= 5 else 0.192
        E5SmallHealFlat = 569.6 if self.eidolon >= 5 else 512
        tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.SKL], [self.element], [0, 0], [0, 0], 30,
                       self.scaling, -1, "HuoHuoSkill"))
        if self.eidolon >= 1:
            bl.append(Buff("HHDivineSPD", StatTypes.SPD_PERCENT, 0.12, Role.ALL, turns=3, tickDown=self.role,
                           tdType=TickDown.START))
            bl.append(Buff("HHDivineOGH", StatTypes.OGH_PERCENT, 0.20, Role.ALL, turns=3, tickDown=self.role,
                           tdType=TickDown.START))
        hl.append(Healing("HuoHuoSkillHealingScaling",[E5BigHealScale,E5SmallHealScale],self.scaling,Role.ALL,self.role,Targeting.BLAST))
        hl.append(Healing("HuoHuoSkillHealingFlat",[E5BigHealFlat,E5SmallHealFlat],Scaling.Other,Role.ALL,self.role,Targeting.BLAST))
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
        if self.ally1Energy > 160:
            bl.append(
                Buff("HuoHuoUltExtraATK", StatTypes.ATK_PERCENT, 0.24, self.ally1Role, [AtkType.ALL], 1, 1,
                     self.ally1Role,
                     TickDown.PERM))
        bl.append(
            Buff("HuoHuoERR", StatTypes.ERR_F, self.ally2Energy * errMul, self.ally2Role, [AtkType.ALL], 1, 1, self.ally2Role,
                 TickDown.PERM))
        if self.ally2Energy > 160:
            bl.append(
                Buff("HuoHuoUltExtraATK", StatTypes.ATK_PERCENT, 0.24, self.ally2Role, [AtkType.ALL], 1, 1,
                     self.ally2Role,
                     TickDown.PERM))
        bl.append(
            Buff("HuoHuoERR", StatTypes.ERR_F, self.ally3Energy * errMul, self.ally3Role, [AtkType.ALL], 1, 1, self.ally3Role,
                 TickDown.PERM))
        if self.ally3Energy > 160:
            bl.append(
                Buff("HuoHuoUltExtraATK", StatTypes.ATK_PERCENT, 0.24, self.ally3Role, [AtkType.ALL], 1, 1,
                     self.ally3Role,
                     TickDown.PERM))
        tl.append(
            Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ULT], [self.element], [0, 0], [0, 0], 5, self.scaling,
                 0, "HuoHuoUlt"))
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
            self.ally1MaxHP = specialRes.attr4[0]
            self.ally1HPRole = specialRes.attr4[1]
            self.ally1CurrentHP = specialRes.attr4[2]
            self.ally2MaxHP = specialRes.attr5[0]
            self.ally2HPRole = specialRes.attr5[1]
            self.ally2CurrentHP = specialRes.attr5[2]
            self.ally3MaxHP = specialRes.attr6[0]
            self.ally3HPRole = specialRes.attr6[1]
            self.ally3CurrentHP = specialRes.attr6[2]
            self.ally4MaxHP = specialRes.attr7[0]
            self.ally4HPRole = specialRes.attr7[1]
            self.ally4CurrentHP = specialRes.attr7[2]
        return super().handleSpecialStart(specialRes)

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        E3HealScale = 0.048 if self.eidolon >= 3 else 0.045
        E3HealFlat = 133.5 if self.eidolon >= 3 else 120
        if ("Skill" in turn.moveName or "Basic" in turn.moveName or "Ult" in turn.moveName) and turn.moveName not in bonusDMG and self.divineTrigger > 0:
            self.divineTrigger = max(0, self.divineTrigger - 1)
            tl.append(Turn(self.name, self.role, self.defaultTarget, Targeting.NA, [AtkType.SPECIAL], [self.element], [0, 0],
                     [0, 0], 1, self.scaling, 0, "HuoHuoAllyERR"))
            hl.append(Healing("HuoHuoTalentHealingScaling", [E3HealScale, 0], self.scaling, Role.ALL,self.role, Targeting.SINGLE))
            hl.append(Healing("HuoHuoTalentHealingFlat", [E3HealFlat, 0], Scaling.Other, Role.ALL, self.role,Targeting.SINGLE))
            if self.ally1CurrentHP <= self.ally1MaxHP:
                hl.append(Healing("HuoHuoTalentHealingScaling", [E3HealScale, 0], self.scaling, Role.ALL, self.ally1HPRole,
                                  Targeting.SINGLE))
                hl.append(Healing("HuoHuoTalentHealingFlat", [E3HealFlat, 0], Scaling.Other, Role.ALL, self.ally1HPRole,
                                  Targeting.SINGLE))
            if self.ally2CurrentHP <= self.ally2MaxHP:
                hl.append(
                    Healing("HuoHuoTalentHealingScaling", [E3HealScale, 0], self.scaling, Role.ALL, self.ally2HPRole,
                            Targeting.SINGLE))
                hl.append(Healing("HuoHuoTalentHealingFlat", [E3HealFlat, 0], Scaling.Other, Role.ALL, self.ally2HPRole,
                                  Targeting.SINGLE))
            if self.ally3CurrentHP <= self.ally3MaxHP:
                hl.append(
                    Healing("HuoHuoTalentHealingScaling", [E3HealScale, 0], self.scaling, Role.ALL, self.ally3HPRole,
                            Targeting.SINGLE))
                hl.append(Healing("HuoHuoTalentHealingFlat", [E3HealFlat, 0], Scaling.Other, Role.ALL, self.ally3HPRole,
                                  Targeting.SINGLE))
            if self.ally4CurrentHP <= self.ally4MaxHP:
                hl.append(
                    Healing("HuoHuoTalentHealingScaling", [E3HealScale, 0], self.scaling, Role.ALL, self.ally4HPRole,
                            Targeting.SINGLE))
                hl.append(Healing("HuoHuoTalentHealingFlat", [E3HealFlat, 0], Scaling.Other, Role.ALL, self.ally4HPRole,
                                  Targeting.SINGLE))
        return bl, dbl, al, dl, tl, hl