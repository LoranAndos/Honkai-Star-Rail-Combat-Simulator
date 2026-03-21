import logging

from Buff import *
from Character import Character
from Delay_Text import *
from Lightcones.CruisingInTheStellarSea import CruisingInTheStellarSea
from Planars.RutilantArena import RutilantArena
from RelicStats import RelicStats
from Relics.ScholarLostInErudition import ScholarLostInErudition
from Result import *
from Turn_Text import Turn
from Healing import *
from random import random

logger = logging.getLogger(__name__)


class Sparxie(Character):
    # Standard Character Settings
    name = "Sparxie"
    path = Path.ELATION
    element = Element.FIRE
    scaling = Scaling.ATK
    baseHP = 1048
    baseATK = 640
    baseDEF = 461
    baseSPD = 107
    maxEnergy = 160
    currEnergy = 80
    ultCost = 160
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.ELABANGER: 0, AtkType.ELAPUNCH: 0}  # Adjust accordingly

    # Unique Character Properties
    AHASpdBuff = 0
    AtkStat = 0
    TotalSP = 0
    TotalElationChar = 0

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, targetRole=Role.DPS, quaAllies=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else CruisingInTheStellarSea(role)
        self.relic1 = r1 if r1 else ScholarLostInErudition(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else RutilantArena(role)
        self.relicStats = subs if subs else RelicStats(13, 4, 0, 4, 4, 0, 3, 3, 3, 3, 0, 11, StatTypes.CD_PERCENT, StatTypes.Spd,
                                                       StatTypes.HP_PERCENT,StatTypes.ERR_PERCENT)
        self.targetRole = targetRole
        self.quaAllies = quaAllies
        self.rotation = rotation if rotation else ["E"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("BangerStartBattle", StatTypes.BANGER, 20, self.role, [AtkType.ELABANGER],1,1,self.role,TickDown.END))
        bl.append(Buff("SparxieTraceCR", StatTypes.CR_PERCENT, 0.12, self.role))
        bl.append(Buff("SparxieTraceCD", StatTypes.CD_PERCENT, 0.133, self.role))
        bl.append(Buff("SparxieTraceELA", StatTypes.ELA, 0.28, self.role))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],[e3Mul, 0], [10, 0], 30, self.scaling, 1, "SparxieBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e3Big1 = 1.1 if self.eidolon >= 3 else 1.0
        e3Small1 = 0.22 if self.eidolon >= 3 else 0.2
        e3Big3 = 0.55 if self.eidolon >= 3 else 0.5
        e3Small3 = 0.11 if self.eidolon >= 3 else 0.1
        tries = self.TotalSP
        successes = sum(random() < 0.2 for _ in range(tries))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.BLAST, [AtkType.BSC],
        [self.element],[e3Big1+e3Small1*(self.TotalSP+successes*2), e3Big3+e3Small3*(self.TotalSP+successes*2)],
        [10, 5], 40, self.scaling, -self.TotalSP+1, "SparxieSkill"))
        bl.append(Buff("SparxieSkillPunch", StatTypes.PUNCH, self.TotalSP+successes*2, self.role, [AtkType.SPECIAL  ], 1, 1, Role.ALL,TickDown.START))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)

        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.AHASpdBuff = specialRes.attr1
        self.AtkStat = specialRes.attr2
        self.TotalSP = specialRes.attr3
        self.TotalElationChar = specialRes.attr4
        return bl, dbl, al, dl, tl, hl