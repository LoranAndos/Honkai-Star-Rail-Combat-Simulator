import logging

from Buff import *
from Character import Character
from Lightcones.Hunt.TheFinaleOfALie import TheFinaleOfALie
from Lightcones.Hunt.CruisingInTheStellarSea import CruisingInTheStellarSea
from Planars.RutilantArena import RutilantArena
from RelicStats import RelicStats
from Relics.GeniusOfBrilliantStars import GeniusOfBrilliantStars
from Result import *
from Turn_Text import Turn
from Healing import *

logger = logging.getLogger(__name__)


class RinTohsaka(Character):
    # Standard Character Settings
    name = "RinTohsaka"
    path = Path.ERUDITION
    element = Element.QUANTUM
    scaling = Scaling.ATK
    baseHP = 1048
    baseATK = 699
    baseDEF = 461
    baseSPD = 102
    maxEnergy = 160
    currEnergy = 80
    ultCost = 160
    currAV = 0
    aggro = 75
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.FUA: 0}  # Adjust accordingly

    # Unique Character Properties
    GemEnergy = 20
    SPAmount = 0
    EnhancedSkill = False
    SkillGemMultiplier = 1

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope
    # With Sparkle:
    # self.relicStats = subs if subs else RelicStats(2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 14, 9, StatTypes.CR_PERCENT, StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT)

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else CruisingInTheStellarSea(role, 5)
        self.relic1 = r1 if r1 else GeniusOfBrilliantStars(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else RutilantArena(role)
        self.relicStats = subs if subs else RelicStats(2, 2, 2, 2, 2, 3, 2, 2, 2, 2, 12, 11, StatTypes.CR_PERCENT, StatTypes.ATK_PERCENT,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["E"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("RinTohsakaTraceCD", StatTypes.CD_PERCENT, 0.373, self.role))
        bl.append(Buff("RinTohsakaTraceATK", StatTypes.ATK_PERCENT, 0.18, self.role))
        bl.append(Buff("RinTohsakaTraceDMG", StatTypes.DMG_PERCENT, 0.08, self.role))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20, self.scaling, 1, "RinTohsakaBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e3Mul = 0.99 if self.eidolon >= 3 else 0.90
        e3MulNormal = 1.98 if self.eidolon >= 3 else 1.80
        if self.EnhancedSkill:
            ExtraHits = min(self.GemEnergy//3,33)
            logger.info(f"Amount of extraHits from EnhancedSkill = {ExtraHits} from {self.GemEnergy} Gem Energy")
            SPUsage = 0 if self.SPAmount <= 2 else self.SPAmount -2
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.SKL], [self.element],
                     [e3Mul, 0], [20, 0], 0, self.scaling, 0, "RinTohsakaSkillAOE"))
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.SKL], [self.element],
                     [e3Mul*ExtraHits, 0], [2*ExtraHits, 0], 30, self.scaling, SPUsage, "RinTohsakaSkillSingle"))
            self.GemEnergy -= 3*ExtraHits
            self.SkillGemMultiplier = 2
        else:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.SKL], [self.element],
                     [e3MulNormal, 0], [20, 0], 30, self.scaling, -1, "RinTohsakaSkill"))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e5Main = 4.40 if self.eidolon >= 5 else 4.0
        e5Side = 2.20 if self.eidolon >= 5 else 2.0
        e5Vuln = 0.22 if self.eidolon >= 5 else 0.20
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ULT], [self.element],
                       [e5Main, 0], [10, 0], 0, self.scaling, 0, "RinTohsakaUltMain"))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT], [self.element],
                       [e5Side, 0], [20, 0], 5, self.scaling, 1, "RinTohsakaUltSide"))
        dbl.append(Debuff("RinTohsakaUltVuln", self.role, StatTypes.VULN, e5Vuln, Role.ALL, [AtkType.ALL], 3,1,Targeting.AOE))
        self.GemEnergy += 12
        return bl, dbl, al, dl, tl, hl

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useFua(enemyID)

        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        e5CD = 1.10 if self.eidolon >= 5 else 1.00
        if turn.spChange != 0:
            self.GemEnergy += abs(turn.spChange) * self.SkillGemMultiplier
            self.SkillGemMultiplier = 1
            bl.append(Buff("TalentCD", StatTypes.CD_PERCENT, e5CD, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.END))
            logger.info(f"Rin has obtained {abs(turn.spChange)} Gem Energy and now has {self.GemEnergy} Gem Energy")
        if self.SPAmount >= 7 or self.GemEnergy >= 15:
            self.EnhancedSkill = True
            logger.info(f"Rin can use Enhanced Skill")
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        e5CD = 1.10 if self.eidolon >= 5 else 1.00
        if turn.spChange != 0:
            self.GemEnergy += abs(turn.spChange)
            bl.append(Buff("TalentCD", StatTypes.CD_PERCENT, e5CD, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.END))
            logger.info(f"Rin has obtained {abs(turn.spChange)} Gem Energy and now has {self.GemEnergy} Gem Energy")
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.SPAmount = specialRes.attr1
        return bl, dbl, al, dl, tl, hl