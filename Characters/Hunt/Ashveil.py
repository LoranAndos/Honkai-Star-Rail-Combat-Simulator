import logging

from Buff import *
from Character import Character
from Lightcones.Nihility.ReforgedInHellfire import ReforgedInHellfire
from Lightcones.Nihility.ResolutionShinesAsPearlsOfSweat import ResolutionMortenaxBlade
from Lightcones.Nihility.GoodNightAndSleepWell import GoodNightAndSleepWell
from Planars.BoneCollectionsSereneDemesne import BoneCollectionsSereneDemesne
from RelicStats import RelicStats
from Relics.DivineQueryingMasterSmith import DivineQueryMasterSmith
from Result import *
from Turn_Text import Turn
from Healing import *

logger = logging.getLogger(__name__)


class Ashveil(Character):
    # Standard Character Settings
    name = "MortenaxBlade"
    path = Path.HUNT
    element = Element.LIGHTNING
    scaling = Scaling.ATK
    baseHP = 854
    baseATK = 776
    baseDEF = 388
    baseSPD = 106
    maxEnergy = 150
    currEnergy = 75
    ultCost = 150
    currAV = 0
    aggro = 75
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.FUA: 0}  # Adjust accordingly

    # Unique Character Properties

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else GoodNightAndSleepWell(role, 5)
        self.relic1 = r1 if r1 else DivineQueryMasterSmith(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else BoneCollectionsSereneDemesne(role)
        self.relicStats = subs if subs else RelicStats(6, 2, 2, 2, 7, 2, 2, 2, 2, 2, 12, 4, StatTypes.CR_PERCENT, StatTypes.SPD,
                                                       StatTypes.HP_PERCENT, StatTypes.ERR_PERCENT)
        self.rotation = rotation if rotation else ["E"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("MortenaxBladeTraceCR", StatTypes.CR_PERCENT, 0.12, self.role))
        bl.append(Buff("MortenaxBladeTraceHP", StatTypes.HP_PERCENT, 0.10, self.role))
        bl.append(Buff("MortenaxBladeTraceDMG", StatTypes.DMG_PERCENT, 0.224, self.role))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)

        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)

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

        return bl, dbl, al, dl, tl, hl
