from enum import Enum, auto

bonusDMG = {} # Will be for special types of damage, and things like additional damage
wbMultiplier = 3767.5533
eleDct = {"PHY": 2.0, "FIR": 2.0, "WIN": 1.5, "ICE": 1.0, "LNG": 1.0, "QUA": 0.5, "IMG": 0.5}
atkRatio_Elites = [0.5, 0.5, 0]
atkRatio_Bosses = [0, 0.5, 0.5]
atkRatio_Adds = [1, 0, 0]

class StatTypes(Enum):
    Spd = "Spd"
    HP = "HP"
    ATK = "ATK"
    DEF = "DEF"
    SPD_PERCENT = "SPD%"
    HP_PERCENT = "HP%"
    ATK_PERCENT = "ATK%"
    DEF_PERCENT = "DEF%"
    CR_PERCENT = "CR%"
    CD_PERCENT = "CD%"
    BE_PERCENT = "BE%"

    WB_EFF = "WBE%"
    BRK_DMG = "BRK_DMG%"
    SBRK_DMG = "SBRK_DMG%"
    OGH_PERCENT = "OGH%"
    ERR_PERCENT = "ERR%"
    EHR_PERCENT = "EHR%"
    ERS_PERCENT = "ERS%"
    DMG_PERCENT = "DMG%"
    SHRED = "SHRED"
    VULN = "VULN"
    PEN = "PEN"
    ERR_T = "ERR_T"
    ERR_F = "ERR_F"
    SKLPT = "SKILLPOINT"

    ICEPEN = "ICEPEN"
    FIRPEN = "FIRPEN"
    LNGPEN = "LNGPEN"
    WINPEN = "WINPEN"
    PHYPEN = "PHYPEN"
    QUAPEN = "QUAPEN"
    IMGPEN = "IMGPEN"

    ENTANGLE = "ENTANGLE"
    SHOCK = "SHOCK"
    WINDSHEAR = "WINDSHEAR"
    FREEZE = "FREEZE"
    BURN = "BURN"
    BLEED = "BLEED"

    TRUEDAMAGE = "TRUEDAMAGE"

class Element(Enum):
    WIND = "WIN"
    FIRE = "FIR"
    LIGHTNING = "LNG"
    IMAGINARY = "IMG"
    QUANTUM = "QUA"
    ICE = "ICE"
    PHYSICAL = "PHY"

class Path(Enum):
    HUNT = 3
    ERUDITION = 3
    HARMONY = 4
    NIHILITY = 4
    ABUNDANCE = 4
    REMEMBRANCE = 4
    MEM = 4
    DESTRUCTION = 5
    GARMENTMAKER = 5
    PRESERVATION = 6

class Role(Enum):
    DPS = auto()
    SUBDPS = auto()
    SUP1 = auto()
    SUP2 = auto()
    SUS = auto()
    MEMO = auto()
    ALL = auto()
    SELF = auto()
    TEAM = auto()  # everyone except the source of the buff
    ENEMY = auto()
    # Summon roles
    LIGHTNINGLORD = auto()
    NUMBY = auto()
    FUYUAN = auto()
    HENSHIN = auto()

class Scaling(Enum):
    ATK = "ATK%"
    HP = "HP%"
    DEF = "DEF%"

class TickDown(Enum):
    END = auto()
    START = auto()
    PERM = auto()

class Targeting(Enum):
    SINGLE = "ST"
    BLAST = "BLAST"
    AOE = "AOE"
    NA = "NA"
    SPECIAL = "SPECIAL"
    STBREAK = "STBREAK"
    BLASTBREAK = "BLASTBREAK"
    AOEBREAK = "AOEBREAK"
    STSB = "STSBREAK"
    BLASTSB = "BLASTSBREAK"
    AOESB = "AOESBREAK"
    DOT = "DOT"
    DEBUFF = "DEBUFF"

class AtkType(Enum):
    BSC = auto()
    SKL = auto()
    ULT = auto()
    FUA = auto()
    BRK = auto()
    SBK = auto()
    DOT = auto()
    MEMO = auto()
    ALL = auto()
    TECH = auto()
    SPECIAL = auto() # special attacks, only takes effect from "ALL"-type buffs
    # Special Buffs/AtkTypes
    DUKEFUA = auto()
    DUKEULT = auto()
    TOPAZULT = auto()
    TOPAZFUA = auto()
    UEBSC = auto() # Sword-7th
    EBSC = auto() # Sword-7th
    ESKILL = auto() # firefly
    HMCSBK = auto() # bonus superbreak dmg from hmc
    FUGUESBK = auto()

class EnemyType(Enum):
    ELITE = auto()
    BOSS = auto()
    ADD = auto()

class Priority(Enum):
    DEFAULT = auto()
    BREAKER = auto()
    BROKEN = auto()
    MIDDLE = auto()

penDct = {Element.PHYSICAL: StatTypes.PHYPEN, Element.FIRE: StatTypes.FIRPEN, Element.WIND: StatTypes.WINPEN, Element.ICE: StatTypes.ICEPEN, Element.QUANTUM: StatTypes.QUAPEN, Element.LIGHTNING: StatTypes.LNGPEN, Element.IMAGINARY: StatTypes.IMGPEN}
