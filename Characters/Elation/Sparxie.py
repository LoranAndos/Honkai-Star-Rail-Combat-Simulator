import logging

from Buff import *
from Character import Character
from Lightcones.Elation.DazzledByAFloweryWorld import DazzledByAFloweryWorld
from Planars.TengokuLivestream import TengokuLivestream
from RelicStats import RelicStats
from Relics.EverGloriousMagicalGirl import EverGloriousMagicalGirl
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
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.ELAPUNCH: 0, AtkType.ELABANGER: 0}  # Adjust accordingly

    # Unique Character Properties
    AHASpdBuff = 0
    AtkStat = 0
    TotalSP = 0
    TotalElationChar = 0
    ELAStat = 0
    Banger = 0
    Thrill = 0
    prePunchline = 0
    tech = True
    hasSummon = True

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT,
                 elationParticipationID=144) -> None:  # SPARXIE ID: 144
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else DazzledByAFloweryWorld(role, 1)
        self.relic1 = r1 if r1 else EverGloriousMagicalGirl(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else TengokuLivestream(role)
        self.relicStats = subs if subs else RelicStats(7, 2, 2, 2, 2, 5, 2, 2, 2, 2, 9, 9, StatTypes.CR_PERCENT, StatTypes.SPD,
                                                       StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["E"]
        self.elationParticipationID = elationParticipationID

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("BangerStartBattle", StatTypes.BANGER, 20, self.role, [AtkType.ALL], 2, 1, self.role, TickDown.END))
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
        #print(f"SKL DEBUG | TotalSP: {self.TotalSP} | Thrill: {self.Thrill} | TotalElationChar: {self.TotalElationChar} | AHASpdBuff: {self.AHASpdBuff:.3f}")
        e3Big1 = 1.1 if self.eidolon >= 3 else 1.0
        e3Small1 = 0.22 if self.eidolon >= 3 else 0.2
        e3Big3 = 0.55 if self.eidolon >= 3 else 0.5
        e3Small3 = 0.11 if self.eidolon >= 3 else 0.1
        e5MulEla1 = 0.44 if self.eidolon >= 5 else 0.4
        e5MulEla3 = 0.22 if self.eidolon >= 5 else 0.2
        totalPunch = 0
        spGain = 0
        SPUsed = min(self.TotalSP + self.Thrill, 20)

        # Roll once per SP consumed
        for _ in range(SPUsed):
            if random() < 0.2:  # "Straight Fire"
                totalPunch += 2
                spGain += 2
            else:  # "Unreal Banger"
                totalPunch += 1

        spGain = min(spGain, SPUsed)  # ← add here, can't gain back more than consumed

        # Roll for bonus SP from Straight Fire, capped at 20 total
        bonusSPConsumed = min(spGain, 20 - SPUsed)
        for _ in range(bonusSPConsumed):
            if random() < 0.2:  # "Straight Fire"
                totalPunch += 2
            else:  # "Unreal Banger"
                totalPunch += 1

        totalSPConsumed = SPUsed + bonusSPConsumed
        realSPConsumed = min(self.TotalSP, SPUsed)  # only real SP, not Thrill

        Character.SharedPunchline += totalPunch

        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.BLAST, [AtkType.BSC],
                       [self.element], [e3Big1 + e3Small1 * totalSPConsumed, e3Big3 + e3Small3 * totalSPConsumed],
                       [10, 5], 40, self.scaling, -self.TotalSP+1, "SparxieSkill"))

        if self.Banger >= 1:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.BLAST, [AtkType.ELABANGER],
                           [self.element], [e5MulEla1, e5MulEla3], [5, 0], 0, Scaling.ELA, 0, "SparxieSkillEla"))
            engagementProcs = min(totalSPConsumed, 20)
            tl.append(Turn(self.name, self.role, -1, Targeting.SINGLE, [AtkType.ELABANGER],
                               [self.element], [e5MulEla3*engagementProcs, 0], [0, 0], 0, Scaling.ELA, 0, "SparxieSkillElaExtra"))

        if self.eidolon >= 2:
            bl.append(
                Buff("SparxieE2CDBuff", StatTypes.CD_PERCENT, min(self.Thrill * 0.1, 0.4), self.role, [AtkType.ALL], 2,
                     1, self.role, TickDown.END))

        self.Thrill = 0
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e5MulReg = 0.52 + 0.6 * self.ELAStat if self.eidolon >= 5 else 0.5 + 0.6 * self.ELAStat
        e5MulEla = 0.528 if self.eidolon >= 5 else 0.48

        # Base 2 Punchline from ult
        Character.SharedPunchline += 2

        # Additional Punchline and Thrill based on Elation character count
        if self.TotalElationChar >= 3:
            Character.SharedPunchline += 8
            self.addThrill(4)
        elif self.TotalElationChar == 2:
            Character.SharedPunchline += 4
            self.addThrill(1)
        elif self.TotalElationChar == 1:
            Character.SharedPunchline += 2
            self.addThrill(1)

        # Base ult DMG — ATK scaling with Elation modifier
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT],
                       [self.element], [e5MulReg, 0], [20, 0], 5, self.scaling, 0, "SparxieUltReg"))

        # Certified Banger additional Elation hit on ult
        if self.Banger >= 1:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELABANGER],
                           [self.element], [e5MulEla, 0], [0, 0], 0, Scaling.ELA, 0, "SparxieUltEla"))

        if self.eidolon >= 4:
            Character.SharedPunchline += 5
            bl.append(
                Buff("SparxieE4Ela", StatTypes.ELA, 0.36, self.role, [AtkType.ALL], 3, 1, self.role, TickDown.END))
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        if result.turnName == "AhaSparxieGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        if self.eidolon >= 1 and result.turnName == "AhaElationSequenceComplete":
            Character.SharedPunchline += 5
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if result.turnName == "AhaSparxieGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        return bl, dbl, al, dl, tl, hl

    def useElaSkill(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useElaSkill(enemyID)
        if self.eidolon >= 5:
            e5MulBig = 0.55
            e5MulSmall = 0.275
        elif 5 > self.eidolon >= 3:
            e5MulBig = 0.525
            e5MulSmall = 0.2625
        else:
            e5MulBig = 0.5
            e5MulSmall = 0.25
        E6ExtraProc = min(self.Punchline, 40) if self.eidolon == 6 else 0

        if Character.ahaFixedPunchline:
            self.savedPunchline = self.SharedPunchline
            self.prePunchline = self.SharedPunchline
            self.SharedPunchline = Character.ahaFixedPunchlineValue
        else:
            self.prePunchline = self.SharedPunchline

        #print(f"DEBUG {self.name} useElaSkill | SharedPunchline: {Character.SharedPunchline} | ahaFixedPunchline: {Character.ahaFixedPunchline}")

        tl.append(Turn(self.name, self.role, -1, Targeting.AOE, [AtkType.ELAPUNCH],
                [self.element], [e5MulBig * Character.ahaElaDMGBoost, 0], [6.67, 0], 5, Scaling.ELA, 0, "SparxieElaSkillBig"))
        tl.append(Turn(self.name, self.role, -1, Targeting.SINGLE, [AtkType.ELAPUNCH],
                [self.element], [e5MulSmall * (20 + E6ExtraProc) * Character.ahaElaDMGBoost, 0], [1.67 * (20 + E6ExtraProc), 0], 0,
                        Scaling.ELA, 0, "SparxieElaSkillSmall"))
        self.addThrill(2)
        if self.eidolon >= 2:
            bl, dbl, al, dl, tl, hl = self.extendLists(bl, dbl, al, dl, tl, hl, *self.useSkl(-1))
            self.addThrill(2)
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.AHASpdBuff = specialRes.attr1
        self.AtkStat = specialRes.attr2
        self.TotalSP = specialRes.attr3
        self.TotalElationChar = specialRes.attr4
        self.ELAStat = specialRes.attr5
        self.Banger = specialRes.attr6
        bl.append(Buff("AhaSpdBuff",StatTypes.SPD,self.AHASpdBuff,Role.AHA,[AtkType.SPECIAL],1,1,Role.AHA,TickDown.START))
        if self.tech:
            tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.TECH], [self.element], [0.5, 0], [10, 0], 0,self.scaling, 2, "SparxieTech"))
            self.tech = False
        bl.append(Buff("SparxieATKtoELA", StatTypes.ELA, min(max(floor((self.AtkStat-2000)/100)*0.05, 0), 0.8), self.role, [AtkType.ALL], 1, 1,Role.SELF, TickDown.START))
        bl.append(Buff("SparxiePunchtoCD", StatTypes.CD_PERCENT, min(self.prePunchline * 0.08, 0.8), Role.ALL, [AtkType.ALL],
                 1, 1, self.role, TickDown.START))
        if self.eidolon >= 1:
            bl.append(Buff("SparxiePunchtoPEN", StatTypes.PEN, min(self.prePunchline * 0.015, 0.15), Role.ALL, [AtkType.ALL],
                     1, 1, self.role, TickDown.START))
        return bl, dbl, al, dl, tl, hl

    def addThrill(self, amount: int):
        self.Thrill = min(self.Thrill + amount, 20)