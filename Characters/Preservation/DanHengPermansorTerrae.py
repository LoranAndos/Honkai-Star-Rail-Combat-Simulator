import logging

from Buff import *
from Character import Character
from Lightcones.Preservation.DHPT_Lightcone_Aeon import DHPT_Lightcone_Aeon
from Planars.LushakaTheSunkenSeas import LushakaTheSunkenSeas
from RelicStats import RelicStats
from Relics.SelfEnshroudedRecluse import SelfEnshroudedRecluse
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
    AtkStat = 0.0

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, targetRole=Role.DPS, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else DHPT_Lightcone_Aeon(role, 5)
        self.relic1 = r1 if r1 else SelfEnshroudedRecluse(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else LushakaTheSunkenSeas(role)
        self.relicStats = subs if subs else RelicStats(12, 2, 2, 2, 2, 11, 2, 2, 2, 2, 2, 2, StatTypes.ATK_PERCENT, StatTypes.SPD,
                                                       StatTypes.ATK_PERCENT, StatTypes.ERR_PERCENT)
        self.targetRole = targetRole
        self.rotation = rotation if rotation else ["A"]

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        ScalingMul = 0.212 if self.eidolon >= 5 else 0.200
        FlatMul = 445 if self.eidolon >= 5 else 400
        bl.append(Buff("DanHengPermansorTerraeATK", StatTypes.ATK, 0.28, self.role))
        bl.append(Buff("DanHengPermansorTerraeDEF", StatTypes.DEF_PERCENT, 0.225, self.role))
        bl.append(Buff("DanHengPermansorTerraeSPD", StatTypes.SPD, 5, self.role))
        al.append(Advance("DanHengPermansorTerraeTrace2Advance",self.role,0.40))

        sl.append(Shield("DanHengPermansorTerraeShield",[ScalingMul, FlatMul],Scaling.ATK,Role.ALL,self.role,Targeting.AOE, 3.0,True, 3, self.role, TickDown.END))
        bl.append(Buff("DanHengPermansorTerraeERR", StatTypes.ERR_T, 30, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        self.bondmateRole = self.targetRole
        if self.eidolon >= 4:
            bl.append(Buff("DanHengPermansorTerraeE4DMGReduction", StatTypes.DMG_REDUCTION, 0.20, self.targetRole, [AtkType.ALL], 1,
                     1, self.targetRole, TickDown.PERM))
        if self.eidolon == 6:
            dbl.append(Debuff("DanHengPermansorTerraeE6Debuff", self.role, StatTypes.VULN, 0.20, Role.ALL, [AtkType.ALL], 9999))
            bl.append(Buff("DanHengPermansorTerraeE6Shred", StatTypes.SHRED, 0.12, self.targetRole,[AtkType.ALL], 1,
                           1, self.targetRole, TickDown.PERM))
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

        # ── Bondmate: transfer hasSummon from previous bondmate to new one ───
        # Souldragon is attributed to the bondmate so equipment/lightcones that
        # check char.hasSummon on the bondmate fire correctly. DHPT itself does
        # not count as "having a summon" from an equipment-trigger perspective.
        if Character._current_player_team:
            # Clear hasSummon on old bondmate (if any)
            if self.bondmateRole is not None:
                for char in Character._current_player_team:
                    if char.role == self.bondmateRole:
                        char.hasSummon = False
                        break
            # Set hasSummon on new bondmate
            for char in Character._current_player_team:
                if char.role == self.targetRole:
                    char.hasSummon = True
                    break
            # DHPT itself does not count as having a summon
            self.hasSummon = False

        self.bondmateRole = self.targetRole
        logger.info(f"BONDMATE > {self.name} designated {self.bondmateRole} as Bondmate (hasSummon transferred)")

        bl.append(Buff("DanHengPermansorTrace1ATK", StatTypes.ATK, 0.15 * self.AtkStat, self.targetRole, [AtkType.ALL], 1, 1,
                 self.targetRole, TickDown.PERM))

        sl.append(Shield("DanHengPermansorTerraeShield", [ScalingMul, FlatMul], Scaling.ATK, Role.ALL, self.role, Targeting.AOE, 3.0, True, 3, self.role, TickDown.END))

        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.NA, [AtkType.ALL], [self.element],
                       [0, 0], [0, 0], 30, self.scaling, -1, "DanHengPermansorTerraeSkill"))
        return bl, dbl, al, dl, tl, hl, sl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e5Mul = 3.3 if self.eidolon >= 5 else 3.0
        ScalingMul = 0.212 if self.eidolon >= 5 else 0.200
        FlatMul = 445 if self.eidolon >= 5 else 400
        spChange = 1 if self.eidolon >= 1 else 0

        # ── Ult DMG: Physical AOE ─────────────────────────────────────────────
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT], [self.element],
                       [e5Mul, 0], [20, 0], 5, self.scaling, spChange, "DanHengPermansorTerraeUlt"))
        if self.eidolon == 6:
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.NA, [AtkType.ALL], [self.element],
                           [0, 0], [0, 0], 0, self.scaling, 0, "DanHengPermansorTerraeE6UltDamage"))
        if self.eidolon >= 1:
            bl.append(Buff("DanHengPermansorTerraeE1Pen", StatTypes.PEN, 0.18, self.targetRole, [AtkType.ALL], 3, 1,
                     self.targetRole, TickDown.END))

        # ── Set ultEnhanced directly on the Souldragon instance ──────────────
        # This must be done here synchronously rather than via allyTurn, because
        # the Advance(SOULDRAGON, 1.00) causes processTurnList to break early
        # (before E2SoulDragonActions is processed), so allyTurn never sees it.
        E2Multiplier = 2.0 if self.eidolon >= 2 else 1.0
        E2Actions = 4 if self.eidolon >= 2 else 2
        if hasattr(self, 'souldragon') and self.souldragon is not None:
            self.souldragon.ultEnhanced += E2Actions
            self.souldragon.E2Multiplier = E2Multiplier
            logger.info(f"SOULDRAGON > Ult enhancement granted (ultEnhanced={E2Actions}, E2Multiplier={E2Multiplier})")
        if self.eidolon >= 2:
            al.append(Advance("DanHengPermansorTerraeE2Advance", Role.SOULDRAGON, 1.00))

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
        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)
        ScalingMul = 0.106 if self.eidolon >= 5 else 0.100
        FlatMul = 222.5 if self.eidolon >= 5 else 200
        E2Multiplier = 2.0 if self.eidolon >= 2 else 1.0
        if turn.moveName == "SoulDragonShield":
            sl.append(Shield("DanHengPermansorTerraeShield", [ScalingMul*E2Multiplier, FlatMul*E2Multiplier], Scaling.ATK, Role.ALL, self.role,
                             Targeting.AOE, 3.0, False, 3, self.role, TickDown.END))
            sl.append(Shield("DanHengPermansorTerraeShield", [0.05*E2Multiplier, 100*E2Multiplier], Scaling.ATK, Role.ALL, self.role,
                             Targeting.SINGLE, 3.0, False, 3, self.role, TickDown.END))
        if turn.moveName == "SoulDragonAttack":
            bl, dbl, al, dl, tl, hl, sl = self.extendLists(bl, dbl, al, dl, tl, hl, sl, *self.useFua(-1))
        if turn.charRole == self.targetRole and turn.moveName not in bonusDMG and result.turnDmg > 0:
            bl.append(Buff("DanHengPermansorTerraeTrace2ERR", StatTypes.ERR_T, 6, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
            al.append(Advance("DanHengPermansorTerraeTrace2SouldragonAdvance", Role.SOULDRAGON, 0.15))
        return bl, dbl, al, dl, tl, hl, sl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)
        self.AtkStat = specialRes.attr1
        bl.append(Buff("DanHengPermansorTrace1ATK", StatTypes.ATK, 0.15*self.AtkStat, self.targetRole, [AtkType.ALL], 1, 1, self.targetRole, TickDown.PERM))
        return bl, dbl, al, dl, tl, hl, sl