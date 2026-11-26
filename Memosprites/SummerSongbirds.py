import logging
import math

from Buff import *
from Memosprite import Memosprite
from Character import Character
from Delay_Text import *
from RelicStats import RelicStats
from Result import *
from Turn_Text import Turn
from Healing import *
from Summons import FeverCountdown, OFF_BAR_SPD

logger = logging.getLogger(__name__)


class NullEquipment:
    """The Summer Songbirds wear no Light Cone / relics of their own: this placeholder only carries zero base stats and
    does nothing on any hook, so the generic Memosprite code (which calls every equipment piece) keeps working."""
    name = "None"
    setType = 0
    level = 0
    baseHP = 0
    baseATK = 0
    baseDEF = 0
    wearer = None

    def __init__(self, *args, **kwargs):
        pass

    def __str__(self) -> str:
        return "None"

    @staticmethod
    def _none(*args, **kwargs):
        return [], [], [], [], [], []

    equip = useBsc = useSkl = useUlt = useFua = useAdd = useElaSkill = useMemo = useHit = _none
    specialStart = specialEnd = ownTurn = allyTurn = _none


class SummerSongbirds(Memosprite):
    """Robin - Summeretto's memosprite "Summer Songbirds" (Bessie, Drummie and Paddie), modelled as ONE unit with 1-3 members.
    The unit talks to Robin ONLY through attributes/methods listed here, so Robin must provide:
        vibes (number), feverActive (bool), eidolon, onFeverStart() and onFeverEnd() -> (bl, dbl, al, dl, tl)   [both optional]
    and must emit a Turn named "SongbirdsSpawn" (Targeting.NA, charName == Robin) when her Skill is used.
    Put Robin BEFORE this unit in the team list so that Vibes she gains from an ally Turn are visible to this unit's allyTurn.
    The countdown is a Summon: MainFunctions.addSummons adds `songbirds.countdown` to the summons list.
    """
    # Standard Character Properties
    name = "SummerSongbirds"
    path = Path.REMEMBRANCE
    element = Element.WIND
    scaling = Scaling.HP
    MemoSummonerName = "RobinSummeretto"
    baseHP = 0
    baseATK = 0
    baseDEF = 0
    baseSPD = OFF_BAR_SPD
    maxEnergy = 0
    EnergyCost = 100
    currEnergy = 0
    currAV = 100.0
    MemoActive = False
    rotation = ["MEMO"]
    specialEnergy = True
    hasMemosprite = False
    hasSummon = True
    removeOnDisappear = ("SongbirdsE4SPD",)
    mirrorMasterGear = True
    ACT_OUTSIDE_FEVER = False

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 MemTarget=None, eidolon=6, targetPrio=Priority.BROKEN, rotation=None) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else NullEquipment()
        self.relic1 = r1 if r1 else NullEquipment()
        self.relic2 = r2 if r2 else None
        self.planar = pl if pl else NullEquipment()
        self.relicStats = subs if subs else RelicStats(0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 12, StatTypes.CR_PERCENT,
                                                       StatTypes.SPD, StatTypes.DMG_PERCENT, StatTypes.HP_PERCENT)
        self.rotation = rotation if rotation else ["MEMO"]
        # per-instance state (class-level lists/flags would be shared between runs)
        self.MemoActive = False
        self.members = 0                 # 0 = off the field, 1 = Bessie, 2 = +Drummie, 3 = +Paddie
        self.hpSnapshot = 0.0            # Bessie's initial Max HP (snapshot at summon)
        self.recordedDMG = 0.0           # E1: DMG recorded from allies
        self.e4Bonus = 0.0               # E4 SPD% bonus, snapshot on Fever entry
        self._masterOOCHP = 0.0          # Robin's out-of-combat Max HP (updated every special-start)
        self._masterPermFlatSPD = 0.0    # Robin's permanent flat SPD buffs (traces)
        countdownRole = getattr(Role, "FEVERCOUNTDOWN", None)
        self.countdown = FeverCountdown(role, countdownRole)

    # ------------------------------------------------------------------ helpers
    @property
    def aggro(self):
        return 100

    def getMaster(self):
        for c in (Character._current_player_team or []):
            if c.name == self.MemoSummonerName:
                return c
        return None

    def _e(self) -> int:
        master = self.getMaster()
        return master.eidolon if master is not None else self.eidolon

    def _talentMul(self) -> float:
        return 1.1 if self._e() >= 3 else 1.0           # E3: Memosprite Talent +1 level (approximated as x1.1)

    def feverActive(self) -> bool:
        master = self.getMaster()
        return bool(master is not None and getattr(master, "feverActive", False))

    def _mirrorGear(self):
        master = self.getMaster()
        if self.mirrorMasterGear and master is not None and getattr(master, "relicStats", None) is not None:
            self.relicStats = master.relicStats

    @staticmethod
    def _merge(dst: tuple, src: tuple) -> tuple:
        for d, s in zip(dst, src):
            d.extend(s)
        return dst

    def _energyTurn(self, master, amount: float, name: str) -> Turn:
        return Turn(master.name, master.role, -1, Targeting.NA, [AtkType.SPECIAL], [master.element],
                    [0, 0], [0, 0], amount, master.scaling, 0, name)

    def _vulnDebuff(self, members: int = None) -> Debuff:
        members = self.members if members is None else members
        VULN_BY_MEMBERS = (0.0, 0.088, 0.132, 0.176) if self._e() >= 3 else (0.0, 0.08, 0.12, 0.16)
        val = VULN_BY_MEMBERS[max(0, min(3, members))] * self._talentMul()
        return Debuff("SongbirdsVuln", self.role, StatTypes.VULN, val, -1, [AtkType.ALL], 999, 1, Targeting.AOE)

    def _inheritedFlatSPDBuff(self) -> Buff:
        # flat SPD (gear + traces) of Robin, out of combat, x1.8 - permanent, refreshed every special-start
        return Buff("SongbirdsInheritedFlatSPD", StatTypes.SPD, 1.80 * self._masterPermFlatSPD, self.role)

    def _stopClock(self):
        self.currSPD = OFF_BAR_SPD
        self.currAV = 10000.0 / OFF_BAR_SPD
        if self.countdown is not None:
            self.countdown.currSPD = OFF_BAR_SPD
            self.countdown.currAV = 10000.0 / OFF_BAR_SPD

    # ------------------------------------------------------------------ stats
    def getSPD(self) -> float:
        # Gear SPD of Robin x1.8. Together with baseSPD (1.8 x Robin's base) and the inherited flat buff this gives
        # 1.8 x Robin's out-of-combat SPD; SPD% buffs on the Songbirds then multiply only their own base SPD.
        master = self.getMaster()
        return 1.80 * master.getSPD() if master is not None else 0.0

    def getHPFlat(self) -> float:
        return 0.0                       # Max HP comes from inheritMaxHP (gear HP of Robin is already inside her Max HP)

    def getHPPercent(self) -> float:
        return 0.0

    def inheritMaxHP(self, masterMaxHP: float, buffHPPercent: float = 0.0, buffHPFlat: float = 0.0):
        if not self.MemoActive:
            return 0.70 * masterMaxHP
        return self.hpSnapshot * (1 + buffHPPercent) + buffHPFlat

    def getBaseStat(self, scaling: Scaling = None):
        scaling = scaling if scaling is not None else self.scaling
        if scaling == Scaling.HP:
            return (self.hpSnapshot if self.MemoActive else 0.0), 0.0, 0.0
        if scaling == Scaling.DEF:
            master = self.getMaster()
            return master.getBaseStat(Scaling.DEF) if master is not None else (0.0, 0.0, 0.0)
        return 0.0, 0.0, 0.0

    def spdOverride(self):
        if not self.MemoActive:
            return OFF_BAR_SPD
        if not self.ACT_OUTSIDE_FEVER and not self.feverActive():
            return OFF_BAR_SPD                                     # no turns outside Fever
        return None                                                # own SPD: baseSPD * (1 + SPD%) + flat

    def canUseUlt(self) -> bool:
        return False

    def addEnergy(self, amount: float):
        pass                                                       # no Energy bar

    def equip(self):
        self._mirrorGear()
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("SongbirdsRebuiltHarmonyCR", StatTypes.CR_PERCENT, 0.50, self.role))   # Rebuilt Harmony: +50% CRIT Rate
        return bl, dbl, al, dl, hl, sl

    # ------------------------------------------------------------ summon / leave
    def _summonBessie(self):
        bl, dbl, al, dl, tl = [], [], [], [], []
        master = self.getMaster()
        masterHP = self._masterOOCHP if self._masterOOCHP > 0 else master.maxHP
        self.hpSnapshot = 0.70 * masterHP
        self.members = 1
        self.MemoActive = True
        self.pendingDisappear = False
        self.recordedDMG = 0.0
        self.e4Bonus = 0.0
        self.baseSPD = 1.80 * master.baseSPD             # 1.8 x Robin's base SPD
        self._stopClock()
        self.maxHP = self.hpSnapshot
        self.currHP = self.maxHP                                   # a freshly summoned memosprite is at full HP
        bl.append(self._inheritedFlatSPDBuff())
        tl.append(self._energyTurn(master, 20, "SongbirdsMemberEnergy"))
        dbl.append(self._vulnDebuff())
        logger.info(f"{self.name}: Bessie summoned (Max HP {self.maxHP:.0f}, base SPD {self.baseSPD:.1f})")
        return bl, dbl, al, dl, tl

    def _checkJoins(self):
        out = ([], [], [], [], [])
        master = self.getMaster()
        JoinVibes = (6, 12)
        if master is None or not self.MemoActive:
            return out
        joined = False
        while self.members < 3 and getattr(master, "vibes", 0) >= JoinVibes[self.members - 1]:
            self.members += 1
            joined = True
            out[4].append(self._energyTurn(master, 20, "SongbirdsMemberEnergy"))
            logger.info(f"{self.name}: member {self.members} joined (Vibes {master.vibes})")
        if joined:
            out[1].append(self._vulnDebuff())
            if self.members >= 3 and not self.feverActive():
                self._merge(out, self._startFever(master))
        return out

    def _startFever(self, master):
        out = ([], [], [], [], [])
        if hasattr(master, "onFeverStart"):
            self._merge(out, master.onFeverStart())
        else:
            master.feverActive = True
        self.e4Bonus = (0.20 + 0.005 * master.vibes) if self._e() >= 4 else 0.0
        if self.e4Bonus > 0:
            out[0].append(Buff("SongbirdsE4SPD", StatTypes.SPD_PERCENT, self.e4Bonus, self.role, [AtkType.ALL], 1, 1,
                               Role.SELF, TickDown.PERM))
        out[0].append(self._inheritedFlatSPDBuff())
        # both clocks start now: a full gauge once spdAdjustment gives them their real SPD
        self.currSPD = OFF_BAR_SPD
        self.currAV = 10000.0 / OFF_BAR_SPD
        if self.countdown is not None:
            self.countdown.currSPD = OFF_BAR_SPD
            self.countdown.currAV = 10000.0 / OFF_BAR_SPD
        logger.info(f"{self.name}: FEVER (Vibes {master.vibes}, E4 SPD +{self.e4Bonus:.3f})")
        return out

    def _leave(self):
        out = ([], [], [], [], [])
        master = self.getMaster()
        wasFever = self.feverActive()
        self.members = 0
        self.MemoActive = False
        self.pendingDisappear = False
        self.recordedDMG = 0.0
        self.e4Bonus = 0.0
        self.hpSnapshot = 0.0
        self.currHP = self.maxHP
        self._stopClock()
        out[1].append(self._vulnDebuff(0))
        out[0].append(Buff("SongbirdsE4SPD", StatTypes.SPD_PERCENT, 0.0, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        if master is not None:
            if wasFever:
                if hasattr(master, "onFeverEnd"):
                    self._merge(out, master.onFeverEnd())
                else:
                    master.feverActive = False
            out[2].append(Advance("SongbirdsLeaveAdvance", master.role, 0.50))
        logger.info(f"{self.name}: left the field")
        return out

    def disappear(self):
        """Engine hook: the Songbirds were reduced to 0 HP."""
        bl, dbl, al, dl, tl, hl, sl = super().disappear()
        leave = self._leave()
        return bl + leave[0], dbl + leave[1], al + leave[2], dl + leave[3], tl + leave[4], hl, sl

    # ---------------------------------------------------------------- actions
    def useMemo(self, enemyID=-1):
        """The Songbirds' own turn: Chirrup Quartet (only taken in Fever)."""
        bl, dbl, al, dl, tl, hl, sl = super().useMemo(enemyID)
        master = self.getMaster()
        if not self.MemoActive or master is None or (not self.ACT_OUTSIDE_FEVER and not self.feverActive()):
            return bl, dbl, al, dl, tl, hl, sl
        e5Mul = 1.65 if self._e() >= 5 else 1.5
        e6Increase = 2.0 if self._e() == 6 else 1.0

        tl.append(Turn(self.name, self.role, -1, Targeting.AOE, [AtkType.MEMO], [self.element], [e5Mul * e6Increase, 0],
                       [10, 0], 0, self.scaling, 0, "SongbirdsChirrup"))

        tl.append(self._energyTurn(master, 20, "SongbirdsChirrupEnergy"))

        if self._e() >= 1 and self.recordedDMG > 0:
            tl.append(Turn(self.name, self.role, -1, Targeting.SINGLE, [AtkType.MEMO], [self.element],
                           [0.11 + 0.01 * master.vibes, 0], [0, 0], 0, self.scaling, 0,
                           "SongbirdsE1TrueDMG"))
        return bl, dbl, al, dl, tl, hl, sl

    def countdownTurn(self):
        bl, dbl, al, dl, tl, hl, sl = [], [], [], [], [], [], []
        master = self.getMaster()
        if not self.MemoActive or master is None or not self.feverActive():
            return bl, dbl, al, dl, tl, hl, sl

        if self._e() == 6:
            bl.append(Buff("SongbirdsE6Energy", StatTypes.ERR_F, 140, master.role, [AtkType.ALL], 1, 1, master.role, TickDown.END))

        before = master.vibes
        spent = min(before, max(math.ceil(before * 0.5), 12))
        master.vibes = before - spent
        logger.info(f"{self.name}: countdown turn, Vibes {before} -> {master.vibes}")

        if master.vibes <= 0:
            self._merge((bl, dbl, al, dl, tl), self._leave())
        return bl, dbl, al, dl, tl, hl, sl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().ownTurn(turn, result)
        if result.turnName == "SongbirdsE1TrueDMG":
            self.recordedDMG *= 0.5
        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)
        out = (bl, dbl, al, dl, tl)
        master = self.getMaster()
        fromMaster = result.charName == self.MemoSummonerName
        e3Mul = 1.1 if self._e() >= 3 else 1.0

        if result.turnName == "SongbirdsSpawn" and fromMaster and master is not None:
            if not self.MemoActive:
                self._merge(out, self._summonBessie())
            else:
                self.ChangeHpValue(e3Mul * self.maxHP)

        if self._e() >= 1 and self.MemoActive and result.turnName not in ("AeonAhaELATrueDMG", "SongbirdsE1TrueDMG"):
            dmg = getattr(result, "TotalDamage", None)
            if dmg is None:
                dmg = result.turnDmg + getattr(result, "ElationturnDMG", 0.0)
            if dmg > 0:
                self.recordedDMG += dmg

        self._merge(out, self._checkJoins())
        return bl, dbl, al, dl, tl, hl, sl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)
        out = (bl, dbl, al, dl, tl)
        self._masterOOCHP = specialRes.attr2 or 0.0
        self._masterPermFlatSPD = specialRes.attr3 or 0.0
        self._mirrorGear()
        master = self.getMaster()
        if self.MemoActive and master is not None:
            # inherit Robin's permanent stat buffs (CRIT / DMG% / ...): temporary buffs on Robin do not carry over
            for b in (specialRes.attr1 or []):
                bl.append(Buff(b.name, b.buffType, b.getBuffVal(), self.role, b.atkType, 1, 1, Role.SELF, TickDown.PERM, b.reqBroken))
            self.baseSPD = 1.80 * master.baseSPD
            bl.append(self._inheritedFlatSPDBuff())
            self._merge(out, self._checkJoins())
        return bl, dbl, al, dl, tl, hl, sl