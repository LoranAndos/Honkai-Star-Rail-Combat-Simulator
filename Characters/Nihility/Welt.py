import logging

from Buff import *
from Character import Character
from Attributes import *
from Lightcones.Nihility.ResolutionShinesAsPearlsOfSweat import ResolutionMortenaxBlade
from Lightcones.Nihility.LiesDanceOnTheBreeze import LiesDanceOnTheBreeze
from Planars.LushakaTheSunkenSeas import LushakaTheSunkenSeas
from RelicStats import RelicStats
from Relics.PioneerDiverOfDeadWaters import PioneerCipher
from Result import *
from Turn_Text import Turn
from Healing import *

logger = logging.getLogger(__name__)


class Welt(Character):
    # Standard Character Settings
    name = "Welt"
    path = Path.NIHILITY
    element = Element.IMAGINARY
    scaling = Scaling.ATK
    baseHP = 1125
    baseATK = 621
    baseDEF = 509
    baseSPD = 102
    maxEnergy = 120
    currEnergy = 60
    ultCost = 120
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.ADD: 0,}  # Adjust accordingly

    # Unique Character Properties

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else ResolutionMortenaxBlade(role, 5)
        self.relic1 = r1 if r1 else PioneerCipher(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else LushakaTheSunkenSeas(role)
        self.relicStats = subs if subs else RelicStats(12, 2, 2, 2, 2, 2, 2, 2, 4, 2, 10, 2, StatTypes.EHR_PERCENT, StatTypes.SPD,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["E"]

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("WeltTraceERS", StatTypes.ERS_PERCENT, 0.10, self.role))
        bl.append(Buff("WeltTraceEHR", StatTypes.EHR_PERCENT, 0.28, self.role))
        bl.append(Buff("WeltTraceDMG", StatTypes.DMG_PERCENT, 0.144, self.role))

        return bl, dbl, al, dl, hl, sl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20, self.scaling, 1, "WeltBasic"))
        return bl, dbl, al, dl, tl, hl, sl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useSkl(enemyID)
        e3Mul = 0.792 if self.eidolon >= 3 else 0.72
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.SKL], [self.element],
                       [e3Mul, 0], [10, 0], 6, self.scaling, -1, "WeltSkill"))
        for i in range(4):
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.SKL], [self.element],
                     [e3Mul, 0], [10, 0], 6, self.scaling, 0, "WeltSkillExtra"))

        return bl, dbl, al, dl, tl, hl, sl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost

        return bl, dbl, al, dl, tl, hl, sl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().ownTurn(turn, result)

        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)

        return bl, dbl, al, dl, tl, hl, sl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)

        return bl, dbl, al, dl, tl, hl, sl