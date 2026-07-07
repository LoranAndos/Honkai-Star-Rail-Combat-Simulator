"""
TeamBenchmark.py
================
Define multiple teams below, each with their own builds, then run either:
  - SINGLE mode: one sim run per team, results printed immediately
  - MULTI  mode: N runs per team, prints average + per-char DPAV breakdown

Toggle between modes and configure runs at the top of the SETTINGS section.
"""

# ============================================================
# ── IMPORTS ─────────────────────────────────────────────────
# ============================================================
from Combat_Simulator import startSimulator
from MainFunctions import *
from Enemy import EnemyModule, EnemyType
from Attributes import *
from RelicStats import RelicStats
import Lightcones

# Import character/lightcone/relic/planar modules
# Adjust paths to match your project layout
from Characters.Abundance.HuoHuo import HuoHuo
from Characters.Abundance.Lingsha import Lingsha
from Characters.Destruction.Saber import Saber
from Characters.Destruction.Gilgamesh import Gilgamesh
from Characters.Harmony.RuanMei import RuanMei
from Characters.Harmony.Tribbie import Tribbie
from Characters.Harmony.Robin import Robin
from Characters.Nihility.MortenaxBlade import MortenaxBlade
# ... add more imports as needed


# ============================================================
# ── SETTINGS ────────────────────────────────────────────────
# ============================================================

MODE       = "MULTI"   # "SINGLE" or "MULTI"
NUM_RUNS   = 100        # only used in MULTI mode
CYCLES     = 5          # cycle limit for every run
OUTPUT_LOG = True      # set True to write a .log file for a single run

# Enemy setup — shared across all teams
ENEMY_MODULE = EnemyModule(
    3,
    [95, 95, 95],
    [EnemyType.ELITE, EnemyType.BOSS, EnemyType.ELITE],
    [130, 158.4, 130],
    [100, 160, 100],
    atkRatio,
    [Element.WIND],
    [1],
)


# ============================================================
# ── TEAM DEFINITIONS ────────────────────────────────────────
# Each team is a dict with:
#   "name"    : label printed in results
#   "factory" : zero-argument callable that returns (s1, s2, s3, s4)
#               Build characters fresh here — relics/LCs go inside.
# ============================================================

