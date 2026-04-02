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


class ElationMC(Character):
    # Standard Character Settings
    name = "ElationMC"
    path = Path.ELATION
    element = Element.LIGHTNING
    scaling = Scaling.ATK
    baseHP = 1087
    baseATK = 466
    baseDEF = 631
    baseSPD = 106
    maxEnergy = 160
    currEnergy = 80
    ultCost = 160
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.BRK: 0, AtkType.ELAPUNCH: 0, AtkType.ELABANGER: 0}  # Adjust accordingly

    # Unique Character Properties,
    hasSummon = True
    AHASpdBuffAmount = 0
    TotalElationChar = 0
    AtkStat = 0
    TotalSPD = 0
    Banger = 0
    targetHasElaSkill = False
    targetElaSkillTurn = ""
    bangerBonus = 0
    preFiredPunchline = 0

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
        bl.append(Buff("ElationMCTraceCR", StatTypes.CR_PERCENT, 0.12, self.role))
        bl.append(Buff("ElationMCTraceCD", StatTypes.CD_PERCENT, 0.133, self.role))
        bl.append(Buff("ElationMCTraceATK", StatTypes.ATK_PERCENT, 0.28, self.role))
        bl.append(Buff("ElationMCTrace2CR",StatTypes.CR_PERCENT,0.15, self.role))
        ElationMCChance = randrange(1, 100, 1)
        if ElationMCChance >= 21:
            bl.append(Buff("ElationTechELA", StatTypes.ELA, 0.2, Role.ALL, [AtkType.ALL], 3, 1, self.role,TickDown.END))
        else:
            bl.append(Buff("ElationTechELA", StatTypes.ELA, 0.3, Role.ALL, [AtkType.ALL], 3, 1, self.role,TickDown.END))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e5Mul = 1.1 if self.eidolon >= 5 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC],
