import logging

from Buff import *
from Character import Character
from Delay_Text import *
from Lightcones.Btbio import Btbio
from Planars.Lushaka import Lushaka
from RelicStats import RelicStats
from Relics.Messenger import Messenger
from Result import Result, Special
from Turn_Text import Turn

logger = logging.getLogger(__name__)


class Bronya(Character):
    # Standard Character Settings
    name = "Bronya"
    path = Path.HARMONY
    element = Element.WIND
    scaling = Scaling.ATK
    baseHP = 1241.9
    baseATK = 582.12
    baseDEF = 533.61
    baseSPD = 99
    maxEnergy = 120
    currEnergy = 60
    ultCost = 120
    currAV = 0
    dmgDct = {AtkType.BSC: 0, AtkType.BRK: 0, AtkType.FUA: 0}  # Adjust accordingly

    # Unique Character Properties
    cdStat = 0
    targetRole = Role.DPS
    e4Trigger = True

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else Btbio(wearerRole=role, targetRole=self.targetRole)
        self.relic1 = r1 if r1 else Messenger(role, 4, True)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else Lushaka(role)
        self.relicStats = subs if subs else RelicStats(3, 4, 0, 4, 4, 0, 6, 4, 4, 4, 0, 15, StatTypes.CD_PERCENT, StatTypes.Spd,
                                                       StatTypes.HP_PERCENT, StatTypes.ERR_PERCENT)
        self.rotation = rotation if rotation else ["E"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("BronyaTech", StatTypes.ATK_PERCENT, 0.15, Role.ALL, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        bl.append(Buff("BronyaBasicCR", StatTypes.CR_PERCENT, 1.0, self.role, [AtkType.BSC], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("BronyaTeamDEF", StatTypes.DEF_PERCENT, 2.0, Role.ALL, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        bl.append(Buff("BronyaTraceDMG", StatTypes.DMG_PERCENT, 0.224, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("BronyaTraceCD", StatTypes.CD_PERCENT, 0.24, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("BronyaTraceERS", StatTypes.ERS_PERCENT, 0.10, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e5Mul = 1.1 if self.eidolon >= 5 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],[e5Mul, 0], [10, 0], 20, self.scaling, 1, "BronyaBasic"))
        al.append(Advance("BronyaBasic", self.role, 0.33 if self.eidolon >= 3 else 0.30))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        spGen = 0 if (self.turn % 2 == 1 and self.eidolon >= 1) else -1
        e5Mul = 0.726 if self.eidolon >= 5 else 0.66
        e6Turns = 2 if self.eidolon == 6 else 1
        tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.SKL], [self.element], [0.0, 0], [0, 0], 30,self.scaling, spGen, "BronyaSkill"))
        bl.append(Buff("BronyaSkillDMG", StatTypes.DMG_PERCENT, e5Mul, self.targetRole, [AtkType.ALL], e6Turns, 1, self.targetRole,TickDown.END))
        if self.eidolon >= 2:
            bl.append(Buff("BronyaE2SPD", StatTypes.SPD_PERCENT, 0.30, self.targetRole, tickDown=self.targetRole,tdType=TickDown.END))
        if self.role != self.targetRole:
            al.append(Advance("BronyaForward", self.targetRole, 1.0))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e3Mul = 0.168 if self.eidolon >= 3 else 0.16
        e3Flat = 0.216 if self.eidolon >= 3 else 0.2
        tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ULT], [self.element], [0.0, 0], [0, 0], 5, self.scaling, 0, "BronyaUlt"))
        bl.append(Buff("BronyaUltATK", StatTypes.ATK_PERCENT, 0.594 if self.eidolon >= 3 else 0.55, Role.ALL, [AtkType.ALL], 2, 1,Role.SELF, TickDown.END))
        bl.append(Buff("BronyaUltCD", StatTypes.CD_PERCENT, e3Mul * self.cdStat + e3Flat, Role.ALL, [AtkType.ALL], 2, 1, Role.SELF,TickDown.END))
        return bl, dbl, al, dl, tl, hl

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useFua(enemyID)
        e5Mul = 1.1 if self.eidolon >= 5 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.FUA, AtkType.BSC],[self.element], [0.8 * e5Mul, 0], [10, 0], 5, self.scaling, 0, "BronyaFUA"))
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        self.cdStat = specialRes.attr1
        return super().handleSpecialStart(specialRes)

    def takeTurn(self) -> str:
        self.e4Trigger = True
        return super().takeTurn()

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if AtkType.BSC in turn.atkType and turn.moveName not in bonusDMG and self.e4Trigger and result.enemiesHit and self.eidolon >= 4:
            self.e4Trigger = False
            bl, dbl, al, dl, tl, hl = self.useFua(result.enemiesHit[0].enemyID)
        return bl, dbl, al, dl, tl, hl