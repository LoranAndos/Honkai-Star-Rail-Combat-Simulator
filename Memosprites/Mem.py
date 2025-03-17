import logging

from Characters import Rmc
from Lightcones.CruisingInTheStellarSea import CruisingInTheStellarSea
from Relics.ScholarLostInErudition import ScholarLostInErudition
from Planars.RutilantArena import RutilantArena
from MainFunctions import getBaseValue, getCharSPD
from Buff import *
from Memosprite import Memosprite
from Character import *
from Delay_Text import *
from RelicStats import RelicStats
from Result import *
from Turn_Text import Turn
from Enemy import *
from Healing import *
from random import randrange

logger = logging.getLogger(__name__)

class Mem(Memosprite):
    # Standard Character Properties
    name = "Mem"
    element = Element.ICE
    scaling = Scaling.ATK
    MemoSummoner = Rmc
    lightcone = CruisingInTheStellarSea
    baseHP = 0.86*1047.8 #if eidolon 3 or lower: 0.8*1047.8 else 0.86*1047.8
    baseATK = 543.31 + lightcone.baseATK
    baseDEF = 630.63 + lightcone.baseDEF
    baseSPD = 1
    maxEnergy = 100
    EnergyCost = 100
    currEnergy = maxEnergy / 2 + 40
    currAV = 100.0
    aggro = 100
    MemoActive = False
    rotation = ["MEMO"]
    dmgDct = {AtkType.MEMO: 0.0,AtkType.SPECIAL: 0.0 ,AtkType.BRK: 0.0}

    # Unique Character Properties
    specialEnergy = True
    firstTurn = True
    Rmc_Bufflist = []
    MemSpawn = False
    HitEnergy = 0
    cdStat = 0
    MemospriteSupport = False
    DpsEnergy = 0
    hasMemosprite = False
    SpecialEnergyCharacter = []
    ExtraTrueDamage = False
    firstSkill = True

    # Relic Settings

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc = None, r1 = None, r2 = None, pl = None, subs = None, MemTarget = None, eidolon = 6, targetPrio = Priority.BROKEN, rotation = None) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else CruisingInTheStellarSea(self.role)
        self.relic1 = r1 if r1 else ScholarLostInErudition(self.role,4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else RutilantArena(self.role)
        self.relicStats = subs if subs else RelicStats(0, 2, 2, 2, 2, 11, 2, 2, 2, 2, 5, 12, StatTypes.CR_PERCENT, StatTypes.ERR_PERCENT,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.MemTarget = MemTarget if MemTarget else Role.DPS
        self.rotation = rotation if rotation else ["MEMO"]

    def equip(self):  # function to add base buffs to wearer
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("RmcTraceCD", StatTypes.CD_PERCENT, 0.373, self.role))
        bl.append(Buff("RmcTraceATK", StatTypes.ATK_PERCENT, 0.14, self.role))
        bl.append(Buff("RmcTraceHP", StatTypes.HP_PERCENT, 0.14, self.role))
        return bl, dbl, al, dl, hl

    def useMemo(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useMemo(enemyID)
        if self.MemoActive:
            if self.eidolon < 5:
                SmallMultiplier = 0.36
                BigMultiplier = 0.9
            else:
                SmallMultiplier = 0.396
                BigMultiplier = 0.99
            if not self.MemospriteSupport:
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SINGLE, [AtkType.MEMO], [self.element],
                         [SmallMultiplier, 0], [5, 0], 0, self.scaling, 0, "MemSkill"))
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SINGLE, [AtkType.MEMO], [self.element],
                         [SmallMultiplier, 0], [5, 0], 0, self.scaling, 0, "MemSkill"))
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SINGLE, [AtkType.MEMO], [self.element],
                         [SmallMultiplier, 0], [5, 0], 0, self.scaling, 0, "MemSkill"))
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SINGLE, [AtkType.MEMO], [self.element],
                         [SmallMultiplier, 0], [5, 0], 0, self.scaling, 0, "MemSkill"))
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.AOE, [AtkType.MEMO], [self.element],
                         [BigMultiplier, 0], [10, 0], 5, self.scaling, 0, "MemBigSkill"))
            else:
                if self.eidolon < 5:
                    TrueDamageBuff = 0.28 + min(0.2,(self.DpsEnergy-100)/10*2/100)
                else:
                    TrueDamageBuff = 0.30 + min(0.2,(self.DpsEnergy-100)/10*2/100)
                if self.ExtraTrueDamage == True and self.eidolon == 4:
                    TrueDamageBuff = 0.28 + 0.06
                elif self.ExtraTrueDamage == True and self.eidolon > 5:
                    TrueDamageBuff = 0.30 + 0.06
                bl.append(Buff("MemSupport",StatTypes.TRUEDAMAGE,TrueDamageBuff,self.MemTarget,[AtkType.ALL],3,1,tickDown=self.MemTarget,tdType=TickDown.START))
                al.append(Advance("MemSupportAdvance",self.MemTarget,1))
                if self.eidolon >= 1:
                    bl.append(Buff("MemCRSupport",StatTypes.CR_PERCENT,0.1,self.MemTarget,[AtkType.ALL],3,1,tickDown=self.MemTarget,tdType=TickDown.START))
                if self.hasMemosprite == True:
                    bl.append(Buff("MemSupport",StatTypes.TRUEDAMAGE,TrueDamageBuff,Role.MEMO1,[AtkType.ALL],3,1,tickDown=Role.MEMO1,tdType=TickDown.START))
                    if self.eidolon >= 1:
                        bl.append(Buff("MemCRSupport", StatTypes.CR_PERCENT, 0.1,Role.MEMO1, [AtkType.ALL], 3, 1,tickDown=Role.MEMO1, tdType=TickDown.START))
                self.MemospriteSupport = False
        return bl, dbl, al, dl, tl, hl
    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        if self.MemoActive:
            self.currEnergy = self.currEnergy - self.EnergyCost
            al.append(Advance("MemUltAdvance",self.role,1))
            self.MemospriteSupport = True
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        if self.MemoActive:
            if self.eidolon < 3:
                CdMultiplier = self.cdStat*0.12+0.24
            else:
                CdMultiplier = self.cdStat*0.132+0.264
            if result.errGain > 0 and not result.charName in self.SpecialEnergyCharacter and turn.moveName != "MemUltimateEnergy":
                energy = result.errGain/10
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SPECIAL, [AtkType.SPECIAL], [self.element],
                         [0, 0], [0, 0], energy, self.scaling, 0, "MemUltimateEnergy"))
            bl.append(Buff("MemCdBuff",StatTypes.CD_PERCENT,CdMultiplier,Role.ALL,[AtkType.ALL],1,1,self.role,TickDown.START))
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if result.turnName == "MemSpawn" and self.firstSkill == True:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SINGLE, [AtkType.SPECIAL], [self.element],
                     [0, 0], [0, 0], 10, self.scaling, 0, "RmcSkillEnergy"))
            self.MemSpawn = True
            self.MemoActive = True
            self.firstSkill = False
            self.baseSPD = 130
            self.currAV = 10000/self.currSPD
        elif result.turnName == "MemSpawn" and self.firstSkill == False:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SINGLE, [AtkType.SPECIAL],[self.element],
                           [0, 0], [0, 0], 10, self.scaling, 0, "RmcSkillEnergy"))
        if self.MemoActive:
            if result.turnName == "RmcUltimate" and result.charName == "Remembrance Trailblazer":
                if self.eidolon == 6:
                    bl.append(Buff("MemCRult", StatTypes.CR_PERCENT, 1,self.role, [AtkType.ALL], 1, 1,tickDown=self.role, tdType=TickDown.START))
                e5Mul = 2.64 if self.eidolon >= 5 else 2.4
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.AOE, [AtkType.MEMO], [self.element],
                         [e5Mul, 0], [20, 0], 40, self.scaling, 0, "MemUltimate"))
                if self.eidolon == 6:
                    bl.append(Buff("MemCRremove", StatTypes.CR_PERCENT, -1,self.role, [AtkType.ALL], 1, 1,tickDown=self.role, tdType=TickDown.START))
            if result.errGain > 0 and not (result.charName in self.SpecialEnergyCharacter) and (turn.moveName != "MemUltimateEnergy"):
                energy = result.errGain/10
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SPECIAL, [AtkType.SPECIAL], [self.element],
                         [0, 0], [0, 0], energy, self.scaling, 0, "MemUltimateEnergy"))
            if turn.charName in self.SpecialEnergyCharacter and (turn.atkType == AtkType.BSC or turn.atkType == AtkType.SKL or turn.atkType == AtkType.ULT) and not AtkType.ADD and self.eidolon >= 4:
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SINGLE, [AtkType.SPECIAL], [self.element],
                         [0, 0], [0, 0], 3, self.scaling, 0, "MemE4Energy"))
                self.ExtraTrueDamage = True
        return bl, dbl, al, dl, tl, hl

    def takeTurn(self) -> str:
        res = super().takeTurn()
        if self.firstTurn:
            self.firstTurn = False
            return "MEMO"
        return res

    def useHit(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useHit(enemyID)
        if self.MemoActive:
            energy = self.HitEnergy
            tl.append(Turn("Remembrance Trailblazer", Role.SUP1, self.bestEnemy(enemyID=-1), Targeting.SPECIAL, [AtkType.SPECIAL], [self.element],
                     [0, 0], [0, 0], energy, self.scaling, 0, "HitEnergyToRmc"))
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialEnd(specialRes)
        self.Rmc_Bufflist = specialRes.attr1
        if self.MemSpawn:
            for buff in self.Rmc_Bufflist:
                bl.append(Buff(buff.name, buff.buffType,buff.val,target=self.role,tickDown=self.role,turns=buff.turns,tdType=TickDown.END))
            self.MemSpawn = False
        self.HitEnergy = specialRes.attr2
        self.cdStat = specialRes.attr3
        self.DpsEnergy = specialRes.attr4
        self.hasMemosprite = specialRes.attr5
        self.SpecialEnergyCharacter = specialRes.attr6
        return bl, dbl, al, dl, tl, hl