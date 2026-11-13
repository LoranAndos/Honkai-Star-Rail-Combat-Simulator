from Lightcones.Hunt.CruisingInTheStellarSea import CruisingInTheStellarSea
from Relics.ScholarLostInErudition import ScholarLostInErudition
from Planars.RutilantArena import RutilantArena
from Buff import *
from Memosprite import Memosprite
from Character import *
from Delay_Text import *
from RelicStats import RelicStats
from Result import *
from Turn_Text import Turn
from Healing import *

logger = logging.getLogger(__name__)

class SummerSongbirds(Memosprite):
    # Standard Character Properties
    name = "SummerSongbirds"
    element = Element.WIND
    scaling = Scaling.HP
    MemoSummonerName = "RobinSummeretto"
    baseHP = 1047.8
    baseATK = 543.31
    baseDEF = 630.63
    baseSPD = 0.0001
    maxEnergy = 100
    EnergyCost = 100
    currEnergy = 0
    currAV = 100.0
    aggro = 100
    MemoActive = False
    rotation = ["MEMO"]
    removeOnDisappear = ("MemCdBuff",)

    # Unique Character Properties
    specialEnergy = True             # Mem's "Energy" is Charge: it never receives normal energy / ERR
    hasMemosprite = False

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc = None, r1 = None, r2 = None, pl = None, subs = None, MemTarget = None, eidolon = 6, targetPrio = Priority.BROKEN, rotation = None) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else CruisingInTheStellarSea(self.role)
        self.relic1 = r1 if r1 else ScholarLostInErudition(self.role,4)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else None)
        self.planar = pl if pl else RutilantArena(self.role)
        self.relicStats = subs if subs else RelicStats(0, 2, 2, 2, 2, 11, 2, 2, 2, 2, 5, 12, StatTypes.CR_PERCENT, StatTypes.ERR_PERCENT,
                                                       StatTypes.DMG_PERCENT, StatTypes.ATK_PERCENT)
        self.MemTarget = MemTarget if MemTarget else Role.DPS
        self.rotation = rotation if rotation else ["MEMO"]
        # per-instance state (class-level lists/flags would be shared between runs)
        self.MemoActive = False
        self.firstSummon = True              # A2: the first summon gives +40% extra Charge
        self.MemospriteSupport = False       # next action is Lemme! Help You!
        self.MasterRole = Role.SUP1          # overwritten every turn from handleSpec (the memomaster's real role)
        self.cdStat = 0.0
        self.cdBuffVal = 0.0
        self.TargetMaxEnergy = 0.0           # Max Energy of the Support target (0 for characters without Energy)
        self.TargetMemoRoles = []            # roles of the Support target's own memosprites
        self.TargetZeroEnergy = False        # the Support target has 0 Max Energy (E4)
        self.SpecialEnergyCharacter = []     # names of the characters with 0 Max Energy

    # ------------------------------------------------------------------ stats
    def getSPD(self) -> float:
        # Mem's SPD is fixed (130 on the field); substat/relic SPD from the placeholder gear must not leak in.
        return 0.0

    def equip(self):  # function to add base buffs to wearer
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("RmcTraceCD", StatTypes.CD_PERCENT, 0.373, self.role))
        bl.append(Buff("RmcTraceATK", StatTypes.ATK_PERCENT, 0.14, self.role))
        bl.append(Buff("RmcTraceHP", StatTypes.HP_PERCENT, 0.14, self.role))
        return bl, dbl, al, dl, hl, sl

    def addCharge(self, amount: float):
        self.currEnergy = min(self.maxEnergy, self.currEnergy + amount)

    def canUseUlt(self) -> bool:
        # Reaching 100% Charge only matters while Mem is actually on the field.
        return self.MemoActive and not self.pendingDisappear and self.currEnergy >= self.EnergyCost

    # ----------------------------------------------------------------- summon
    def _summon(self):
        self.MemoActive = True
        self.pendingDisappear = False
        self.MemospriteSupport = False
        self.baseSPD = 130
        self.currAV = 10000 / self.currSPD       # currSPD is 1 while off-field; spdAdjustment rescales it to 10000/130
        self.currHP = self.maxHP                 # a freshly summoned memosprite is at full HP
        self.currEnergy = 0
        self.addCharge(50)                       # Go, Mem, Go!
        if self.firstSummon:
            self.addCharge(40)                   # A2: extra Charge on the first summon only
            self.firstSummon = False

    def disappear(self):
        bl, dbl, al, dl, tl, hl, sl = super().disappear()
        self.MemospriteSupport = False
        self.currEnergy = 0
        self.baseSPD = 1
        self.currSPD = 1
        self.currAV = 10000.0
        self.currHP = self.maxHP                 # off-field Mem is shown at full HP so "lowest HP ally" logic ignores it
        self.cdBuffVal = 0.0
        # No... Regrets: when Mem disappears Rmc's action is advanced by 25%
        al.append(Advance("MemDisappearAdvance", self.MasterRole, 0.25))
        return bl, dbl, al, dl, tl, hl, sl

    # ---------------------------------------------------------------- actions
    def useMemo(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl, sl = super().useMemo(enemyID)
        if not self.MemoActive:
            return bl, dbl, al, dl, tl, hl, sl
        if not self.MemospriteSupport:
            # Baddies! Trouble!: 4 hits, each on a random enemy + 1 AoE hit
            if self.eidolon >= 5:
                smallMul, bigMul = 0.396, 0.99
            else:
                smallMul, bigMul = 0.36, 0.90
            for _ in range(4):
                tl.append(Turn(self.name, self.role, -1, Targeting.RANDOM, [AtkType.MEMO], [self.element],
                               [smallMul, 0], [5, 0], 0, self.scaling, 0, "MemSkill"))
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.AOE, [AtkType.MEMO], [self.element],
                           [bigMul, 0], [10, 0], 0, self.scaling, 0, "MemBigSkill"))
        else:
            # Lemme! Help You!: advance one ally 100% and grant "Mem's Support" (True DMG) for 3 turns
            target = self.MemTarget
            baseTrue = 0.30 if self.eidolon >= 5 else 0.28
            a6 = min(0.20, max(0.0, (self.TargetMaxEnergy - 100) / 10 * 0.02))      # A6: +2% per 10 Max Energy above 100
            e4 = 0.06 if (self.eidolon >= 4 and self.TargetZeroEnergy) else 0.0       # E4: +6% on 0-Max-Energy allies
            trueDmg = baseTrue + a6 + e4
            if target != self.MasterRole:       # Mem cannot Support its own memomaster
                for r in [target] + list(self.TargetMemoRoles):
                    bl.append(Buff("MemSupport", StatTypes.TRUEDAMAGE, trueDmg, r, [AtkType.ALL], 3, 1, tickDown=r, tdType=TickDown.END))
                    if self.eidolon >= 1:
                        bl.append(Buff("MemCRSupport", StatTypes.CR_PERCENT, 0.1, r, [AtkType.ALL], 3, 1, tickDown=r, tdType=TickDown.END))
                al.append(Advance("MemSupportAdvance", target, 1))
            # a Turn is needed so that Rmc sees the Memosprite skill (it gives her 10 Energy)
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.NA, [AtkType.SPECIAL], [self.element],
                           [0, 0], [0, 0], 0, self.scaling, 0, "MemSupport"))
            self.MemospriteSupport = False
        return bl, dbl, al, dl, tl, hl, sl

    def useUlt(self, enemyID=-1):
        # "Ultimate" = reaching 100% Charge: Mem acts immediately and its next action is Lemme! Help You!
        bl, dbl, al, dl, tl, hl, sl = super().useUlt(enemyID)
        if self.MemoActive:
            self.currEnergy = self.currEnergy - self.EnergyCost
            al.append(Advance("MemUltAdvance", self.role, 1))
            self.MemospriteSupport = True
        return bl, dbl, al, dl, tl, hl, sl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().ownTurn(turn, result)
        if result.turnName == "MemBigSkill":
            self.addCharge(5)                    # A4: +5% Charge per Baddies! Trouble!
        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)
        wasActive = self.MemoActive
        fromMaster = result.charName == self.MemoSummonerName
        if result.turnName == "MemSpawn" and fromMaster:
            if not self.MemoActive:
                self._summon()                   # Rmc's Skill summons Mem
            else:
                heal = 0.66 if self.eidolon >= 3 else 0.60
                self.ChangeHpValue(heal * self.maxHP)      # Rmc's Skill on an existing Mem: heal + 10% Charge
                self.addCharge(10)
        elif result.turnName == "RmcUltimate" and fromMaster:
            if not self.MemoActive:
                self._summon()                   # the Ultimate summons Mem if absent
            self.addCharge(40)
            mul = 2.64 if self.eidolon >= 5 else 2.4
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID=-1), Targeting.AOE, [AtkType.MEMO, AtkType.ULT], [self.element],
                           [mul, 0], [20, 0], 0, self.scaling, 0, "MemUltimate"))
            if self.eidolon == 6:
                bl.append(Buff("MemE6CRBuff", StatTypes.CR_PERCENT, 1.00, self.role, [AtkType.ULT], 1, 1, Role.SELF, TickDown.PERM))
        # +1% Charge per 10 Energy regenerated by allies (only if Mem was already out; characters without Energy excluded)
        if wasActive and result.errGain > 0 and result.charName != self.name and result.charName not in self.SpecialEnergyCharacter:
            self.addCharge(result.errGain / 10)
        return bl, dbl, al, dl, tl, hl, sl

    def handleSpecialStart(self, specialRes: Special):
        bl, dbl, al, dl, tl, hl, sl = super().handleSpecialStart(specialRes)
        self.MasterRole = specialRes.attr2
        self.TargetMaxEnergy = specialRes.attr4
        self.TargetMemoRoles = specialRes.attr5
        self.SpecialEnergyCharacter = specialRes.attr6
        self.TargetZeroEnergy = specialRes.attr7
        actorName = specialRes.attr8
        # Mem's CRIT DMG without the Friends! Together! buff it gives itself (avoids feeding back into itself)
        self.cdStat = specialRes.attr3 - (self.cdBuffVal if self.MemoActive else 0.0)
        if self.MemoActive:
            # inherit the memomaster's permanent stat buffs (temporary buffs on the master do not carry over)
            for b in specialRes.attr1:
                bl.append(Buff(b.name, b.buffType, b.getBuffVal(), self.role, b.atkType, 1, 1, Role.SELF, TickDown.PERM, b.reqBroken))
            # E4: an ally with 0 Max Energy acts -> Mem gains 3% Charge
            if self.eidolon >= 4 and actorName in self.SpecialEnergyCharacter:
                self.addCharge(3)
            # Friends! Together!: all allies' CRIT DMG scales with Mem's CRIT DMG while Mem is on the field
            if self.eidolon >= 3:
                self.cdBuffVal = self.cdStat * 0.132 + 0.264
            else:
                self.cdBuffVal = self.cdStat * 0.12 + 0.24
            bl.append(Buff("MemCdBuff", StatTypes.CD_PERCENT, self.cdBuffVal, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, tl, hl, sl