def team_Saber_Gilgamesh_MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_Tribbie_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, eidolon=0)
    s3 = Tribbie(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_RuanMei_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, eidolon=0)
    s3 = RuanMei(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_E1RuanMei_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, eidolon=0)
    s3 = RuanMei(2, Role.SUP2, 1, eidolon=1)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_Robin_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, eidolon=0)
    s3 = Robin(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_MortenaxBlade_Lingsha():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = Lingsha(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_MortenaxBlade_E1s1Lingsha():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = Lingsha(3, Role.SUS,   1, lc=Lightcones.Abundance.ScentAloneStaysTrue.ScentAloneStaysTrueLingsha(Role.SUS,1),eidolon=1)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_e0s1MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, lc=Lightcones.Destruction.IAmAsYouBehold.IAmAsYouBehold(Role.SUP1,1), eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_e1s0MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, eidolon=1)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_e1s1MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, lc=Lightcones.Destruction.IAmAsYouBehold.IAmAsYouBehold(Role.SUP1,1), eidolon=1)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_e2s0MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, eidolon=2)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_e2s1MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, lc=Lightcones.Destruction.IAmAsYouBehold.IAmAsYouBehold(Role.SUP1,1), eidolon=2)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_e3s1MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, lc=Lightcones.Destruction.IAmAsYouBehold.IAmAsYouBehold(Role.SUP1,1), eidolon=3)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_e4s1MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, lc=Lightcones.Destruction.IAmAsYouBehold.IAmAsYouBehold(Role.SUP1,1), eidolon=4)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_e5s1MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, lc=Lightcones.Destruction.IAmAsYouBehold.IAmAsYouBehold(Role.SUP1,1), eidolon=5)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_e6s1MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, lc=Lightcones.Destruction.IAmAsYouBehold.IAmAsYouBehold(Role.SUP1,1), eidolon=6)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgameshs1BygoneBlood_MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, lc=Lightcones.Destruction.ATrailOfBygoneBlood.ATrailOfBygoneBlood(Role.SUP1,1) ,eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgameshs5BygoneBlood_MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, lc=Lightcones.Destruction.ATrailOfBygoneBlood.ATrailOfBygoneBlood(Role.SUP1,5) ,eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgameshs5SecretVow_MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, lc=Lightcones.Destruction.ASecretVow.ASecretVow(Role.SUP1,5) ,eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_e0s0Saber_Gilgamesh_MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, lc=Lightcones.Destruction.ASecretVow.ASecretVow(Role.DPS,5) , eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_e1s0Saber_Gilgamesh_MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, lc=Lightcones.Destruction.ASecretVow.ASecretVow(Role.DPS,5) , eidolon=1)
    s2 = Gilgamesh(1, Role.SUP1, 1, eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_e1s1Saber_Gilgamesh_MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=1)
    s2 = Gilgamesh(1, Role.SUP1, 1, eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_e2s0Saber_Gilgamesh_MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, lc=Lightcones.Destruction.ASecretVow.ASecretVow(Role.DPS,5) , eidolon=2)
    s2 = Gilgamesh(1, Role.SUP1, 1, eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_e2s1Saber_Gilgamesh_MortenaxBlade_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=2)
    s2 = Gilgamesh(1, Role.SUP1, 1, eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_MortenaxBladee0s1_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1,eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, lc=Lightcones.Nihility.ReforgedInHellfire.ReforgedInHellfire(Role.SUP2,1), eidolon=0)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_MortenaxBladee1s0_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=1)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_MortenaxBladee1s1_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1, eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, lc=Lightcones.Nihility.ReforgedInHellfire.ReforgedInHellfire(Role.SUP2,1), eidolon=1)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_MortenaxBladee2s0_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1,eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, eidolon=2)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4

def team_Saber_Gilgamesh_MortenaxBladee2s1_Huohuo():
    """Archer / Sparkle / Ruan Mei / Huo Huo — standard hunt team"""

    s1 = Saber(0, Role.DPS,   1, eidolon=0)
    s2 = Gilgamesh(1, Role.SUP1, 1,eidolon=0)
    s3 = MortenaxBlade(2, Role.SUP2, 1, lc=Lightcones.Nihility.ReforgedInHellfire.ReforgedInHellfire(Role.SUP2,1),eidolon=2)
    s4 = HuoHuo(3, Role.SUS,   1, eidolon=0)
    return s1, s2, s3, s4


