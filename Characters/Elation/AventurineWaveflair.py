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
from random import random
from math import floor

logger = logging.getLogger(__name__)


class AventurineWaveflair(Character):
    # Standard Character Settings
    name = "AventurineWaveflair"
    path = Path.ELATION
    element = Element.QUANTUM
    scaling = Scaling.ATK
    baseHP = 1164
    baseATK = 485
    baseDEF = 606
    baseSPD = 107
    maxEnergy = 130
    currEnergy = 65
    ultCost = 130
    currAV = 0
    aggro = 100
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.ELAPUNCH: 0, AtkType.ELABANGER: 0}  # Adjust accordingly

    # Unique Character Properties


    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT,
                 elationParticipationID=156) -> None:  # Aventurine Waveflair ID: 156
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else MushyShroomysAdventuresSparxie(role,5)
        self.relic1 = r1 if r1 else EverGloriousMagicalGirl(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else TengokuLivestream(role)
        self.relicStats = subs if subs else RelicStats(6, 2, 2, 2, 2, 8, 2, 2, 2, 2, 9, 9, StatTypes.CR_PERCENT, StatTypes.SPD, StatTypes.ATK_PERCENT, StatTypes.ERR_PERCENT)
        self.rotation = rotation if rotation else ["E"]
        self.elationParticipationID = elationParticipationID

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("BangerStartBattle", StatTypes.BANGER, 20, self.role, [AtkType.ALL], 2, 1, self.role, TickDown.END))
        bl.append(Buff("SparxieTraceCR", StatTypes.CR_PERCENT, 0.12, self.role))
        bl.append(Buff("SparxieTraceCD", StatTypes.CD_PERCENT, 0.133, self.role))
        bl.append(Buff("SparxieTraceELA", StatTypes.ELA, 0.28, self.role))
        return bl, dbl, al, dl, hl, sl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC],
[self.element],[e3Mul, 0], [10, 0], 20, self.scaling, 1, "SparxieBasic"))
        return bl, dbl, al, dl, tl, hl, sl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useSkl(enemyID)

        return bl, dbl, al, dl, tl, hl, sl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost

        return bl, dbl, al, dl, tl, hl, sl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().ownTurn(turn, result)
        if result.turnName == "AhaSparxieGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        pearl = next((c for c in (Character._current_player_team or []) if c.name == "Pearl"), None)
        if result.turnName == "SparxieSkillElaExtra" and Character.PearlUlt == True and pearl is not None and self.role == pearl.targetRole:
            bl.append(Buff("PearlAestheticArchetypeBanger", StatTypes.BANGER, 0, self.role,
                           [AtkType.ALL], 2, 1, self.role, TickDown.PERM))
            Character.SharedPunchline -= 60 * Character.PearlE2Modifier
            Character.PearlUlt = False

        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)

        if result.turnName == "AhaSparxieGoGo" or result.turnName == f"ElationMCUltTrigger_{self.role.name}":
            return self.useElaSkill(-1)

        pearl = next((c for c in (Character._current_player_team or []) if c.name == "Pearl"), None)
        if result.turnName == "PearlUltimate" and Character.PearlUlt == True and pearl is not None and self.role == pearl.targetRole:
            bl.append(Buff("PearlAestheticArchetypeBanger", StatTypes.BANGER, 30 * Character.PearlE2Modifier, self.role,
                           [AtkType.ALL], 2, 1, self.role, TickDown.PERM))
            Character.SharedPunchline += 60 * Character.PearlE2Modifier

            bl, dbl, al, dl, tl, hl, sl = self.extendLists(bl, dbl, al, dl, tl, hl, sl, *self.useSkl(-1))

        return bl, dbl, al, dl, tl, hl, sl

    def useElaSkill(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useElaSkill(enemyID)
        # Aventurine Wavelflair laatste elation skill hit ook toevoegen aan lijst in summons voor aha correct te laten verlopen en ook gewoon in lijst van attributes en bij alle andere zaken die horen bij Pearl

        return bl, dbl, al, dl, tl, hl, sl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)


        bl.append(Buff("AhaSpdBuff",StatTypes.SPD,self.AHASpdBuff,Role.AHA,[AtkType.SPECIAL],1,1,Role.AHA,TickDown.START))
        if self.tech:
            self.tech = False

        return bl, dbl, al, dl, tl, hl, sl
