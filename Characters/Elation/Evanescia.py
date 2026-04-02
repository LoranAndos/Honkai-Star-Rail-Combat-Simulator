import logging

from Buff import *
from Delay_Text import Advance
from Character import Character
from Lightcones.Elation.ElationBrimmingWithBlessings import ElationBrimmingWithBlessings
from Planars.BrokenKeel import BrokenKeel
from RelicStats import RelicStats
from Relics.EagleOfTwilightLine import EagleOfTwilightLine
from Result import *
from Turn_Text import Turn
from Healing import *
from random import randrange
from math import floor

logger = logging.getLogger(__name__)


class Evanescia(Character):
    # Standard Character Settings
    name = "Evanescia"
    path = Path.ELATION
    element = Element.PHYSICAL
    scaling = Scaling.ATK
    baseHP = 1048
    baseATK = 737
    baseDEF = 461
    baseSPD = 104
    maxEnergy = 480
    currEnergy = 240
    ultCost = 240
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.BRK: 0, AtkType.FUA: 0, AtkType.ELAPUNCH: 0, AtkType.ELABANGER: 0}  # Adjust accordingly

    # Unique Character Properties,
    hasSummon = True
    AHASpdBuffAmount = 0
    TotalElationChar = 0
    ElaStat = 0
    Punch = 0

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, targetRole=Role.DPS, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else ElationBrimmingWithBlessings(role,1)
        self.relic1 = r1 if r1 else EagleOfTwilightLine(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else BrokenKeel(role)
        self.relicStats = subs if subs else RelicStats(13, 4, 0, 4, 4, 0, 3, 3, 3, 3, 0, 11, StatTypes.CR_PERCENT, StatTypes.SPD,
                                                       StatTypes.ATK_PERCENT,StatTypes.ERR_PERCENT)
        self.targetRole = targetRole
        self.rotation = rotation if rotation else ["E"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("BangerStartBattle", StatTypes.BANGER, 20, self.role, [AtkType.ALL], 2, 1, self.role, TickDown.END))
        bl.append(Buff("EvanesciaTraceCR", StatTypes.CR_PERCENT, 0.187, self.role))
        bl.append(Buff("EvanesciaTraceSPD", StatTypes.SPD, 5, self.role))
        bl.append(Buff("EvenesciaTraceELA", StatTypes.ELA, 0.18, self.role))
        bl.append(Buff("EvanesciaTrace1CR",StatTypes.CR_PERCENT,0.30, self.role))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC],[self.element], [e3Mul, 0], [10, 0], 20, self.scaling, 1, "EvanesciaBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)

        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost

        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        if result.turnName == "AhaEvanesciaGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
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
        if result.turnName == "AhaEvanesciaGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
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
        self.savedPunchline = Character.SharedPunchline
        if Character.ahaFixedPunchline:
            Character.SharedPunchline = Character.ahaFixedPunchlineValue  # set to 20 or 40
        #print(f"DEBUG {self.name} useElaSkill | SharedPunchline: {Character.SharedPunchline} | ahaFixedPunchline: {Character.ahaFixedPunchline}")
        if Character.ahaFixedPunchline:
            Character.SharedPunchline = self.savedPunchline
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.AHASpdBuffAmount = specialRes.attr1
        self.TotalElationChar = specialRes.attr2
        self.ElaStat = specialRes.attr3
        self.Punch = specialRes.attr4
        bl.append(Buff("AhaSpdBuff",StatTypes.SPD,self.AHASpdBuffAmount,Role.AHA,[AtkType.SPECIAL],1,1,Role.AHA,TickDown.START))
        return bl, dbl, al, dl, tl, hl