# ── Register teams here ──────────────────────────────────────
TEAMS = [
    {"name": "Saber E0 | Gilgamesh | MortenaxBlade | Huo Huo", "factory": team_Saber_Gilgamesh_MortenaxBlade_Huohuo},
    {"name": "Saber E0 | Gilgamesh | Tribbie | Huo Huo", "factory": team_Saber_Gilgamesh_Tribbie_Huohuo},
    {"name": "Saber E0 | Gilgamesh | Ruan Mei | Huo Huo", "factory": team_Saber_Gilgamesh_RuanMei_Huohuo},
    {"name": "Saber E0 | Gilgamesh | Ruan Mei e1 | Huo Huo", "factory": team_Saber_Gilgamesh_E1RuanMei_Huohuo},
    {"name": "Saber E0 | Gilgamesh | Robin | Huo Huo", "factory": team_Saber_Gilgamesh_Robin_Huohuo},
    {"name": "Saber E0 | Gilgamesh | MortenaxBlade | Lingsha e0s0", "factory": team_Saber_Gilgamesh_MortenaxBlade_Lingsha},
    {"name": "Saber E0 | Gilgamesh | MortenaxBlade | Lingsha e1s1", "factory": team_Saber_Gilgamesh_MortenaxBlade_E1s1Lingsha},
    {"name": "Saber E0 | Gilgamesh e0s1 | MortenaxBlade | Huo Huo", "factory": team_Saber_Gilgamesh_e0s1MortenaxBlade_Huohuo},
    {"name": "Saber E0 | Gilgamesh e1s0 | MortenaxBlade | Huo Huo", "factory": team_Saber_Gilgamesh_e1s0MortenaxBlade_Huohuo},
    {"name": "Saber E0 | Gilgamesh e1s1 | MortenaxBlade | Huo Huo", "factory": team_Saber_Gilgamesh_e1s1MortenaxBlade_Huohuo},
    {"name": "Saber E0 | Gilgamesh e2s0 | MortenaxBlade | Huo Huo", "factory": team_Saber_Gilgamesh_e2s0MortenaxBlade_Huohuo},
    {"name": "Saber E0 | Gilgamesh e2s1 | MortenaxBlade | Huo Huo", "factory": team_Saber_Gilgamesh_e2s1MortenaxBlade_Huohuo},
    {"name": "Saber E0 | Gilgamesh e3s1 | MortenaxBlade | Huo Huo", "factory": team_Saber_Gilgamesh_e3s1MortenaxBlade_Huohuo},
    {"name": "Saber E0 | Gilgamesh e4s1 | MortenaxBlade | Huo Huo", "factory": team_Saber_Gilgamesh_e4s1MortenaxBlade_Huohuo},
    {"name": "Saber E0 | Gilgamesh e5s1 | MortenaxBlade | Huo Huo", "factory": team_Saber_Gilgamesh_e5s1MortenaxBlade_Huohuo},
    {"name": "Saber E0 | Gilgamesh e6s1 | MortenaxBlade | Huo Huo", "factory": team_Saber_Gilgamesh_e6s1MortenaxBlade_Huohuo},
    {"name": "Saber e0s0 | Gilgamesh | MortenaxBlade | Huo Huo", "factory": team_e0s0Saber_Gilgamesh_MortenaxBlade_Huohuo},
    {"name": "Saber e1s0 | Gilgamesh | MortenaxBlade | Huo Huo", "factory": team_e1s0Saber_Gilgamesh_MortenaxBlade_Huohuo},
    {"name": "Saber e1s1 | Gilgamesh | MortenaxBlade | Huo Huo", "factory": team_e1s1Saber_Gilgamesh_MortenaxBlade_Huohuo},
    {"name": "Saber e2s0 | Gilgamesh | MortenaxBlade | Huo Huo", "factory": team_e2s0Saber_Gilgamesh_MortenaxBlade_Huohuo},
    {"name": "Saber e2s1 | Gilgamesh | MortenaxBlade | Huo Huo", "factory": team_e2s1Saber_Gilgamesh_MortenaxBlade_Huohuo},
    {"name": "Saber E0 | Gilgamesh | MortenaxBlade e0s1 | Huo Huo", "factory": team_Saber_Gilgamesh_MortenaxBladee0s1_Huohuo},
    {"name": "Saber E0 | Gilgamesh | MortenaxBlade e1s0 | Huo Huo", "factory": team_Saber_Gilgamesh_MortenaxBladee1s0_Huohuo},
    {"name": "Saber E0 | Gilgamesh | MortenaxBlade e1s1 | Huo Huo", "factory": team_Saber_Gilgamesh_MortenaxBladee1s1_Huohuo},
    {"name": "Saber E0 | Gilgamesh | MortenaxBlade e2s0 | Huo Huo", "factory": team_Saber_Gilgamesh_MortenaxBladee2s0_Huohuo},
    {"name": "Saber E0 | Gilgamesh | MortenaxBlade e2s1 | Huo Huo", "factory": team_Saber_Gilgamesh_MortenaxBladee2s1_Huohuo},
    # Add more teams here:
    # {"name": "My Team 3", "factory": team_my_team_3},
]


# ============================================================
# ── RUNNER ──────────────────────────────────────────────────
# ============================================================

def _parse_dpav(result_str: str) -> float:
    """Extract the DPAV float from startSimulator's return string."""
    return float(result_str.split("DPAV: ")[1].split(" |")[0])


