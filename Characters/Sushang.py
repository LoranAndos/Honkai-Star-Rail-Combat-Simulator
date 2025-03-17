import logging

from Lightcones.CruisingInTheStellarSea import CruisingInTheStellarSea
from Relics.ScholarLostInErudition import ScholarLostInErudition
from Planars.RutilantArena import RutilantArena
from Buff import *
from Character import Character
from Delay_Text import *
from RelicStats import RelicStats
from Result import *
from Turn_Text import Turn
from Enemy import *
from Healing import *
from random import randrange

logger = logging.getLogger(__name__)

class Sushang(Character):
    # Standard Character Properties
    name = "Sushang"
    path = Path.HUNT
    element = Element.PHYSICAL
    scaling = Scaling.ATK
    baseHP = 917.3
    baseATK = 564.48
    baseDEF = 418.95
    baseSPD = 107.0
    maxEnergy = 120.0
    ultCost = 120.0
    currEnergy = 60
    currAV = 100.0
    aggro = 75
    rotation = ["E"]
    dmgDct = {AtkType.BSC: 0.0, AtkType.SKL: 0.0, AtkType.ULT: 0.0, AtkType.BRK: 0.0, AtkType.SBK: 0.0}

    # Unique Character Properties
    HasExtraSwordStance = False
    enemyteam = []
    # Relic Settings

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc = None, r1 = None, r2 = None, pl = None, subs = None, eidolon = 6, targetPrio = Priority.BROKEN, rotation = None) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else CruisingInTheStellarSea(self.role)
        self.relic1 = r1 if r1 else ScholarLostInErudition(self.role,4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else RutilantArena(self.role)
        self.relicStats = subs if subs else RelicStats(2, 2, 2, 2, 2, 11, 2, 2, 2, 2, 5, 12, StatTypes.CR_PERCENT, StatTypes.Spd,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["E"]

    def equip(self):  # function to add base buffs to wearer
        bl, dbl, al, dl, hl = super().equip()
        e3Mul = 0.21 if self.eidolon >= 3 else 0.2
        e6Stacks = 2 if self.eidolon == 6 else 1
        bl.append(Buff("SushangTraceATK",StatTypes.ATK_PERCENT,0.28,self.role))
        bl.append(Buff("SushangTraceHP",StatTypes.HP_PERCENT,0.18,self.role))
        bl.append(Buff("SushangTraceDEF",StatTypes.DEF_PERCENT,0.125,self.role))
        if self.eidolon >= 4:
            bl.append(Buff("SushangE4BE", StatTypes.BE_PERCENT, 0.40, self.role))
        if self.eidolon == 6:
            bl.append(Buff("SushangTalent",StatTypes.SPD_PERCENT,e3Mul,self.role,turns = 2,stackLimit = e6Stacks,tdType=TickDown.END))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e5Mul = 1.1 if self.eidolon >= 5 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e5Mul, 0], [10, 0], 20, self.scaling, 1, "SushangBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e5Mul = 2.31 if self.eidolon >= 5 else 2.1
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.SKL], [self.element],
                       [e5Mul, 0], [20, 0], 30, self.scaling, -1, "SushangSkill"))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        self.currEnergy = self.currEnergy - self.ultCost
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        e3Mul = 3.46 if self.eidolon >= 3 else 3.20
        e3Buff = 0.32 if self.eidolon >= 3 else 0.3
        bl.append(Buff("SushangUltimateAttack", StatTypes.ATK_PERCENT, e3Buff, self.role, turns=2, stackLimit=1,
                       tdType=TickDown.END))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ULT], [self.element],
                       [e3Mul, 0], [30, 0], 5, self.scaling, 0, "SushangUltimate"))
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        Once = True
        for enemy in self.enemyteam:
            if enemy.broken == True and result.turnName == ("SushangBasic" or "SushangSkill") and Once == True:
                al.append(Advance("SushangTrace1",self.role,0.15))
                Once = False
        if result.brokenEnemy == True:
            e3Mul = 0.21 if self.eidolon >= 3 else 0.2
            e6Stacks = 2 if self.eidolon == 6 else 1
            bl.append(Buff("SushangTalent",StatTypes.SPD_PERCENT,e3Mul,self.role,turns = 2,stackLimit = e6Stacks,tdType=TickDown.END))
        if enemy.broken == True and result.turnName == "SushangSkill":
            e5Mul = 1.1 if self.eidolon >= 5 else 1
            tl.append(Turn(self.name,self.role,-1,Targeting.NA,[AtkType.SPECIAL],[self.element],[0,0],[0,0],0,self.scaling,1,"Sushange1SP"))
            tl.append(Turn(self.name,self.role,self.bestEnemy(enemyID=-1), Targeting.SINGLE,[AtkType.SKL,AtkType.ADD],[self.element],[e5Mul,0],[0,0],0,self.scaling,0,"SushangSwordStance"))
        if result.turnName == "SushangSkill" and enemy.broken == False:
            SwordStanceChance = randrange(1,100,1)
            e5Mul = 1.1 if self.eidolon >= 5 else 1
            if SwordStanceChance > 67:
                tl.append(Turn(self.name,self.role,self.bestEnemy(enemyID=-1), Targeting.SINGLE,[AtkType.SKL,AtkType.ADD],[self.element],[e5Mul,0],[0,0],0,self.scaling,0,"SushangSwordStance"))
        if enemy.broken == True and self.HasExtraSwordStance == True and result.turnName == "SushangSkill":
            tl.append( Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SINGLE, [AtkType.SKL,AtkType.ADD], [self.element],
                     [e5Mul/2, 0], [0, 0], 0, self.scaling, 0, "SushangSwordStanceExtra"))
            tl.append( Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SINGLE, [AtkType.SKL,AtkType.ADD], [self.element],
                     [e5Mul/2, 0], [0, 0], 0, self.scaling, 0, "SushangSwordStanceExtra"))
        if result.turnName == "SushangSkill" and enemy.broken == False:
            for i in range(1,3):
                SwordStanceChance = randrange(1, 100, 1)
                e5Mul = 1.1 if self.eidolon >= 5 else 1
                if SwordStanceChance > 67:
                    tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1),Targeting.SINGLE, [AtkType.SKL,AtkType.ADD],[self.element], [e5Mul/2, 0], [0, 0], 0, self.scaling, 0, "SushangSwordStance"))
        if result.turnName == "SushangSwordStance" or result.turnName == "SushangSwordStanceExtra":
            bl.append(Buff("SushangTrace2",StatTypes.DMG_PERCENT,0.02,self.role,[AtkType.ALL],1,10,Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if result.brokenEnemy == True:
            e3Mul = 0.21 if self.eidolon >= 3 else 0.2
            e6Stacks = 2 if self.eidolon == 6 else 1
            bl.append(Buff("SushangTalent",StatTypes.SPD_PERCENT,e3Mul,self.role,turns = 2,stackLimit = e6Stacks,tdType=TickDown.END))
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        if specialRes.attr1 == True:
            self.HasExtraSwordStance = True
        self.enemyteam = specialRes.attr2
        return super().handleSpecialEnd(specialRes)