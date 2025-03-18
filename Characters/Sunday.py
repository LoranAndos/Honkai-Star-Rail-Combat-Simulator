import logging

from Character import Character
from RelicStats import RelicStats
from Result import *
from Buff import *
from Delay_Text import *
from Lightcones.Ascent import AscentSunday
from Lightcones.Btbio import Btbio
from Relics.Sacerdos import SacerdosSunday
from Planars.Keel import Keel
from Turn_Text import Turn

logger = logging.getLogger(__name__)


class Sunday(Character):
    # Standard Character Settings
    name = "Sunday"
    path = Path.HARMONY
    element = Element.IMAGINARY
    scaling = Scaling.ATK
    baseHP = 1241.9
    baseATK = 737.35
    baseDEF = 533.61
    baseSPD = 96
    maxEnergy = 130
    currEnergy = 65 + 25  # Bonus 25 from major trace 2
    ultCost = 130
    currAV = 0
    dmgDct = {AtkType.BSC: 0, AtkType.BRK: 0}  # Adjust accordingly

    # Unique Character Properties
    targetSummonRole = None
    targetEnergyCap = None
    cdStat = None
    targetCR = None

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT, targetRole=Role.DPS) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else AscentSunday(role, level=1, targetRole=targetRole)
        self.relic1 = r1 if r1 else SacerdosSunday(role, 4, targetRole=targetRole)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else Keel(role)
        # Fast Sunday Build RelicStats(14, 4, 0, 4, 4, 0, 4, 4, 4, 4, 0, 6, Pwr.CD_PERCENT, Pwr.SPD, Pwr.DEF_PERCENT, Pwr.HP_PERCENT)
        # Normal Sunday Build RelicStats(4, 4, 0, 4, 4, 0, 4, 4, 4, 10, 0, 10, Pwr.CD_PERCENT, Pwr.SPD, Pwr.DEF_PERCENT, Pwr.HP_PERCENT)
        self.relicStats = subs if subs else RelicStats(4, 4, 0, 4, 4, 0, 4, 4, 4, 10, 0, 10, StatTypes.CD_PERCENT, StatTypes.Spd,
                                                       StatTypes.DEF_PERCENT, StatTypes.ERR_PERCENT)
        self.eidolon = eidolon
        self.rotation = rotation if rotation else ["E"]
        self.targetRole = targetRole

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("SundayTraceCD", StatTypes.CD_PERCENT, 0.373, self.role, [AtkType.ALL]))
        bl.append(Buff("SundayTraceERS", StatTypes.ERS_PERCENT, 0.18, self.role, [AtkType.ALL]))
        bl.append(Buff("SundayTraceDEF", StatTypes.DEF_PERCENT, 0.125, self.role, [AtkType.ALL]))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [Element.IMAGINARY],[e3Mul, 0], [0, 0], 20, Scaling.ATK, 1, "SundayBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        sp = 0 if self.turn % 2 == 1 else -1
        dmgbuffMul = 2 if self.targetSummonRole is not None else 1
        e5DMG = 0.44 if self.eidolon >= 5 else 0.40
        e5CR = 0.22 if self.eidolon >= 5 else 0.20
        e6Stacks = 3 if self.eidolon >= 6 else 1
        bl.append(Buff("SundaySklDMG", StatTypes.DMG_PERCENT, e5DMG * dmgbuffMul, self.targetRole, [AtkType.ALL], 2, 1, self.role, TickDown.END))
        bl.append(Buff("SundaySklCR", StatTypes.CR_PERCENT, e5CR, self.targetRole, [AtkType.ALL], 2, e6Stacks, self.role, TickDown.END))
        if self.eidolon >= 1:
            bl.append(Buff("SundayE1RP", StatTypes.PEN, 0.20, self.targetRole, [AtkType.ALL], 2, 1, self.role, TickDown.START))
        tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.SKL], [self.element], [0, 0], [0, 0], 30,self.scaling, sp, "SundaySkill"))
        if self.targetSummonRole is not None:
            al.append(Advance("SundaySummonADV", self.targetSummonRole, 1.0))
        al.append(Advance("SundayTargetADV", self.targetRole, 1.0))
        al.append(Advance("SundayTargetADV", self.targetRole, 0.1))  # Forces character to act before their summon
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e3Mul = 0.28 if self.eidolon >= 3 else 0.25
        e3Add = 0.0832 if self.eidolon >= 3 else 0.08
        bl.append(Buff("SundayUltERR", StatTypes.ERR_F, self.targetEnergyCap * 0.2, self.targetRole, [AtkType.ALL]))
        bl.append(Buff("SundayBeatified", StatTypes.CD_PERCENT, self.cdStat * e3Mul + e3Add, self.targetRole, [AtkType.ALL], 3, 1,self.role, TickDown.END))
        if self.eidolon >= 2:
            bl.append(
                Buff("SundayE2SelfSPD", StatTypes.SPD_PERCENT, 0.20, self.role, [AtkType.ALL], 3, 1, self.role, TickDown.END))
            bl.append(Buff("SundayE2TargetSPD", StatTypes.SPD_PERCENT, 0.20, self.targetRole, [AtkType.ALL], 3, 1, self.role,
                           TickDown.END))
        if self.eidolon == 6:
            bl.append(Buff("SundaySklCR", StatTypes.CR_PERCENT, 0.22, self.targetRole, [AtkType.ALL], 2, 3, self.role,TickDown.END))
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.targetSummonRole = specialRes.attr1
        self.targetEnergyCap = specialRes.attr2
        self.cdStat = specialRes.attr3
        if self.eidolon >= 4 and specialRes.attr4:
            bl.append(Buff("SundayE4ERR", StatTypes.ERR_T, 8, self.role))
        return bl, dbl, al, dl, tl, hl

    def handleSpecialEnd(self, specialRes):
        bl, dbl, al, dl, tl, hl = super().handleSpecialEnd(specialRes)
        self.targetCR = specialRes.attr1
        excessCR = max(0, self.targetCR - 1.0)
        if self.eidolon == 6:
            bl.append(Buff("SundayE6CD", StatTypes.CD_PERCENT, excessCR * 2, self.targetRole))
        return bl, dbl, al, dl, tl, hl