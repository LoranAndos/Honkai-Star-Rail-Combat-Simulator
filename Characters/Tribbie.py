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
    # Relic Settings

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc = None, r1 = None, r2 = None, pl = None, subs = None, eidolon = 6, targetPrio = Priority.BROKEN, rotation = None) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else CruisingInTheStellarSea(self.role)
        self.relic1 = r1 if r1 else ScholarLostInErudition(self.role,4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else RutilantArena(self.role)
        self.relicStats = subs if subs else RelicStats(2, 2, 2, 2, 2, 11, 2, 2, 2, 2, 5, 12, StatTypes.CR_PERCENT, StatTypes.Spd,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["EAA"]

    def equip(self):  # function to add base buffs to wearer
        bl, dbl, al, dl = super().equip()
        bl.append(Buff("TribbieTraceCD", StatTypes.CD_PERCENT, 0.373, self.role))
        bl.append(Buff("TribbieTraceCR", StatTypes.ATK_PERCENT, 0.12, self.role))
        bl.append(Buff("TribbieTraceHP", StatTypes.HP_PERCENT, 0.10, self.role))
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
        bl.append(Buff("Numinosity",StatTypes.PEN,e5ResPen,Role.ALL,[AtkType.ALL],3,1,self.role,TickDown.START  ))
        return bl, dbl, al, dl, tl

    def useUlt(self, enemyID=-1):
        self.currEnergy = self.currEnergy - self.ultCost
        bl, dbl, al, dl, tl = super().useUlt(enemyID)
        e3MultUltimate = 0.33 if self.eidolon >= 5 else 0.3
        e3VulnUltimate = 0.33 if self.eidolon >= 5 else 0.3
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.AOE, [AtkType.ULT], [self.element],
                     [e3MultUltimate], [20], 5, self.scaling, 0, "TribbieUltimate"))
        return bl, dbl, al, dl, tl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl = super().allyTurn(turn, result)
        if result.turnName == "MemBigSkill":
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SINGLE, [AtkType.ULT], [self.element],
                     [0, 0], [0, 0], 10, self.scaling, 0, "MemAttackEnergy"))
        if (turn.charRole == Role.MEMO1 or turn.charRole == Role.MEMO2 or turn.charRole == Role.MEMO3) and not turn.charName == "Mem" and self.CanGetEnergy == True and self.eidolon >= 2:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.SINGLE, [AtkType.ULT], [self.element],
                     [0, 0], [0, 0], 8, self.scaling, 0, "MemAttackEnergy"))
            self.CanGetEnergy = False

        return bl, dbl, al, dl, tl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl = super().ownTurn(turn, result)
        self.CanGetEnergy = True
        return bl, dbl, al, dl, tl

    def takeTurn(self) -> str:
        res = super().takeTurn()
        if self.firstTurn:
            self.firstTurn = False
            return "E"
        return res

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl = super().handleSpecialEnd(specialRes)
        if self.technique:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.AOE, [AtkType.SPECIAL], [self.element],
                     [1, 0], [0, 0], 0, self.scaling, 0, "RmcTechnique"))
            dl.append(Delay("RmcTechnique", 0.5,Role.ALL, False, False))
            self.technique = False
        return bl, dbl, al, dl, tl