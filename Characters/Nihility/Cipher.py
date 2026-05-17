import logging

from Buff import *
from Character import Character
from Lightcones.Nihility.ReforgedInHellfire import ReforgedInHellfire
from Lightcones.Nihility.ResolutionShinesAsPearlsOfSweat import ResolutionMortenaxBlade
from Lightcones.Nihility.GoodNightAndSleepWell import GoodNightAndSleepWell
from Planars.BoneCollectionsSereneDemesne import BoneCollectionsSereneDemesne
from Planars.DuranDynastyOfRunningWolves import DuranDynastyOfRunningWolves
from Planars.LushakaTheSunkenSeas import LushakaTheSunkenSeas
from RelicStats import RelicStats
from Relics.DivineQueryingMasterSmith import DivineQueryMasterSmith
from Result import *
from Turn_Text import Turn
from Healing import *

logger = logging.getLogger(__name__)


class Cipher(Character):
    # Standard Character Settings
    name = "Cipher"
    path = Path.NIHILITY
    element = Element.LIGHTNING
    scaling = Scaling.ATK
    baseHP = 931
    baseATK = 640
    baseDEF = 509
    baseSPD = 106
    maxEnergy = 130
    currEnergy = 65
    ultCost = 130
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.FUA: 0}  # Adjust accordingly

    # Unique Character Properties
    SpdStat = 0.0
    TallyMultiplier = 1.0

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else ResolutionMortenaxBlade(role, 5)
        self.relic1 = r1 if r1 else DivineQueryMasterSmith(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else LushakaTheSunkenSeas(role)
        self.relicStats = subs if subs else RelicStats(10, 2, 2, 2, 2, 2, 2, 2, 7, 2, 10, 2, StatTypes.EHR_PERCENT, StatTypes.SPD,
                                                       StatTypes.HP_PERCENT, StatTypes.ERR_PERCENT)
        self.rotation = rotation if rotation else ["E"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("CipherTraceSPD", StatTypes.SPD, 14, self.role))
        bl.append(Buff("CipherTraceEHR", StatTypes.EHR_PERCENT, 0.10, self.role))
        bl.append(Buff("CipherTraceDMG", StatTypes.DMG_PERCENT, 0.144, self.role))
        bl.append(Buff("Talent3CD", StatTypes.CD_PERCENT, 1.00, self.role, [AtkType.FUA], 1, 1, Role.SELF, TickDown.PERM))
        dbl.append(Debuff("CipherTrace3Vuln", self.role, StatTypes.VULN, 0.40, Role.ALL, [AtkType.ALL], 1000,1,Targeting.AOE))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20, self.scaling, 1, "CipherBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e5MulMain = 2.2 if self.eidolon >= 5 else 2.0
        e5MulSide = 1.1 if self.eidolon >= 5 else 1.0
        dbl.append(Debuff("CipherSkillDmgReduction", self.role, StatTypes.ENEMY_DMG_REDUCTION, 0.10, self.bestEnemy(enemyID), [AtkType.ALL], 2,1,Targeting.BLAST))
        bl.append(Buff("CipherSkillAttack", StatTypes.ATK_PERCENT, 0.30, self.role, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.BLAST, [AtkType.SKL], [self.element],
                       [e5MulMain, e5MulSide], [20, 10], 30, self.scaling, -1, "CipherSkill"))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        return bl, dbl, al, dl, tl, hl

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useFua(enemyID)
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        return bl, dbl, al, dl, tl, hl

    def useHit(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useHit(enemyID)
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.SpdStat = specialRes.attr1
        if 170 > self.SpdStat >= 140:
            bl.append(Buff("Talent1CR", StatTypes.CR_PERCENT, 0.25, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
            self.TallyMultiplier += 0.50
        elif self.SpdStat >= 170:
            bl.append(Buff("Talent1CR", StatTypes.CR_PERCENT, 0.50, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
            self.TallyMultiplier += 1.0
        return bl, dbl, al, dl, tl, hl