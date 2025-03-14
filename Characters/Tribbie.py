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

logger = logging.getLogger(__name__)

class Tribbie(Character):
    # Standard Character Properties
    name = "Tribbie"
    path = Path.HARMONY
    element = Element.QUANTUM
    scaling = Scaling.HP
    baseHP = 1047.8
    baseATK = 523.91
    baseDEF = 727.65
    baseSPD = 96
    maxEnergy = 120.0
    ultCost = 120.0
    currEnergy = 60
    currAV = 100.0
    aggro = 100
    dmgDct = {AtkType.BSC: 0.0 ,AtkType.FUA: 0.0 ,AtkType.ULT: 0.0 ,AtkType.ADD: 0.0 ,AtkType.BRK: 0.0, AtkType.SBK: 0.0}

    # Unique Character Properties
    CharacterList = []
    TeamHp = 0
    # Relic Settings

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc = None, r1 = None, r2 = None, pl = None, subs = None, eidolon = 6, targetPrio = Priority.BROKEN, rotation = None) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else CruisingInTheStellarSea(self.role)
        self.relic1 = r1 if r1 else ScholarLostInErudition(self.role,4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else RutilantArena(self.role)
        self.relicStats = subs if subs else RelicStats(2, 2, 2, 2, 2, 11, 2, 2, 2, 2, 5, 12, StatTypes.CR_PERCENT, StatTypes.Spd,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["A","A","E"]

    def equip(self):  # function to add base buffs to wearer
        bl, dbl, al, dl = super().equip()
        e5ResPen = 0.264 if self.eidolon >= 5 else 0.24
        bl.append(Buff("TribbieTraceCD", StatTypes.CD_PERCENT, 0.373, self.role))
        bl.append(Buff("TribbieTraceCR", StatTypes.ATK_PERCENT, 0.12, self.role))
        bl.append(Buff("TribbieTraceHP", StatTypes.HP_PERCENT, 0.10, self.role))
        bl.append(Buff("TribbieTechniqueBuff", StatTypes.ERR_T, 30, self.role))
        bl.append(Buff("Numinosity", StatTypes.PEN, e5ResPen, Role.ALL, [AtkType.ALL], 3, 1, self.role, TickDown.START))
        if self.eidolon >= 6:
            bl.append(Buff("TribbieE6FuaDamageBoost", StatTypes.DMG_PERCENT, 7.29, self.role, [AtkType.FUA],1,1,Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl = super().useBsc(enemyID)
        e3MultBasic = 0.33 if self.eidolon >= 5 else 0.3
        e3MultBasic2 = 0.165 if self.eidolon >= 5 else 0.15
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.BLAST, [AtkType.BSC], [self.element],
                       [e3MultBasic, e3MultBasic2], [10, 5], 20, self.scaling, 1, "TribbieBasic"))
        return bl, dbl, al, dl, tl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl = super().useSkl(enemyID)
        e5ResPen = 0.264 if self.eidolon >= 5 else 0.24
        bl.append(Buff("Numinosity",StatTypes.PEN,e5ResPen,Role.ALL,[AtkType.ALL],3,1,self.role,TickDown.START))
        if self.eidolon >= 4:
            bl.append(Buff("TribbieE4DefShred",StatTypes.SHRED,0.18,Role.ALL,[AtkType.ALL],3,1,self.role,TickDown.START))
        return bl, dbl, al, dl, tl

    def useUlt(self, enemyID=-1):
        self.currEnergy = self.currEnergy - self.ultCost
        bl, dbl, al, dl, tl = super().useUlt(enemyID)
        e3MultUltimate = 0.33 if self.eidolon >= 5 else 0.3
        e3VulnUltimate = 0.33 if self.eidolon >= 5 else 0.3
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.AOE, [AtkType.ULT], [self.element],
                     [e3MultUltimate], [20,0], 5, self.scaling, 0, "TribbieUltimate"))
        bl.append(Buff("TribbieUltVuln",StatTypes.VULN,e3VulnUltimate,Role.ALL,[AtkType.ALL],3,1,self.role,TickDown.START))
        if self.eidolon >= 1:
            bl.append(Buff("TribbieTrueDmg",StatTypes.TRUEDAMAGE,0.24,Role.ALL,[AtkType.ALL],3,1,self.role,TickDown.START))
            # Change target to enemy with highest hp once hp for enemies and them taking damage has been coded
        return bl, dbl, al, dl, tl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl = super().allyTurn(turn, result)
        e3AdditionalMulti = 0.132 if self.eidolon >= 3 else 0.12
        e5TalentFua = 0.198 if self.eidolon >= 3 else 0.18

        if (turn.moveName not in bonusDMG) and result.enemiesHit and self.eidolon < 2 and result.turnDmg > 0:
            tl.append(Turn(self.name,self.role, self.bestEnemy(enemyID=-1),Targeting.SINGLE,[AtkType.ADD],[self.element],
                           [e3AdditionalMulti*len(result.enemiesHit),0],[0,0],0,self.scaling,0,"TribbieAdditionalDamage"))
            #Change target to enemy with highest hp once hp for enemies and them taking damage has been coded
            bl.append(Buff("TribbieTrace1Energy", StatTypes.ERR_T, 1.5*len(result.enemiesHit), self.role))

        if (turn.moveName not in bonusDMG) and result.enemiesHit and self.eidolon >= 2 and result.turnDmg > 0:
            tl.append(Turn(self.name,self.role, self.bestEnemy(enemyID=-1),Targeting.SINGLE,[AtkType.ADD],[self.element],
                           [e3AdditionalMulti*(len(result.enemiesHit)+1)*1.2,0],[0,0],0,self.scaling,0,"TribbieAdditionalDamage"))
            #Change target to enemy with highest hp once hp for enemies and them taking damage has been coded
            bl.append(Buff("TribbieTrace1Energy", StatTypes.ERR_T, 1.5*len(result.enemiesHit), self.role))

        if result.atkType == AtkType.ULT and (turn.moveName not in bonusDMG) and result.charName in self.CharacterList:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.AOE, [AtkType.FUA], [self.element],
                     [e5TalentFua], [5, 0], 5, self.scaling, 0,"TribbieTalentFua"))
            bl.append("TribbieTrace3Dmg",StatTypes.DMG_PERCENT,0.72,self.role,[AtkType.ALL],3,3,self.role,TickDown.START)
            self.CharacterList.remove(result.charName)

        return bl, dbl, al, dl, tl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl = super().ownTurn(turn, result)
        e3AdditionalMulti = 0.132 if self.eidolon >= 3 else 0.12
        e5TalentFua = 0.198 if self.eidolon >= 3 else 0.18
        if (turn.moveName not in bonusDMG) and result.enemiesHit and self.eidolon < 2 and result.turnDmg > 0:
            tl.append(
                Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SINGLE, [AtkType.ADD], [self.element],
                     [e3AdditionalMulti * len(result.enemiesHit),0], [0, 0], 0, self.scaling, 0,
                     "TribbieAdditionalDamage"))
            # Change target to enemy with highest hp once hp for enemies and them taking damage has been coded
            bl.append(Buff("TribbieTrace1Energy", StatTypes.ERR_T, 1.5 * len(result.enemiesHit), self.role))

        if (turn.moveName not in bonusDMG) and result.enemiesHit and self.eidolon >= 2 and result.turnDmg > 0:
            tl.append(Turn(self.name,self.role, self.bestEnemy(enemyID=-1),Targeting.SINGLE,[AtkType.ADD],[self.element],
                           [e3AdditionalMulti*(len(result.enemiesHit)+1)*1.2,0],[0,0],0,self.scaling,0,"TribbieAdditionalDamage"))
            #Change target to enemy with highest hp once hp for enemies and them taking damage has been coded
            bl.append(Buff("TribbieTrace1Energy", StatTypes.ERR_T, 1.5*len(result.enemiesHit), self.role))

        if result.atkType == AtkType.ULT and (turn.moveName not in bonusDMG) and result.charName in self.CharacterList and self.eidolon >= 6:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.AOE, [AtkType.FUA], [self.element],
                     [e5TalentFua], [5, 0], 5, self.scaling, 0,"TribbieTalentFua"))
            self.CharacterList.remove(result.charName)
            bl.append("TribbieTrace3Dmg", StatTypes.DMG_PERCENT, 0.72, self.role, [AtkType.ALL], 3, 3, self.role,TickDown.START)
        bl.append(Buff("TribbieTrace2HP",StatTypes.HP,0.09*self.TeamHp,self.role,[AtkType.ALL],1,1,self.role,TickDown.START))
        return bl, dbl, al, dl, tl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl = super().handleSpecialEnd(specialRes)
        self.CharacterList = specialRes.attr1
        self.TeamHp = specialRes.attr2
        return bl, dbl, al, dl, tl