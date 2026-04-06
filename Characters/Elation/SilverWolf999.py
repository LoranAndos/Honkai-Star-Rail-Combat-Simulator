import logging

from Buff import *
from Delay_Text import Advance
from Character import Character
from Lightcones.Elation.WelcomeToTheCosmicCity import WelcometotheCosmicCity
from Lightcones.Elation.MushyShroomyAdventures import MushyShroomysAdventures
from Planars.PunklordeStageZero import PunklordeStageZero
from RelicStats import RelicStats
from Relics.EverGloriousMagicalGirl import EverGloriousMagicalGirl
from Result import *
from Turn_Text import Turn
from Healing import *
from random import randrange
from math import floor

logger = logging.getLogger(__name__)


class SilverWolf999(Character):
    # Standard Character Settings
    name = "SilverWolf999"
    path = Path.ELATION
    element = Element.IMAGINARY
    scaling = Scaling.ATK
    baseHP = 1048
    baseATK = 388
    baseDEF = 655
    baseSPD = 110
    maxEnergy = 300
    currEnergy = 0
    ultCost = 60
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0,AtkType.BRK: 0, AtkType.ELAPUNCH: 0, AtkType.ELABANGER: 0}

    # Unique Character Properties
    hasSummon = True
    specialEnergy = True
    AHASpdBuffAmount = 0
    TotalElationChar = 0
    ElaStat = 0
    Punch = 0
    SpdStat = 0
    WolfInstants = 0
    LootBoxChance = 1.00

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, targetRole=Role.DPS, rotation=None, targetPrio=Priority.DEFAULT,
                 elationParticipationID=999) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else WelcometotheCosmicCity(role, 1)
        self.relic1 = r1 if r1 else EverGloriousMagicalGirl(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else PunklordeStageZero(role)
        self.relicStats = subs if subs else RelicStats(5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 13, 10, StatTypes.CD_PERCENT,
                                                       StatTypes.SPD,StatTypes.ATK_PERCENT, StatTypes.ERR_PERCENT)
        self.targetRole = targetRole
        self.rotation = rotation if rotation else ["E"]
        self.elationParticipationID = elationParticipationID

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("BangerStartBattle", StatTypes.BANGER, 20, self.role, [AtkType.ALL], 2, 1, self.role, TickDown.END))
        bl.append(Buff("SilverWolf999TraceCR", StatTypes.CR_PERCENT, 0.187, self.role))
        bl.append(Buff("SilwerWolf999TraceSPD", StatTypes.SPD, 9, self.role))
        bl.append(Buff("SilverWolf999TraceELA", StatTypes.ELA, 0.10, self.role))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        if self.WolfInstants == 0:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                           Targeting.SINGLE, [AtkType.BSC], [self.element],
                           [e3Mul, 0], [10, 0], 0, self.scaling, 1, "SilverWolf999Basic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e3Mul = 1.76 if self.eidolon >= 3 else 1.6
        Character.SharedPunchline += 5
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                       Targeting.AOE, [AtkType.SKL], [self.element],
                       [e3Mul, 0], [10, 0], 0, self.scaling, -1, "SilverWolf999Skill"))
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost + 20

        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        if result.turnName == "AhaSilverWolf999GoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        # Fixed Aha turns - reset flags but NOT punchline
        if result.turnName == "AhaFixedEndGoGo":
            Character.ahaFixedPunchline = False
            Character.ahaFixedPunchlineValue = 20
            Character.ahaElaDMGBoost = 1.0

        # Normal Aha sequence end - reset punchline
        if result.turnName == "AhaElationSequenceComplete":
            Character.SharedPunchline = 3
            Character.ahaFixedPunchline = False

        if result.turnName == "AhaEndGoGo":
            Character.ahaFixedPunchline = False
            Character.ahaFixedPunchlineValue = 20
            Character.ahaElaDMGBoost = 1.0

        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if result.turnName == "AhaSilverWolf999GoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        # Fixed Aha turns - reset flags but NOT punchline
        if result.turnName == "AhaFixedEndGoGo":
            Character.ahaFixedPunchline = False
            Character.ahaFixedPunchlineValue = 20
            Character.ahaElaDMGBoost = 1.0

        # Normal Aha sequence end - reset punchline
        if result.turnName == "AhaElationSequenceComplete":
            Character.SharedPunchline = 3
            Character.ahaFixedPunchline = False

        if result.turnName == "AhaEndGoGo":
            Character.ahaFixedPunchline = False
            Character.ahaFixedPunchlineValue = 20
            Character.ahaElaDMGBoost = 1.0

        return bl, dbl, al, dl, tl, hl

    def useElaSkill(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useElaSkill(enemyID)
        if self.eidolon >= 5:
            e5Mul = 0.99
        elif 5 > self.eidolon >= 3:
            e5Mul = 0.945
        else:
            e5Mul = 0.9
        self.savedPunchline = Character.SharedPunchline
        if Character.ahaFixedPunchline:
            Character.SharedPunchline = Character.ahaFixedPunchlineValue  # set to 20 or 40
            self.currEnergy += Character.ahaFixedPunchlineValue
        if self.WolfInstants == 0:
            self.currEnergy += 15
        else:
            self.LootBoxChance = 1.00
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                           Targeting.SINGLE, [AtkType.ELAPUNCH], [self.element],
                           [e5Mul, 0], [5, 0], 0, Scaling.ELA, -1, "SilverWolf999ELASkill"))
            for i in range(1,5,1):
                tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID),
                           Targeting.SINGLE, [AtkType.ELAPUNCH], [self.element],
                           [e5Mul, 0], [5, 0], 0, Scaling.ELA, -1, "SilverWolf999ELASkillExtra"))
        bl.append(Buff("BangerELASkill", StatTypes.BANGER, self.SharedPunchline, self.role, [AtkType.ALL], 2, 1, self.role,TickDown.END))
        if Character.ahaFixedPunchline:
            Character.SharedPunchline = self.savedPunchline
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.AHASpdBuffAmount = specialRes.attr1
        self.TotalElationChar = specialRes.attr2
        self.ElaStat = specialRes.attr3
        self.Punch = specialRes.attr4
        self.SpdStat = specialRes.attr5
        bl.append(Buff("AhaSpdBuff", StatTypes.SPD, self.AHASpdBuffAmount, Role.AHA, [AtkType.SPECIAL], 1, 1, Role.AHA,
                       TickDown.START))
        if self.currSPD >= 150:
            ELABuff = min(max((self.SpdStat-150), 0), 100)
            bl.append(Buff("YaoGuangTalentELABuff", StatTypes.ELA, 0.30+ELABuff*0.02, self.role  , [AtkType.ALL], 1, 1, self.role,TickDown.START))

        return bl, dbl, al, dl, tl, hl

    def takeTurn(self) -> str:
        return "A" if self.WolfInstants else "E"

    def canUseUlt(self) -> bool:
        return super().canUseUlt() if not self.WolfInstants else False