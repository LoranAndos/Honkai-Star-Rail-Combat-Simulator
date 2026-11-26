import logging

from Lightcones.Remembrance.RiseAndSing import RiseAndSing
from Relics.WorldRemakingDeliverer import WorldRemakingDeliverer
from Planars.AmphoreusTheEternalLand import AmphoreusTheEternalLand
from Buff import *
from Character import Character
from Delay_Text import *
from RelicStats import RelicStats
from Result import *
from Turn_Text import Turn
from Healing import *

logger = logging.getLogger(__name__)

OFF_BAR_SPD = 0.0001      # SPD of a unit that has no place on the action bar (same convention as Memosprite.OFF_FIELD_SPD)


class RobinSummeretto(Character):
    """
    She owns the Vibes and the Fever state; the Summer Songbirds (SummerSongbirds.py) are her memosprite and talk to her only through
    `vibes`, `feverActive`, `eidolon`, `onFeverStart()` / `onFeverEnd()` and the Turn named "SongbirdsSpawn".
    Put her BEFORE the Songbirds in the team list and give the Songbirds to startSimulator through `extraChars`.
    """
    # Standard Character Properties
    name = "RobinSummeretto"
    path = Path.REMEMBRANCE
    element = Element.WIND
    scaling = Scaling.HP
    baseHP = 1203
    baseATK = 602
    baseDEF = 485
    baseSPD = 95
    maxEnergy = 140
    ultCost = 140
    currEnergy = 70
    currAV = 0
    aggro = 100
    buffList = []

    # Unique Character Properties
    hasMemosprite = True
    GrooveOnHeal = True
    CountMemoAttacks = True  # attacks of other memosprites (Mem) give Vibes too

    ATTACK_TYPES = (AtkType.BSC, AtkType.SKL, AtkType.ULT, AtkType.FUA, AtkType.MEMO, AtkType.ELAPUNCH, AtkType.ELABANGER)

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc = None, r1 = None, r2 = None, pl = None, subs = None, eidolon = 6, targetPrio = Priority.BROKEN, rotation = None, ultTarget: Role = Role.DPS) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else RiseAndSing(self.role, 5)
        self.relic1 = r1 if r1 else WorldRemakingDeliverer(self.role, 4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else AmphoreusTheEternalLand(self.role)
        # sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD% | main stats: Body, Boots, Sphere, Rope
        self.relicStats = subs if subs else RelicStats(8, 2, 2, 2, 9, 2, 2, 2, 2, 2, 2, 9, StatTypes.CD_PERCENT, StatTypes.SPD,
                                                       StatTypes.HP_PERCENT, StatTypes.HP_PERCENT)
        self.rotation = rotation if rotation else ["E", "A"]
        self.ultTarget = ultTarget
        # per-instance state (class-level lists/flags would be shared between runs)
        self.vibes = 0
        self.groove = 0
        self.feverActive = False
        self.technique = True
        self.guestRole = None            # ally that currently is the Special Guest
        self.maxHPNow = 0.0              # snapshots refreshed at the start of every unit's turn (handleSpec)
        self.atkNow = 0.0
        self.allyATK = {}
        self._vibeActionId = -1          # one Vibe per action and ally (Character.actionId), E2 / Groove once per action
        self._vibeGivers = set()
        self._firstGainDone = False
        self._deviatedKind = {}

    # ------------------------------------------------------------------ helpers
    @property
    def vibeCap(self) -> int:
        return 70 if self.eidolon >= 2 else 50

    def getSongbirds(self):
        return next((c for c in (Character._current_player_team or []) if c.name == "SummerSongbirds"), None)

    def addVibes(self, amount: int) -> int:
        before = self.vibes
        self.vibes = min(self.vibeCap, self.vibes + amount)
        logger.info(f"{self.name}: Vibes {before} -> {self.vibes}")
        return self.vibes - before

    def spdOverride(self):
        # In Fever Robin takes no turns: she has no place on the action bar until the Songbirds leave
        return OFF_BAR_SPD if self.feverActive else None

    def _energyTurn(self, amount: float, name: str) -> Turn:
        return Turn(self.name, self.role, -1, Targeting.NA, [AtkType.SPECIAL], [self.element], [0, 0], [0, 0], amount,
                    self.scaling, 0, name)

    def equip(self):  # function to add base buffs to wearer
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("RobinSummerettoTraceCR", StatTypes.CR_PERCENT, 0.067, self.role))
        bl.append(Buff("RobinSummerettoTraceSPD", StatTypes.SPD, 14, self.role))
        bl.append(Buff("RobinSummerettoTraceHP", StatTypes.HP_PERCENT, 0.18, self.role))
        bl.append(Buff("RobinRebuiltHarmonyCR", StatTypes.CR_PERCENT, 0.50, self.role))          # A6: +50% CRIT Rate (the Songbirds get their own)
        if self.eidolon >= 2:
            bl.append(Buff("RobinE2ResPen", StatTypes.PEN, 0.18, Role.ALL, [AtkType.ALL], 1, 1, self.role, TickDown.PERM))
        return bl, dbl, al, dl, hl, sl

    # ------------------------------------------------------------------ actions
    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useBsc(enemyID)
        e5Mul = 1.1 if self.eidolon >= 5 else 1.0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element], [e5Mul, 0],
                       [10, 0], 20, self.scaling, 1, "RobinSummerettoBasic"))
        return bl, dbl, al, dl, tl, hl, sl

    def useSkl(self, enemyID=-1):
        # Summons Bessie; with the Songbirds already out it heals them (resolved in SummerSongbirds.allyTurn) and gives 6 Vibes
        bl, dbl, al, dl, tl, hl, sl = super().useSkl(enemyID)
        birds = self.getSongbirds()
        if birds is not None and birds.MemoActive:
            self.addVibes(6)
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.NA, [AtkType.SKL], [self.element], [0, 0], [0, 0],
                       30, self.scaling, -1, "SongbirdsSpawn"))
        return bl, dbl, al, dl, tl, hl, sl

    def useUlt(self, enemyID=-1):
        self.currEnergy = self.currEnergy - self.ultCost
        bl, dbl, al, dl, tl, hl, sl = super().useUlt(enemyID)
        e5Mul = 0.216 if self.eidolon >= 5 else 0.20
        team = Character._current_player_team or []
        ally = next((c for c in team if c.role == self.ultTarget and c is not self), None)
        if ally is None:
            ally = next((c for c in team if c is not self and not getattr(c, "isMemosprite", False) and not c.isSummon()), None)
        if ally is not None:
            role = ally.role
            refill = e5Mul * ally.maxEnergy
            al.append(Advance("RobinSummerettoUltADV", role, 1.00))
            if refill > 0:
                bl.append(Buff("RobinSummerettoUltEnergy", StatTypes.ERR_F, refill, role, [AtkType.ALL], 1, 1, role, TickDown.START))
            # Special Guest (marker buff: Robin reads it back through handleSpec): 2 turns, ticks on the guest's own turns
            bl.append(Buff("RobinSpecialGuest", StatTypes.DMG_PERCENT, 0, role, [AtkType.ALL], 2, 1, role, TickDown.END))
            self.guestRole = role
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.NA, [AtkType.ULT], [self.element], [0, 0], [0, 0],
                       5, self.scaling, 0, "RobinSummerettoUlt"))
        return bl, dbl, al, dl, tl, hl, sl

    # ------------------------------------------------------------------ Vibes
    def _vibeSource(self, result: Result):
        """Which ally action (attack or heal) gives Vibes: returns the ally's role or None."""
        role = result.charRole
        if role == self.role:
            return None
        ally = next((c for c in (Character._current_player_team or []) if c.role == role), None)
        if ally is None or ally.name == "SummerSongbirds":
            return None
        if getattr(ally, "isMemosprite", False) and not self.CountMemoAttacks:
            return None
        dealt = (getattr(result, "TotalDamage", 0) or 0) > 0 or bool(getattr(result, "enemiesHit", None))
        isAttack = dealt and any(a in self.ATTACK_TYPES for a in (result.atkType or []))
        isHeal = (getattr(result, "HPGain", 0) or 0) > 0
        if isAttack:
            return role, "attack"
        if isHeal:
            return role, "heal"
        return None

    def _deviatedChords(self, role: Role, bl: list):
        v = self.vibes
        allyATK = self.allyATK.get(role)
        useATK = allyATK is not None and allyATK > self.atkNow
        kind = "ATK" if useATK else "CD"
        if useATK:
            hp = self.maxHPNow if self.maxHPNow > 0 else self.maxHP
            bl.append(Buff("RobinDeviatedATK", StatTypes.ATK, (0.16 + 0.4 * v) * hp, role,
                           [AtkType.ALL], 2, 1, role, TickDown.END))
        else:
            bl.append(Buff("RobinDeviatedCD", StatTypes.CD_PERCENT, 0.40 + 0.015 * v, role,
                           [AtkType.ALL], 2, 1, role, TickDown.END))
        other = self._deviatedKind.get(role)
        if other is not None and other != kind:     # the other variant (from an earlier action) ends
            bl.append(Buff("RobinDeviatedATK" if kind == "CD" else "RobinDeviatedCD",
                           StatTypes.ATK if kind == "CD" else StatTypes.CD_PERCENT, 0.0, role, [AtkType.ALL], 2, 1, role, TickDown.END))
        self._deviatedKind[role] = kind

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)
        src = self._vibeSource(result)
        if src is None:
            return bl, dbl, al, dl, tl, hl, sl
        role, kind = src
        # a new action starts: every ally gives Vibes once per action, E2 and Groove trigger once per action
        if Character.actionId != self._vibeActionId:
            self._vibeActionId = Character.actionId
            self._vibeGivers = set()
            self._firstGainDone = False
        if kind == "heal" and self.GrooveOnHeal:
            self.groove = 12
        if role in self._vibeGivers:
            return bl, dbl, al, dl, tl, hl, sl
        self._vibeGivers.add(role)

        gain = 2 if role == self.guestRole else 1
        if self.eidolon >= 2 and not self._firstGainDone:
            gain += 2
        self.addVibes(gain)
        if not self._firstGainDone:
            self._firstGainDone = True
            if self.groove > 0:
                self.groove -= 1
                tl.append(self._energyTurn(3, "RobinSummerettoGrooveEnergy"))
        self._deviatedChords(role, bl)
        return bl, dbl, al, dl, tl, hl, sl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().ownTurn(turn, result)
        return bl, dbl, al, dl, tl, hl, sl

    # ------------------------------------------------------------------ Fever (called by the Songbirds)
    def onFeverStart(self):
        bl, dbl, al, dl, tl = [], [], [], [], []
        self.feverActive = True
        if self.eidolon >= 4:
            self.addVibes(12)
        v = self.vibes
        e3Mul = 0.16 if self.eidolon >= 3 else 0.15
        # "Not dynamic": both values keep the Vibe count of this moment while the Vibes drain
        zone = e3Mul + 0.005 * v
        feverDMG = (0.66 + 0.022 * v) if self.eidolon >= 3 else (0.60 + 0.02 * v)
        bl.append(Buff("RobinZoneShred", StatTypes.SHRED, zone, Role.ALL, [AtkType.ALL], 1, 1, self.role, TickDown.PERM))
        bl.append(Buff("RobinFeverDMG", StatTypes.DMG_PERCENT, feverDMG, self.role, [AtkType.ALL], 1, 1, self.role, TickDown.PERM))
        birds = self.getSongbirds()
        if birds is not None:
            bl.append(Buff("RobinFeverDMG", StatTypes.DMG_PERCENT, feverDMG, birds.role, [AtkType.ALL], 1, 1, birds.role, TickDown.PERM))
        if self.eidolon >= 6:
            self.maxEnergy = 280
            bl.append(Buff("RobinE6FeverEnergy", StatTypes.ERR_F, 140, self.role, [AtkType.ALL], 1, 1, self.role, TickDown.END))
        logger.info(f"{self.name}: Fever starts (Vibes {v}, Zone {zone:.3f}, DMG +{feverDMG:.3f})")
        return bl, dbl, al, dl, tl

    def onFeverEnd(self):
        bl, dbl, al, dl, tl = [], [], [], [], []
        self.feverActive = False
        bl.append(Buff("RobinZoneShred", StatTypes.SHRED, 0.0, Role.ALL, [AtkType.ALL], 1, 1, self.role, TickDown.PERM))
        bl.append(Buff("RobinFeverDMG", StatTypes.DMG_PERCENT, 0.0, self.role, [AtkType.ALL], 1, 1, self.role, TickDown.PERM))
        birds = self.getSongbirds()
        if birds is not None:
            bl.append(Buff("RobinFeverDMG", StatTypes.DMG_PERCENT, 0.0, birds.role, [AtkType.ALL], 1, 1, birds.role, TickDown.PERM))
        if self.maxEnergy != type(self).maxEnergy:
            self.maxEnergy = type(self).maxEnergy
            self.currEnergy = min(self.currEnergy, self.maxEnergy)
        logger.info(f"{self.name}: Fever ends")
        return bl, dbl, al, dl, tl

    # ------------------------------------------------------------------ turn flow
    def takeTurn(self) -> str:
        res = super().takeTurn()
        birds = self.getSongbirds()
        if birds is not None and not birds.MemoActive:
            return "E"           # no Songbirds out: summon Bessie
        return res

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)   # also stores enemyStatus for bestEnemy()
        # snapshots from the engine (handleSpec): Special Guest, Robin's Max HP / ATK, the allies' ATK (for Deviated Chords)
        self.guestRole = specialRes.attr1
        self.maxHPNow = specialRes.attr2 or 0.0
        self.atkNow = specialRes.attr3 or 0.0
        self.allyATK = specialRes.attr4 or {}
        if self.technique:
            self.technique = False
            self.addVibes(6)
            bl.append(Buff("RobinTechniqueDMG", StatTypes.DMG_PERCENT, 0.30, Role.ALL, [AtkType.ALL], 2, 1,
                           Role.SELF, TickDown.END))
            al.append(Advance("RobinSummerettoTechADV", self.role, 0.20))
        return bl, dbl, al, dl, tl, hl, sl