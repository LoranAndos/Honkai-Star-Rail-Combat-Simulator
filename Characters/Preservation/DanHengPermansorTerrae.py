import logging

from Buff import *
from Character import Character
from Lightcones.Destruction.IAmAsYouBehold import IAmAsYouBehold
from Lightcones.Destruction.OnTheFallOfAnAeon import OnTheFallOfAnAeon
from Lightcones.Destruction.ATrailOfBygoneBlood import ATrailOfBygoneBlood
from Lightcones.Destruction.ASecretVow import ASecretVow
from Planars.CosmicLifeSciencesInstitute import CosmicLifeSciencesInstitute
from Planars.InertSalsotto import InertSalsotto
from RelicStats import RelicStats
from Relics.ScholarLostInErudition import ScholarLostInErudition
from Relics.AsNavigatorIseeSeesIt import AsNavigatorIseeSeesIt
from Result import *
from Turn_Text import Turn
from Delay_Text import Advance
from Healing import *
from Shields import Shield
from Summons import Souldragon

logger = logging.getLogger(__name__)


class DangHengPermansorTerrae(Character):
    # Standard Character Settings
    name = "DanHengPermansorTerrae"
    path = Path.PRESERVATION
    element = Element.PHYSICAL
    scaling = Scaling.ATK
    baseHP = 1048
    baseATK = 582
    baseDEF = 776
    baseSPD = 97
    maxEnergy = 135
    currEnergy = 67.5
    ultCost = 135
    currAV = 0
    aggro = 150
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.FUA: 0}
    hasSummon = True

    # Unique Character Properties
    bondmateRole = None     # Role of the current Bondmate (most recent Skill target)

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, targetRole=Role.DPS, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else OnTheFallOfAnAeon(role, 5)
        self.relic1 = r1 if r1 else ScholarLostInErudition(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else CosmicLifeSciencesInstitute(role)
        self.relicStats = subs if subs else RelicStats(7, 2, 2, 2, 2, 3, 2, 2, 2, 2, 11, 10, StatTypes.CR_PERCENT, StatTypes.SPD,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.targetRole = targetRole
        self.rotation = rotation if rotation else ["A"]

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        ScalingMul = 0.212 if self.eidolon >= 5 else 0.200
        FlatMul = 445 if self.eidolon >= 5 else 400
        bl.append(Buff("DanHengPermansorTerraeATK", StatTypes.ATK, 0.28, self.role))
        bl.append(Buff("DanHengPermansorTerraeDEF", StatTypes.DEF_PERCENT, 0.225, self.role))
        bl.append(Buff("DanHengPermansorTerraeSPD", StatTypes.SPD, 5, self.role))

        sl.append(Shield("DanHengPermansorTerraeShield",[ScalingMul, FlatMul],Scaling.ATK,Role.ALL,self.role,Targeting.AOE, 3.0,True, 3, self.role, TickDown.END))
        bl.append(Buff("DanHengPermansorTerraeERR", StatTypes.ERR_T, 30, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        return bl, dbl, al, dl, hl, sl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20, self.scaling, 1, "DanHengPermansorTerraeBasic"))
        return bl, dbl, al, dl, tl, hl, sl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useSkl(enemyID)
        ScalingMul = 0.212 if self.eidolon >= 5 else 0.200
        FlatMul = 445 if self.eidolon >= 5 else 400

        # ── Bondmate: set to targetRole ──────────────────────────────────────
        self.bondmateRole = self.targetRole
        logger.info(f"BONDMATE > {self.name} designated {self.bondmateRole} as Bondmate")

        sl.append(Shield("DanHengPermansorTerraeShield",[ScalingMul, FlatMul],Scaling.ATK,Role.ALL,self.role,Targeting.AOE, 3.0,True, 3, self.role, TickDown.END))

        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.NA, [AtkType.ALL], [self.element],
                       [0, 0], [0, 0], 30, self.scaling, -1, "DanHengPermansorTerraeSkill"))
        return bl, dbl, al, dl, tl, hl, sl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e5Mul = 3.3 if self.eidolon >= 5 else 3.0
        ScalingMul = 0.212 if self.eidolon >= 5 else 0.200
        FlatMul = 445 if self.eidolon >= 5 else 400

        # ── Ult DMG: Physical AOE ─────────────────────────────────────────────
        tl.append(Turn(self.name, self. role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT], [self.element],
                       [e5Mul, 0], [20, 0], 5, self.scaling, 0, "DanHengPermansorTerraeUlt"))
        logger.info(f"SOULDRAGON > Ult enhancement granted (2 enhanced actions)")

        # ── Ult shield: same formula as Skill but non-defining ───────────────
        # isDefining=False: adds to currentAmount but never changes the cap,
        # which remains as last set by the Skill application.
        sl.append(Shield("DanHengPermansorTerraeShield",[ScalingMul, FlatMul],Scaling.ATK,Role.ALL,self.role,Targeting.AOE, 3.0,False, 3, self.role, TickDown.END))

        return bl, dbl, al, dl, tl, hl, sl

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useFua(enemyID)
        e3Mul = 0.88 if self.eidolon >= 3 else 0.80
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.FUA], [self.element],
                       [e3Mul, 0], [20, 0], 0, self.scaling, 0, "DanHengPermansorTerraeFUA"))
        return bl, dbl, al, dl, tl, hl, sl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().ownTurn(turn, result)
        ScalingMul = 0.106 if self.eidolon >= 5 else 0.100
        FlatMul = 222.5 if self.eidolon >= 5 else 200
        if turn.moveName == "SoulDragonShield":
            sl.append(Shield("DanHengPermansorTerraeShield", [ScalingMul, FlatMul], Scaling.ATK, Role.ALL, self.role,
                             Targeting.AOE, 3.0, False, 3, self.role, TickDown.END))
        if turn.moveName == "SoulDragonAttack":
            bl, dbl, al, dl, tl, hl, sl = self.extendLists(bl, dbl, al, dl, tl, hl, sl, *self.useFua(-1))
        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)
        return bl, dbl, al, dl, tl, hl, sl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)
        return bl, dbl, al, dl, tl, hl, sl