[self.element],[e5Mul, 0], [10, 0], 20, self.scaling, 1, "ElationMCBasic"))
        bl.append(Buff("ElationMCSkillTalentERR", StatTypes.ERR_F, 10, self.role, [AtkType.ALL], 1, 1, self.role, TickDown.START))
        Character.SharedPunchline += 3
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e3Mul = 0.66 if self.eidolon >= 3 else 0.6
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.SKL],
                       [self.element], [e3Mul, 0], [20, 0], 30, self.scaling, -1, "ElationMCSkill"))
        bl.append(Buff("ElationMCSkillBanger",StatTypes.BANGER,20 + self.bangerBonus ,self.role,[AtkType.ALL],2,5,Role.SELF,TickDown.END))
        Character.SharedPunchline += 3
        bl.append(Buff("ElationMCSkillTalentERR", StatTypes.ERR_F, 10, self.role, [AtkType.ALL], 1, 1, self.role, TickDown.START))
        self.bangerBonus = 0
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        self.preFiredPunchline = self.SharedPunchline  # ← add this before any buffs
        e5Mul = 0.54 if self.eidolon >= 5 else 0.50

        Character.SharedPunchline += 5
        bl.append(Buff("ElationMCUltCD", StatTypes.CD_PERCENT, e5Mul, self.targetRole, [AtkType.ALL], 3, 1, self.role,TickDown.START))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.NA, [AtkType.ULT],[self.element], [0, 0], [0, 0], 5, self.scaling, 1, "ElationMCUlt"))

        # Check if target has Elation Skill
        targetHasElaSkill = self.targetHasElaSkill  # set from handleSpecialStart

        if targetHasElaSkill:
            # Grant 10 Certified Banger to target
            bl.append(Buff("ElationMCUltBanger", StatTypes.BANGER, 10, self.targetRole, [AtkType.ALL], 1, 1, self.role,TickDown.START))

            # Signal fixed 20 Punchline extra turn
            Character.ahaFixedPunchline = True
            Character.ahaFixedPunchlineValue = 20
            # Trigger target's Elation Skill via their GoGo turn
            # This is handled in ownTurn when result.turnName == "ElationMCUlt"
        else:
            # No Elation Skill — advance target by 50%
            al.append(Advance("ElationMCUltAdvance", self.targetRole, 0.50))
        if self.eidolon >= 2:
            bl.append(Buff("ElationMCUltE2ELA", StatTypes.ELA, 0.12, self.targetRole, [AtkType.ALL], 2, 1, self.role, TickDown.END))
        if self.eidolon >= 6:
            bl.append(Buff("ElationMCUltE6SPD", StatTypes.SPD_PERCENT, 0.12, self.targetRole, [AtkType.ALL], 3, 1, self.role, TickDown.END))
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        e3TalMul = 0.33 if self.eidolon >= 3 else 0.3
        if result.turnName == "AhaElationMCGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
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

        if result.turnName in ("ElationMCELASkillBig", "ElationMCELASkillSmall") and self.eidolon >= 1:
            self.bangerBonus = min(self.bangerBonus + 2, 2)
        if turn.moveName == "ElationMCSkill":
            attackerBanger = self.BangerDict.get(turn.charRole, 0)
            ElationMCBanger = self.BangerDict.get(self.role, 0)
            # If attacker has higher ELA, add the difference as a temporary buff on ElationMC
            if attackerBanger > ElationMCBanger:
                bl.append(Buff("ElationMCTalentSkillBanger", StatTypes.BANGER, attackerBanger - ElationMCBanger,
                               self.role, [AtkType.ALL], 1, 1, self.role, TickDown.START))
            if self.Banger >= 1:
                tl.append(Turn(self.name, self.role, self.bestEnemy(-1), Targeting.AOE, [AtkType.ELABANGER],
                               [self.element], [e3TalMul, 0], [0, 0], 0, Scaling.ELA, 0, "ElationMCTalentSkill"))
        if result.turnName == "ElationMCUlt" and result.charRole == self.role:
            if self.targetHasElaSkill:
                tl.append(
                    Turn(self.name, self.targetRole, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                         self.scaling, 0, f"ElationMCUltTrigger_{self.targetRole.name}"))
                # Change from "ElationMCEndGoGo" to "AhaFixedEndGoGo"
                tl.append(
                    Turn(self.name, self.targetRole, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                         self.scaling, 0, "AhaFixedEndGoGo"))
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if result.turnName == "AhaElationMCGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
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
            e5MulBig = 0.66
            e5MulSmall = 0.22
        elif 5 > self.eidolon >= 3:
            e5MulBig = 0.63
            e5MulSmall = 0.21
        else:
            e5MulBig = 0.6
            e5MulSmall = 0.2
        self.savedPunchline = Character.SharedPunchline
        if Character.ahaFixedPunchline:
            Character.SharedPunchline = Character.ahaFixedPunchlineValue  # set to 20 or 40

        #print(f"DEBUG {self.name} useElaSkill | SharedPunchline: {Character.SharedPunchline} | ahaFixedPunchline: {Character.ahaFixedPunchline}")

        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ELAPUNCH],[self.element], [e5MulBig*8, 0], [0, 0], 0, Scaling.ELA, 0, "ElationMCELASkillBig"))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ELAPUNCH],[self.element], [e5MulSmall, 0], [20, 0], 5, Scaling.ELA, 0, "ElationMCELASkillSmall"))
        bl.append(Buff("ElationMCSkillTalentERR", StatTypes.ERR_F, 10, self.role, [AtkType.ALL], 1, 1, self.role, TickDown.START))
        if self.eidolon >= 4:
            dbl.append(Debuff("ElationMCELASkillVul", self.role, StatTypes.VULN, 0.10, Role.ALL, [AtkType.ALL], 2, 1, False, [0, 0], False))
        bl.append(Buff("BangerELASkill", StatTypes.BANGER, self.SharedPunchline , self.role, [AtkType.ALL], 2, 1, self.role,TickDown.END))
        if Character.ahaFixedPunchline:
            Character.SharedPunchline = self.savedPunchline
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.AHASpdBuffAmount = specialRes.attr1
        self.TotalElationChar = specialRes.attr2
        self.AtkStat = specialRes.attr3
        self.TotalSPD = specialRes.attr4
        self.Banger = specialRes.attr5
        self.BangerDict = specialRes.attr6
        self.targetHasElaSkill = specialRes.attr7
        self.targetElaSkillTurn = specialRes.attr8
        bl.append(Buff("AhaSpdBuff",StatTypes.SPD,self.AHASpdBuffAmount,Role.AHA,[AtkType.SPECIAL],1,1,Role.AHA,TickDown.START))
        bl.append(Buff("ElationMCATKtoELA", StatTypes.ELA, min(max(floor((self.AtkStat - 1000) / 200) * 0.10, 0), 0.6),self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        return bl, dbl, al, dl, tl, hl
