import logging

from Buff import *
from Character import Character
from Delay_Text import *
from Lightcones.WhenSheDecidedToSee import WhenSheDecidedToSee
from Planars.RutilantArena import RutilantArena
from RelicStats import RelicStats
from Relics.ScholarLostInErudition import ScholarLostInErudition
from Result import *
from Turn_Text import Turn
from Healing import *

logger = logging.getLogger(__name__)


class YaoGuang(Character):
    # Standard Character Settings
    name = "Yao Guang"
    path = Path.ELATION
    element = Element.PHYSICAL
    scaling = Scaling.ATK
    baseHP = 1242
    baseATK = 466
    baseDEF = 655
    baseSPD = 101
    maxEnergy = 180
    currEnergy = 90
    ultCost = 180
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.ELAPUNCH: 0, AtkType.ELABANGER: 0}  # Adjust accordingly

    # Unique Character Properties
    AHASpdBuff = 0
    TotalElationChar = 0
    hasSummon = True

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else WhenSheDecidedToSee(role,1)
        self.relic1 = r1 if r1 else ScholarLostInErudition(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else RutilantArena(role)
        self.relicStats = subs if subs else RelicStats(13, 4, 0, 4, 4, 0, 3, 3, 3, 3, 0, 11, StatTypes.CR_PERCENT, StatTypes.ATK_PERCENT,
                                                       StatTypes.ATK_PERCENT,StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["E","A","A"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("BangerStartBattle", StatTypes.BANGER, 20, self.role, [AtkType.ALL], 2, 1, self.role, TickDown.END))
        bl.append(Buff("YaoGuangTraceCR", StatTypes.CR_PERCENT, 0.187, self.role))
        bl.append(Buff("YaoGuangTraceSPD", StatTypes.Spd, 9, self.role))
        bl.append(Buff("YaoGuangTraceELA", StatTypes.ELA, 0.10, self.role))
        if self.eidolon == 6:
            bl.append(Buff("YaoGuangE6MerryMake", StatTypes.MERRY, 0.25,Role.ALL))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC],
[self.element],[e3Mul, 0], [10, 0], 20, self.scaling, 1, "SparxieBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        #print(f"SKL DEBUG | TotalSP: {self.TotalSP} | Thrill: {self.Thrill} | TotalElationChar: {self.TotalElationChar} | AHASpdBuff: {self.AHASpdBuff:.3f}")

        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost

        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        if result.turnName == "AhaYaoGuangGoGo":
            return self.useElaSkill(-1)
        return bl, dbl, al, dl, tl, hl

    def useElaSkill(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useElaSkill(enemyID)

        bl.append(Buff("BangerELASkill", StatTypes.BANGER, self.Punchline , self.role, [AtkType.ALL], 2, 1, self.role,TickDown.END))
        self.Punchline = self.TotalElationChar  # ← consumed then reset to TotalElationChar base
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.AHASpdBuff = specialRes.attr1
        self.TotalElationChar = specialRes.attr2
        bl.append(Buff("AhaSpdBuff", StatTypes.Spd, self.AHASpdBuff, Role.AHA, [AtkType.SPECIAL], 1, 1, Role.AHA,TickDown.START))
        return bl, dbl, al, dl, tl, hl
