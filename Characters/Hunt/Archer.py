import logging

from Buff import *
from Character import Character
from Lightcones.Hunt.TheHellWhereIdealsBurn import TheHellWhereIdealsBurn
from Planars.TengokuLivestream import TengokuLivestream
from RelicStats import RelicStats
from Relics.GeniusOfBrilliantStars import GeniusOfBrilliantStars
from Result import *
from Turn_Text import Turn
from Healing import *

logger = logging.getLogger(__name__)


class Archer(Character):
    # Standard Character Settings
    name = "Archer"
    path = Path.HUNT
    element = Element.QUANTUM
    scaling = Scaling.ATK
    baseHP = 1164
    baseATK = 621
    baseDEF = 485
    baseSPD = 100
    maxEnergy = 220
    currEnergy = 110
    ultCost = 220
    currAV = 0
    aggro = 75
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0, AtkType.FUA: 0}  # Adjust accordingly

    # Unique Character Properties
    FUACharge = 1
    SPAmount = 0
    Tech = True
    RinTohsakaInTeam = False
    RinTurnHappened = True
    RinEidolon = 0
    E6SP = False

    # Circuit Connection state
    circuitActive = False      # Whether "Circuit Connection" state is currently active
    circuitSklCount = 0        # Number of skills used within the current Circuit Connection (max 5)
    circuitDMGStacks = 0       # Stacked DMG bonus from repeated skill use in circuit (max 2, +100% each)

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope
    # With Sparkle:
    # self.relicStats = subs if subs else RelicStats(2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 14, 9, StatTypes.CR_PERCENT, StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT, StatTypes.ATK_PERCENT)

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=0, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else TheHellWhereIdealsBurn(role, 1)
        self.relic1 = r1 if r1 else GeniusOfBrilliantStars(role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else TengokuLivestream(role)
        self.relicStats = subs if subs else RelicStats(2, 2, 2, 2, 2, 3, 2, 2, 2, 2, 13, 10, StatTypes.CR_PERCENT, StatTypes.ATK_PERCENT,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.rotation = rotation if rotation else ["E"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("ArcherTraceCR", StatTypes.CD_PERCENT, 0.067, self.role))
        bl.append(Buff("ArcherTraceATK", StatTypes.ATK_PERCENT, 0.18, self.role))
        bl.append(Buff("ArcherTraceDMG", StatTypes.DMG_PERCENT, 0.224, self.role))
        if self.eidolon >= 4:
            bl.append(Buff("ArcherE4UltDMG", StatTypes.DMG_PERCENT, 1.50, self.role,[AtkType.ULT],1,1, self.role, TickDown.PERM))
        if self.eidolon >= 6:
            bl.append(Buff("ArcherE6SKLShred", StatTypes.SHRED, 0.20, self.role,[AtkType.SKL],1,1, self.role, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],
                       [e3Mul, 0], [10, 0], 20, self.scaling, 1, "ArcherBasic"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e3Mul = 3.96 if self.eidolon >= 3 else 3.6
        e6DmgBoostLimit = 3 if self.eidolon == 6 else 2

        if not self.circuitActive:
            # ── First skill use: enter Circuit Connection ──────────────────────
            self.circuitActive = True
            self.circuitSklCount = 1
            self.circuitDMGStacks = 0
            logger.info(f"CIRCUIT > {self.name} entered Circuit Connection (use 1/5)")
        else:
            # ── Subsequent use inside Circuit Connection ───────────────────────
            self.circuitSklCount += 1
            self.circuitDMGStacks = min(self.circuitDMGStacks + 1, e6DmgBoostLimit)
            logger.info(f"CIRCUIT > {self.name} Circuit skill use {self.circuitSklCount}/5, DMG stacks: {self.circuitDMGStacks}")

        # Emit the damage hit for this use, scaled by current stacks.
        # circuitDMGStacks is 0 on use-1, 1 on use-2, 2 on uses 3-5.
        stkMul = 1.0 + self.circuitDMGStacks * 1.0
        SpUsage = 0 if self.circuitSklCount == 3 and self.eidolon >= 1 else -2
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.SKL],
                       [self.element], [e3Mul * stkMul, 0], [20, 0], 30, self.scaling, SpUsage, "ArcherSkill"))
        # Check exit conditions AFTER emitting the hit so the final hit uses the
        # correct (accumulated) stkMul before state is cleared.
        spAfterThis = self.SPAmount - 2
        if spAfterThis <= 3 and self.RinTohsakaInTeam and self.RinTurnHappened:
            bl, dbl, al, dl, tl, hl = self.extendLists(bl, dbl, al, dl, tl, hl, *self.useJointAttack(-1))
            self.RinTurnHappened = False
            spAfterThis += 4
        shouldExit = (self.circuitSklCount >= 5) or (spAfterThis < abs(SpUsage))
        if shouldExit:
            self.circuitActive = False
            self.circuitDMGStacks = 0
            self.circuitSklCount = 0
            logger.info(f"CIRCUIT > {self.name} exited Circuit Connection state")

        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        self.currEnergy = self.currEnergy - self.ultCost
        e5Mul = 10.8 if self.eidolon >= 5 else 10.0
        if self.eidolon >= 2:
            dbl.append(Debuff("ArcherE2ResPen", self.role, StatTypes.QUAPEN, 0.20, self.bestEnemy(enemyID), [AtkType.ALL], 2,1,Targeting.SINGLE))
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.ULT], [self.element],
                       [e5Mul, 0], [30, 0], 5, self.scaling, 0, "ArcherUlt"))
        self.FUACharge = min(self.FUACharge+2,4)
        logger.info(f"Archer Obtained 2 FUA Charge")
        return bl, dbl, al, dl, tl, hl

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useFua(enemyID)
        e5Mul = 2.2 if self.eidolon >= 5 else 2.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.FUA], [self.element],
                       [e5Mul, 0], [10, 0], 5, self.scaling, 1, "ArcherFUA"))
        self.FUACharge -= 1
        return bl, dbl, al, dl, tl, hl

    def useJointAttack(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useJointAttack(enemyID)
        e3RinMult = 3.3 if self.RinEidolon >= 3 else 3.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.FUA],
                       [self.element], [e3RinMult, 0], [0, 0], 0, self.scaling, 0, "ArcherJointAttack"))
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        # If all enemies are defeated mid-circuit, cancel the remaining uses.
        if self.circuitActive and self.get_alive_enemy_count() == 0:
            self.circuitActive = False
            self.circuitDMGStacks = 0
            self.circuitSklCount = 0
            logger.info(f"CIRCUIT > {self.name} exited Circuit Connection (all enemies defeated)")
        if self.SPAmount >= 4 and turn.spChange >= 1 or turn.spChange >= 4:
            bl.append(Buff("Trace3CD", StatTypes.CD_PERCENT,1.20, self.role,[AtkType.ALL],1,1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, tl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        if (turn.moveName not in bonusDMG) and result.enemiesHit and result.turnDmg > 0 and self.FUACharge > 0:
            bl, dbl, al, dl, tl, hl = self.extendLists(bl, dbl, al, dl, tl, hl, *self.useFua(-1))
        if self.SPAmount >= 4 and turn.spChange >= 1 or turn.spChange >= 4:
            bl.append(Buff("Trace3CD", StatTypes.CD_PERCENT,1.20, self.role,[AtkType.ALL],1,1, Role.SELF, TickDown.END))
        if turn.moveName not in bonusDMG and turn.charName == "RinTohsaka" and turn.moveName != ("RinTohsakaJointAttack" or "RinTohsakaUltSide"):
            self.RinTurnHappened = True
        return bl, dbl, al, dl, tl, hl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl = super().handleSpecialStart(specialRes)
        self.SPAmount = specialRes.attr1
        isOwnTurn = specialRes.attr2
        self.RinTohsakaInTeam = specialRes.attr3
        self.RinEidolon = specialRes.attr4
        if self.RinTohsakaInTeam:
            bl.append(Buff("RinTohsakaAllyTrace1ATK", StatTypes.ATK_PERCENT, 1.50, self.role))
            bl.append(Buff("RinTohsakaAllyTrace1Shred", StatTypes.SHRED, 0.20, self.role))
        if self.Tech:
            tl.append(Turn(self.name, self.role, -1, Targeting.AOE, [AtkType.TECH], [self.element], [2.0, 0], [0, 0], 0, self.scaling, 0, "ArcherTech"))
            self.FUACharge = min(self.FUACharge + 1, 4)
            self.Tech = False
        # E6: recover 1 SP at the start of Archer's own turn
        if self.eidolon >= 6 and isOwnTurn:
            bl.append(Buff("ArcherE6SP", StatTypes.SKLPT, 1, self.role))
        return bl, dbl, al, dl, tl, hl