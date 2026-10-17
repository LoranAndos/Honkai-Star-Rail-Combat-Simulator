import logging

from Buff import *
from Character import Character
from Lightcones.Elation.DazzledByAFloweryWorld import DazzledByAFloweryWorld
from Lightcones.Elation.MushyShroomyAdventures import MushyShroomysAdventuresSparxie
from Planars.TengokuLivestream import TengokuLivestream
from RelicStats import RelicStats
from Relics.EverGloriousMagicalGirl import EverGloriousMagicalGirl
from Result import *
from Turn_Text import Turn
from Healing import *
from Delay_Text import Advance
from random import random
from math import floor

logger = logging.getLogger(__name__)


class AeonAha(Character):
    # Standard Character Settings
    name = "AeonAha"
    path = Path.ELATION
    element = Element.QUANTUM
    scaling = Scaling.ELA
    baseHP = 1048
    baseATK = 679
    baseDEF = 509
    baseSPD = 94
    maxEnergy = 10
    currEnergy = 0
    ultCost = 8
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.ELAPUNCH: 0, AtkType.ELABANGER: 0}  # Adjust accordingly

    # Unique Character Properties
    hasSummon = True
    specialEnergy = True
    AHASpdBuffAmount = 0
    TotalElationChar = 0
    Wishpower = 0
    UltActive = False
    UltTurns = 0
    TalentWishpowerTrigger = True

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, targetRole=Role.DPS, rotation=None, targetPrio=Priority.DEFAULT,
                 elationParticipationID=0) -> None:  # AeonAha ID: 0
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else MushyShroomysAdventuresSparxie(role,5)
        self.relic1 = r1 if r1 else EverGloriousMagicalGirl(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else TengokuLivestream(role)
        self.relicStats = subs if subs else RelicStats(6, 2, 2, 2, 2, 8, 2, 2, 2, 2, 9, 9, StatTypes.CR_PERCENT, StatTypes.SPD, StatTypes.ATK_PERCENT, StatTypes.ERR_PERCENT)
        self.targetRole = targetRole
        self.rotation = rotation if rotation else ["E"]
        self.elationParticipationID = elationParticipationID

    def addEnergy(self, amount: float):

        if not self.UltActive:
            space = self.maxEnergy - self.currEnergy
            if amount > space:
                # Fill currEnergy to max, put the remainder into overflow
                self.currEnergy = self.maxEnergy
                self.overflowEnergy = min(80.0, self.overflowEnergy + (amount - space))
            else:
                self.currEnergy = min(self.maxEnergy, self.currEnergy + amount)
        else:
            self.currEnergy = min(self.maxEnergy, self.currEnergy + amount)

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("BangerStartBattle", StatTypes.BANGER, 20, self.role, [AtkType.ALL], 2, 1, self.role, TickDown.END))
        bl.append(Buff("AeonAhaTraceCR", StatTypes.CR_PERCENT, 0.12, self.role))
        bl.append(Buff("AeonAhaTraceSPD", StatTypes.SPD, 5, self.role))
        bl.append(Buff("AeonAhaTraceCD", StatTypes.ELA, 0.373, self.role))
        return bl, dbl, al, dl, hl, sl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useBsc(enemyID)
        e3Mul = 0.55 if self.eidolon >= 3 else 0.50
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC,AtkType.ELABANGER],
[self.element],[e3Mul, 0], [10, 0], 0, self.scaling, 1, "AeonAhaBasic"))
        self.Wishpower += 1
        return bl, dbl, al, dl, tl, hl, sl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useSkl(enemyID)
        e5Mul = 0.55 if self.eidolon >= 5 else 0.50
        e5ELABuff = 0.22 if self.eidolon >= 5 else 0.20
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.FUA, AtkType.ELABANGER],
                 [self.element], [e5Mul, 0], [10, 0], 0, self.scaling, -1, "AeonAhaSkill"))
        bl.append(Buff("AhaSkillELA", StatTypes.ELA, e5ELABuff, self.targetRole, [AtkType.ALL], 1, 1, self.targetRole, TickDown.PERM))
        self.Wishpower += 1
        return bl, dbl, al, dl, tl, hl, sl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e3MulBig = 2.16 if self.eidolon >= 3 else 2.00
        e3MulSmall = 0.648 if self.eidolon >= 3 else 0.60
        al.append(Advance("AhaADV", Role.AHA, 0.20))
        self.UltActive = True
        self.UltTurns = 3
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT, AtkType.ELABANGER],
                 [self.element], [e3MulBig, 0], [20, 0], 0, self.scaling, 0, "AeonAhaUlt"))
        for _ in range(5):
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ULT, AtkType.ELABANGER],
                     [self.element], [e3MulSmall, 0], [5, 0], 0, self.scaling, 0, "AeonAhaUltExtra"))
        return bl, dbl, al, dl, tl, hl, sl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().ownTurn(turn, result)
        e5CDBuff = 0.44 if self.eidolon >= 5 else 0.40
        if result.turnName == "AhaGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        pearl = next((c for c in (Character._current_player_team or []) if c.name == "Pearl"), None)
        if result.turnName == "AeonAhaSkill" and Character.PearlUlt == True and pearl is not None and self.role == pearl.targetRole:
            bl.append(Buff("PearlAestheticArchetypeBanger", StatTypes.BANGER, 0, self.role,
                           [AtkType.ALL], 2, 1, self.role, TickDown.PERM))
            Character.SharedPunchline -= 60 * Character.PearlE2Modifier
            Character.PearlUlt = False

        if Character.SharedPunchline >= 40 and self.TalentWishpowerTrigger:
            self.Wishpower += 1
            self.TalentWishpowerTrigger = False
            bl.append(Buff("AhaTalentCD", StatTypes.CD_PERCENT, e5CDBuff, Role.ALL, [AtkType.ALL], 3, 1, self.role, TickDown.END))

        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)
        e5CDBuff = 0.44 if self.eidolon >= 5 else 0.40

        if result.turnName == "AhaGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        pearl = next((c for c in (Character._current_player_team or []) if c.name == "Pearl"), None)
        if result.turnName == "PearlUltimate" and Character.PearlUlt == True and pearl is not None and self.role == pearl.targetRole:
            bl.append(Buff("PearlAestheticArchetypeBanger", StatTypes.BANGER, 30 * Character.PearlE2Modifier, self.role,
                           [AtkType.ALL], 2, 1, self.role, TickDown.PERM))
            Character.SharedPunchline += 60 * Character.PearlE2Modifier

            bl, dbl, al, dl, tl, hl, sl = self.extendLists(bl, dbl, al, dl, tl, hl, sl, *self.useSkl(-1))

        if turn.moveName == "AhaElationSequenceComplete":
            self.TalentWishpowerTrigger = True

        if Character.SharedPunchline >= 40 and self.TalentWishpowerTrigger and Character.PearlUlt == False:
            self.Wishpower += 1
            self.TalentWishpowerTrigger = False
            bl.append(Buff("AhaTalentCD", StatTypes.CD_PERCENT, e5CDBuff, Role.ALL, [AtkType.ALL], 3, 1, self.role, TickDown.END))


        return bl, dbl, al, dl, tl, hl, sl

    def _onTargetTurnBegins_Wishpower(self):
        self.Wishpower += 1
        logger.info(f"WISHPOWER > {self.name} gained 1 Wishpower from {self.targetRole.name}'s turn beginning "
                   f"(total: {self.Wishpower})")

    def useElaSkill(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useElaSkill(enemyID)
        self.Wishpower += 1
        return bl, dbl, al, dl, tl, hl, sl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)
        self.AHASpdBuffAmount = specialRes.attr1
        self.TotalElationChar = specialRes.attr2

        e5CDBuff = 0.44 if self.eidolon >= 5 else 0.40

        bl.append(Buff("AhaSpdBuff",StatTypes.SPD,self.AHASpdBuffAmount,Role.AHA,[AtkType.SPECIAL],1,1,Role.AHA,TickDown.PERM))
        if self.tech:
            self.tech = False

        if Character.SharedPunchline >= 40 and self.TalentWishpowerTrigger:
            self.Wishpower += 1
            self.TalentWishpowerTrigger = False
            bl.append(Buff("AhaTalentCD", StatTypes.CD_PERCENT, e5CDBuff, Role.ALL, [AtkType.ALL], 3, 1, self.role, TickDown.END))

        return bl, dbl, al, dl, tl, hl, sl

    def takeTurn(self) -> str:
        if self.UltActive:
            self.UltTurns -= 1
        if self.UltTurns == 0:
            self.UltActive = False
        return super().takeTurn()