def run_single(teams, cycles, enemy_module, output_log):
    """One run per team."""
    separator = "=" * 70
    print(f"\n{separator}")
    print(f"  SINGLE MODE  |  {cycles} cycles  |  {len(teams)} team(s)")
    print(separator)

    for team in teams:
        s1, s2, s3, s4 = team["factory"]()
        result = startSimulator(
            cycleLimit=cycles,
            s1=s1, s2=s2, s3=s3, s4=s4,
            outputLog=output_log,
            enemyModule=enemy_module,
        )
        dpav = _parse_dpav(result)
        sp_info = " | ".join(result.split(" | ")[1:])  # SP Used / SP Gain
        print(f"\n  {team['name']}")
        print(f"  DPAV: {dpav:.3f}  |  {sp_info}")

    print(f"\n{separator}\n")


def run_multi(teams, num_runs, cycles, enemy_module):
    """N runs per team, reports mean DPAV and per-character breakdown."""
    av_limit = cycles * 100 + 50
    separator = "=" * 70

    print(f"\n{separator}")
    print(f"  MULTI MODE  |  {num_runs} runs  |  {cycles} cycles  |  {len(teams)} team(s)")
    print(separator)

    all_results = []

    for team in teams:
        team_dpavs = []
        char_dpavs = {}   # char_name -> list[float]
        char_names = []

        print(f"\n  Running: {team['name']} ...", end="", flush=True)

        for i in range(num_runs):
            s1, s2, s3, s4 = team["factory"]()
            slots = [s1, s2, s3, s4]

            # Collect char names on first run
            if i == 0:
                char_names = [c.name for c in slots]
                for n in char_names:
                    char_dpavs[n] = []

            result = startSimulator(
                cycleLimit=cycles,
                s1=s1, s2=s2, s3=s3, s4=s4,
                outputLog=False,
                enemyModule=enemy_module,
            )

            team_dpav = _parse_dpav(result)
            team_dpavs.append(team_dpav)

            for char in slots:
                _, total_dmg = char.getTotalDMG()
                char_dpavs[char.name].append(total_dmg / av_limit)

            if (i + 1) % 20 == 0:
                print(".", end="", flush=True)

        print(" done")

        avg_team  = sum(team_dpavs) / num_runs
        min_team  = min(team_dpavs)
        max_team  = max(team_dpavs)

        all_results.append({
            "name":       team["name"],
            "avg":        avg_team,
            "min":        min_team,
            "max":        max_team,
            "char_names": char_names,
            "char_dpavs": char_dpavs,
        })

    # ── Print summary ────────────────────────────────────────
    print(f"\n{separator}")
    print(f"  RESULTS  ({num_runs} runs, {cycles} cycles)")
    print(separator)

    for r in all_results:
        print(f"\n  {r['name']}")
        print(f"  Team DPAV  avg: {r['avg']:.3f}  |  min: {r['min']:.3f}  |  max: {r['max']:.3f}")
        for name in r["char_names"]:
            dpavs  = r["char_dpavs"][name]
            avg_c  = sum(dpavs) / num_runs
            pct    = avg_c / r["avg"] * 100 if r["avg"] > 0 else 0
            print(f"    {name:<20} avg DPAV: {avg_c:.3f}  ({pct:.1f}%)")

    # ── Ranking ──────────────────────────────────────────────
    ranked = sorted(all_results, key=lambda x: x["avg"], reverse=True)
    print(f"\n{separator}")
    print("  RANKING")
    print(separator)
    for i, r in enumerate(ranked, 1):
        diff = r["avg"] - ranked[0]["avg"]
        diff_str = "" if i == 1 else f"  ({diff:+.3f})"
        print(f"  #{i}  {r['avg']:.3f}{diff_str}  —  {r['name']}")

    print(f"\n{separator}\n")


# ============================================================
# ── ENTRY POINT ─────────────────────────────────────────────
# ============================================================

if __name__ == "__main__":
    if MODE == "SINGLE":
        run_single(TEAMS, CYCLES, ENEMY_MODULE, OUTPUT_LOG)
    elif MODE == "MULTI":
        run_multi(TEAMS, NUM_RUNS, CYCLES, ENEMY_MODULE)
    else:
        raise ValueError(f"Unknown MODE: '{MODE}'. Use 'SINGLE' or 'MULTI'.")