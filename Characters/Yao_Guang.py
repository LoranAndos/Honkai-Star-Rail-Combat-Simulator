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
    name = "YaoGuang"
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
    Banger = 0
    elaDict = {}
    SPDStat = 0

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
        self.relicStats = subs if subs else RelicStats(13, 4, 0, 4, 4, 0, 3, 3, 3, 3, 0, 11, StatTypes.CR_PERCENT, StatTypes.Spd,
                                                       StatTypes.ATK_PERCENT,StatTypes.ERR_PERCENT)
        self.rotation = rotation if rotation else ["A","A","E"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        ElationBuff = 0.22 if self.eidolon >=3 else 0.20
        bl.append(Buff("BangerStartBattle", StatTypes.BANGER, 20, self.role, [AtkType.ALL], 2, 1, self.role, TickDown.END))
        bl.append(Buff("YaoGuangTraceCR", StatTypes.CR_PERCENT, 0.187, self.role))
        bl.append(Buff("YaoGuangTraceSPD", StatTypes.Spd, 9, self.role))
        bl.append(Buff("YaoGuangTraceELA", StatTypes.ELA, 0.10, self.role))
        bl.append(Buff("YaoGuangTech", StatTypes.ERR_T, 30, self.role))
        bl.append(Buff("YaoGuangTechElaBuff",StatTypes.ELA,ElationBuff,Role.ALL,[AtkType.ALL],3,1,self.role,TickDown.START))
        bl.append(Buff("YaoGuangTechPunchline", StatTypes.PUNCH, 3, Role.ALL, [AtkType.ALL], 1, 1, self.role,TickDown.START))
        bl.append(Buff("YaoGuangTraceCD",StatTypes.CD_PERCENT,0.60,self.role))
        if self.eidolon >= 1:
            bl.append(Buff("YaoGuangE1SHRED", StatTypes.SHRED, 0.20, Role.ALL, [AtkType.ELAPUNCH], 1, 1,self.role, TickDown.START))
            bl.append(Buff("YaoGuangE1SHRED", StatTypes.SHRED, 0.20, Role.ALL, [AtkType.ELABANGER], 1, 1,self.role, TickDown.START))
        if self.eidolon == 6:
            bl.append(Buff("YaoGuangE6MerryMake", StatTypes.MERRY, 0.25,Role.ALL))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3MulBig = 0.99 if self.eidolon >= 3 else 0.9
        e3MulSmall = 0.33 if self.eidolon >= 3 else 0.3
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.BLAST, [AtkType.BSC],
[self.element],[e3MulBig, e3MulSmall], [10, 5], 30, self.scaling, 1, "YaoGuangBasic"))
        bl.append(Buff("YaoGuangBasicPunchline", StatTypes.PUNCH, 3, Role.ALL, [AtkType.ALL], 1, 1, self.role,TickDown.START))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        #print(f"SKL DEBUG | TotalSP: {self.TotalSP} | Thrill: {self.Thrill} | TotalElationChar: {self.TotalElationChar} | AHASpdBuff: {self.AHASpdBuff:.3f}")
        ElationBuff = 0.22 if self.eidolon >=3 else 0.20
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.NA, [AtkType.SKL],
                       [self.element], [0, 0], [0, 0], 30, self.scaling, -1, "YaoGuangSkill"))
        bl.append(Buff("YaoGuangSkillELABuff",StatTypes.ELA,ElationBuff,Role.ALL,[AtkType.ALL],3,1,self.role,TickDown.START))
        bl.append(Buff("YaoGuangSkillPunchline", StatTypes.PUNCH, 3, Role.ALL, [AtkType.ALL], 1, 1, self.role,TickDown.START))
        if self.eidolon >= 2:
            bl.append(Buff("YaoGuangE2SPDBuff", StatTypes.SPD_PERCENT, 0.12, Role.ALL, [AtkType.ALL], 3, 1, self.role,
                           TickDown.START))
            bl.append(Buff("YaoGuangE2ELABuff", StatTypes.ELA, 0.16, Role.ALL, [AtkType.ALL], 3, 1, self.role,
                           TickDown.START))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        ResPenBuff = 0.22 if self.eidolon >= 5 else 0.2
        bl.append(Buff("YaoGuangUltPunchline", StatTypes.PUNCH, 5, Role.ALL, [AtkType.ALL], 1, 1, self.role, TickDown.START))
        bl.append(Buff("YaoGuangUltResPen", StatTypes.PEN, ResPenBuff, Role.ALL, [AtkType.ALL], 3, 1, self.role,TickDown.START))
        al.append(Advance("YaoGuangUltAhaAdvance", Role.AHA, 1.0))
        Character.ahaFixedPunchline = True
        Character.ahaSkipAVReset = True
        Character.ahaFixedPunchlineValue = 40 if self.eidolon >= 1 else 20
        if self.eidolon >= 4:
            Character.ahaElaDMGBoost = 1.5
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        if result.turnName == "AhaYaoGuangGoGo":
            return self.useElaSkill(-1)
        if result.turnName == "AhaEndGoGo":
            if Character.ahaFixedPunchline:
                self.Punchline = self.savedPunchline + self.TotalElationChar
            Character.ahaFixedPunchline = False
            Character.ahaFixedPunchlineValue = 20
            Character.ahaElaDMGBoost = 1.0
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        e5Mul = 0.22 if self.eidolon >= 5 else 0.2
        if self.Banger >= 1 and (turn.moveName not in bonusDMG) and result.enemiesHit and result.turnDmg > 0:
            attackerELA = self.elaDict.get(turn.charRole, 0)
            yaoGuangELA = self.elaDict.get(self.role, 0)
            # If attacker has higher ELA, add the difference as a temporary buff on YaoGuang
            if attackerELA > yaoGuangELA:
                bl.append(Buff("YaoGuangGreatBoonELA", StatTypes.ELA, attackerELA - yaoGuangELA,
                               self.role, [AtkType.ELABANGER], 1, 1, self.role, TickDown.START))
            if turn.spChange <= -1:
                tl.append(Turn(self.name, self.role, self.bestEnemy(-1), Targeting.SINGLE, [AtkType.ELABANGER],
                               [self.element], [e5Mul * 2, 0], [0, 0], 0, Scaling.ELA, 0, "YaoGuangTalentADDSP"))
            else:
                tl.append(Turn(self.name, self.role, self.bestEnemy(-1), Targeting.SINGLE, [AtkType.ELABANGER],
                               [self.element], [e5Mul, 0], [0, 0], 0, Scaling.ELA, 0, "YaoGuangTalentADD"))
        return bl, dbl, al, dl, tl, hl

    def useElaSkill(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useElaSkill(enemyID)
        if self.eidolon >= 5:
            e5MulBig = 1.1
            e5MulSmall = 0.22
        elif 5 > self.eidolon >= 3:
            e5MulBig = 1.05
            e5MulSmall = 0.21
        else:
            e5MulBig = 1.0
            e5MulSmall = 0.20
        if self.eidolon == 6:
            E6ELASkillIncrease = 2
        else:
            E6ELASkillIncrease = 1

        if Character.ahaFixedPunchline:
            self.savedPunchline = self.Punchline
            self.Punchline = Character.ahaFixedPunchlineValue

        bl.append(Buff("BangerELASkill", StatTypes.PUNCH, self.Punchline, self.role, [AtkType.ALL], 3, 1, self.role,
                       TickDown.END))
        dbl.append(Debuff("YaoGuangELASkillVUL", self.role, StatTypes.VULN, 0.16, Role.ALL, [AtkType.ALL], 3, 1, False, [0, 0],False))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELAPUNCH],
                       [self.element], [e5MulBig*E6ELASkillIncrease*Character.ahaElaDMGBoost, 0], [20, 0], 5, Scaling.ELA, 1, "YaoGuangELASkillAOE"))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ELAPUNCH],
                       [self.element], [e5MulSmall*5*E6ELASkillIncrease*Character.ahaElaDMGBoost, 0], [5*5, 0], 5, Scaling.ELA, 0, "YaoGuangELASkillSINGLE"))
        bl.append(Buff("BangerELASkill", StatTypes.BANGER, self.Punchline , self.role, [AtkType.ALL], 3, 1, self.role,TickDown.END))
        self.Punchline = self.TotalElationChar  # ← consumed then reset to TotalElationChar base
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.AHASpdBuff = specialRes.attr1
        self.TotalElationChar = specialRes.attr2
        self.Banger = specialRes.attr3
        self.elaDict = specialRes.attr4
        self.SPDStat = specialRes.attr5
        bl.append(Buff("AhaSpdBuff", StatTypes.Spd, self.AHASpdBuff, Role.AHA, [AtkType.SPECIAL], 1, 1, Role.AHA,TickDown.START))
        if self.currSPD >= 120:
            ELABuff = min(max((self.SPDStat-120), 0), 2.0)
            bl.append(Buff("YaoGuangTalentELABuff", StatTypes.ELA, 0.30+ELABuff, Role.ALL, [AtkType.ALL], 3, 1, self.role,
                           TickDown.START))
        return bl, dbl, al, dl, tl, hl
