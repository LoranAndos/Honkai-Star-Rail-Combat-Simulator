import logging

from Buff import *
from Character import Character
from Delay_Text import *
from Lightcones.Resolution import ResolutionPela
from Planars.Keel import Keel
from RelicStats import RelicStats
from Relics.Longevous import Longevous
from Relics.Messenger import Messenger
from Result import Special
from Turn_Text import Turn

logger = logging.getLogger(__name__)


class Pela(Character):
    # Standard Character Settings
    name = "Pela"
    path = Path.NIHILITY
    element = Element.ICE
    scaling = Scaling.ATK
    baseHP = 987.8
    baseATK = 546.84
    baseDEF = 463.05
    baseSPD = 105
    maxEnergy = 110
    currEnergy = 55
    ultCost = 110
    currAV = 0
    dmgDct = {AtkType.BSC: 0, AtkType.SKL: 0, AtkType.ULT: 0, AtkType.BRK: 0}  # Adjust accordingly

    # Unique Character Properties

    # Relic Settings
    # First 12 entries are sub rolls: SPD, HP, ATK, DEF, HP%, ATK%, DEF%, BE%, EHR%, RES%, CR%, CD%
    # Last 4 entries are main stats: Body, Boots, Sphere, Rope

    def __init__(self, pos: int, role: Role, defaultTarget: int = -1, lc=None, r1=None, r2=None, pl=None, subs=None,
                 eidolon=6, rotation=None, targetPrio=Priority.DEFAULT) -> None:
        super().__init__(pos, role, defaultTarget, eidolon, targetPrio)
        self.lightcone = lc if lc else ResolutionPela(role, 5)
        self.relic1 = r1 if r1 else Longevous(role, 2)
        self.relic2 = None if self.relic1.setType == 4 else (r2 if r2 else Messenger(role, 2, False))
        self.planar = pl if pl else Keel(role)
        self.relicStats = subs if subs else RelicStats(14, 2, 0, 2, 4, 0, 4, 4, 10, 8, 0, 0, StatTypes.HP_PERCENT, StatTypes.Spd,
                                                       StatTypes.DEF_PERCENT, StatTypes.ERR_PERCENT)
        self.rotation = rotation if rotation else ["E", "A"]

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("PelaTraceEHR", StatTypes.ERR_PERCENT, 0.1, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("PelaTraceDMG", StatTypes.DMG_PERCENT, 0.224, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("PelaTraceATK", StatTypes.ATK_PERCENT, 0.18, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("PelaTeamEHR", StatTypes.ERR_PERCENT, 0.1, Role.ALL, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("PelaDebuffBonusDMG", StatTypes.DMG_PERCENT, 0.2, self.role, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useBsc(enemyID)
        e3Mul = 1.1 if self.eidolon >= 3 else 1.0
        e5ERR = 11 if self.eidolon >= 5 else 10
        e6Bonus = 0.4 if self.eidolon == 6 else 0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.BSC], [self.element],[e3Mul + e6Bonus, 0], [10, 0], 20, self.scaling, 1, "PelaBasic"))  # bonus 0.4 from e6
        if self.lightcone.name == "Resolution Shines as Pearls of Sweat":
            tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.NA, [AtkType.ALL], [self.element], [0, 0],[0, 0], e5ERR, self.scaling, 0, "PelaTalentERR"))
        return bl, dbl, al, dl, tl, hl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useSkl(enemyID)
        e3Mul = 2.31 if self.eidolon >= 3 else 2.1
        e5ERR = 11 if self.eidolon >= 5 else 10
        e6Bonus = 0.4 if self.eidolon == 6 else 0
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.SINGLE, [AtkType.SKL], [self.element],[e3Mul + e6Bonus, 0], [20, 0], 30, self.scaling, -1, "PelaSkill"))  # bonus 0.4 from e6
        tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], e5ERR,self.scaling, 0, "PelaTalentERR"))
        if self.eidolon >= 4:
            dbl.append(Debuff("PelaIceRes", self.role, StatTypes.ICEPEN, 0.12, self.bestEnemy(enemyID), [AtkType.ALL], 2))  # e4
        return bl, dbl, al, dl, tl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, tl, hl = super().useUlt(enemyID)
        e5ERR = 11 if self.eidolon >= 5 else 10
        e5DmgMUL = 1.08 if self.eidolon >= 5 else 1.0
        e5Shred = 0.42 if self.eidolon >= 5 else 0.4
        e6Bonus = 0.4 if self.eidolon == 6 else 0
        self.currEnergy = self.currEnergy - self.ultCost
        tl.append(Turn(self.name, self.role, self.bestEnemy(enemyID), Targeting.AOE, [AtkType.ULT], [self.element],[e5DmgMUL + e6Bonus, 0], [10, 0], 5, self.scaling, 0, "PelaUlt"))  # bonus 0.4 from e6
        tl.append(Turn(self.name, self.role, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], e5ERR,self.scaling, 0, "PelaTalentERR"))
        dbl.append(Debuff("PelaUltShred", self.role, StatTypes.SHRED, e5Shred, Role.ALL, [AtkType.ALL], 2, 1, False, [0, 0], False))
        return bl, dbl, al, dl, tl, hl