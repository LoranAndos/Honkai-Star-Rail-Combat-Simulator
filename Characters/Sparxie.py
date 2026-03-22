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
from math import floor

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
    ELAStat = 0
    ELABanger = 0
    Thrill = 0
    tech = True

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
        bl.append(Buff("BangerStartBattle", StatTypes.BANGER, 20, self.role, [AtkType.SPECIAL],1,1,self.role,TickDown.END))
        bl.append(Buff("SparxieTraceCR", StatTypes.CR_PERCENT, 0.12, self.role))
        bl.append(Buff("SparxieTraceCD", StatTypes.CD_PERCENT, 0.133, self.role))
        bl.append(Buff("SparxieTraceELA", StatTypes.ELA, 0.28, self.role))
        if self.eidolon == 6:
            bl.append(Buff("SparxieE6ResPen", StatTypes.PEN, 0.20,Role.ALL))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC],
[self.element],[e3Mul, 0], [10, 0], 20, self.scaling, 1, "SparxieBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e3Big1 = 1.1 if self.eidolon >= 3 else 1.0
        e3Small1 = 0.22 if self.eidolon >= 3 else 0.2
        e3Big3 = 0.55 if self.eidolon >= 3 else 0.5
        e3Small3 = 0.11 if self.eidolon >= 3 else 0.1
        e5MulEla1 = 0.44 if self.eidolon >= 5 else 0.4
        e5MulEla3 = 0.22 if self.eidolon >= 5 else 0.2
        tries = self.TotalSP + self.Thrill + floor((self.TotalSP+self.Thrill)*0.2*2)
        successes = sum(random() < 0.2 for _ in range(tries))
        SPUsed = min(self.TotalSP+successes*2+self.Thrill,20)
        bl.append(Buff("SparxieSkillPunch", StatTypes.PUNCH, SPUsed + successes, Role.ALL, [AtkType.SPECIAL], 1, 1,self.role, TickDown.START))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.BLAST, [AtkType.BSC],
        [self.element],[e3Big1+e3Small1*SPUsed, e3Big3+e3Small3*SPUsed],
        [10, 5], 40, self.scaling, max(-self.TotalSP+1,-20+successes*2+self.Thrill+self.TotalSP), "SparxieSkill"))
        if self.ELABanger >= 1:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.BLAST, [AtkType.ELABANGER],
                           [self.element], [e5MulEla1, e5MulEla3], [5, 0], 0, self.ELAStat, 0, "SparxieSkillEla"))
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ELABANGER],
                               [self.element], [e5MulEla3*SPUsed, 0], [5*SPUsed, 0], 0, self.ELAStat, 0, "SparxieSkillEla"))
        if self.eidolon >= 2:
            bl.append(Buff("SparxieE2CDBuff", StatTypes.CD_PERCENT, min(self.Thrill*0.1,0.4), self.role, [AtkType.ALL], 2, 1,self.role, TickDown.END))
        self.Thrill = 0
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        e5MulReg = 0.52 + 0.6*self.ELAStat if self.eidolon >= 5 else 0.5 + 0.6*self.ELAStat
        e5MulEla = 0.528 if self.eidolon >= 5 else 0.48
        bl.append(Buff("SparxieUltPunch", StatTypes.PUNCH, 2 + 2^min(self.TotalElationChar,3), Role.ALL, [AtkType.SPECIAL], 1, 1,self.role, TickDown.START))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT],
                       [self.element], [e5MulReg, 0], [20, 0], 5, self.scaling, 0, "SparxieUltReg"))
        if self.ELABanger >= 1:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELABANGER],
                           [self.element], [e5MulEla, 0], [0, 0], 0, self.ELAStat, 0, "SparxieUltEla"))
        if self.TotalElationChar >= 3:
            self.Thrill += 4
        else:
            self.Thrill += 1
        if self.eidolon >= 4:
            bl.append(Buff("SparxieE4Punch", StatTypes.PUNCH, 5, Role.ALL,[AtkType.SPECIAL], 1, 1, self.role, TickDown.START))
            bl.append(Buff("SparxieE4Ela", StatTypes.ELA,0.36, self.role,[AtkType.ALL], 1, 1, Role.ALL, TickDown.START))
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if self.eidolon >= 5:
            e5MulBig = 0.55
            e5MulSmall = 0.275
        elif 5 < self.eidolon >= 3:
            e5MulBig = 0.525
            e5MulSmall = 0.2625
        else:
            e5MulBig = 0.5
            e5MulSmall = 0.25
        E6ExtraProc = min(self.Punchline,40) if self.eidolon == 6 else 0
        if turn.moveName == "AhaSparxie":
            tl.append(Turn(self.name, self.role, result.enemiesHit[0].enemyID, Targeting.AOE, [AtkType.ELAPUNCH],
                           [self.element], [e5MulBig, 0], [6.67, 0], 5, self.ELAStat, 0, "SparxieElaSkillBig"))
            tl.append(Turn(self.name, self.role, result.enemiesHit[0].enemyID, Targeting.SINGLE, [AtkType.ELAPUNCH],
                           [self.element], [e5MulSmall*(20+E6ExtraProc), 0], [1.67*(20+E6ExtraProc), 0], 0, self.ELAStat, 0, "SparxieElaSkillSmall"))
            self.Thrill += 2
            self.Punchline = 0 + self.TotalElationChar
        if turn.moveName == "AhaEnd" and self.eidolon >= 1:
            bl.append(Buff("SparxieE1AhaPunch", StatTypes.PUNCH, 5, Role.ALL,[AtkType.SPECIAL], 1, 1, self.role, TickDown.START))
        if turn.moveName == "AhaEnd" and self.eidolon >= 2:
            bl, dbl, al, dl, tl, hl = self.extendLists(bl, dbl, al, dl, tl, hl, *self.useSkl(result.enemiesHit[0].enemyID))
            self.Thrill += 2
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.AHASpdBuff = specialRes.attr1
        self.AtkStat = specialRes.attr2
        self.TotalSP = specialRes.attr3
        self.TotalElationChar = specialRes.attr4
        self.ELAStat = specialRes.attr5
        self.ElaBanger = specialRes.attr6
        bl.append(Buff("AhaSpdBuff",StatTypes.Spd,self.AHASpdBuff,Role.AHA,[AtkType.SPECIAL],1,1,Role.AHA,TickDown.START))
        if self.tech:
            tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.TECH], [self.element], [0, 0], [0, 0], 0,self.scaling,2, "SparxieTech"))
            self.tech = False
        bl.append(Buff("SparxieATKtoELA", StatTypes.ELA, min(floor((self.AtkStat-2000)/100)*0.05,0.8), self.role, [AtkType.ALL], 1, 1,Role.SELF, TickDown.START))
        bl.append(Buff("SparxiePunchtoCD", StatTypes.CD_PERCENT, min(self.Punchline*0.08, 0.8), Role.ALL,[AtkType.ALL], 1, 1, self.role, TickDown.START))
        if self.eidolon >= 1:
            bl.append(Buff("SparxiePunchtoPEN", StatTypes.PEN, min(self.Punchline*0.015, 0.15), Role.ALL,[AtkType.ALL], 1, 1, self.role, TickDown.START))
        return bl, dbl, al, dl, tl, hl