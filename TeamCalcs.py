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
import logging
import math
import os

from Combat_Simulator import startSimulator
from MainFunctions import *
from Enemy import EnemyModule, EnemyType, FINITE_ENEMY_HP
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
OUTPUT_LOG = True      # set True to write a .log file for a single run (per-team, via Combat_Simulator)

# Anchored to this script's own directory (not the process's current working
# directory) so the log always lands next to TeamCalcs.py regardless of where
# the script is launched from (e.g. an IDE's "run" button often uses a
# different cwd than a terminal would).
LOG_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Output")

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


class _Tee:
    """Writes lines to both stdout and a log file.

    NOTE: this deliberately does NOT use Python's `logging` module.
    Combat_Simulator.py calls `logging.disable(logging.CRITICAL)` whenever
    startSimulator() runs with outputLog=False (which is every run in MULTI
    mode) — logging.disable() is a global, process-wide switch that stays
    in effect until something calls logging.disable(logging.NOTSET). That
    silently killed every logging.critical() call TeamCalcs made after the
    first simulation run. Writing directly to our own file sidesteps that
    entanglement entirely.
    """
    def __init__(self, filename: str):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.filename = os.path.abspath(filename)
        self._file = open(self.filename, "w", encoding="utf-8", buffering=1)  # line-buffered

    def log(self, msg: str = ""):
        print(msg)
        self._file.write(str(msg) + "\n")
        self._file.flush()
        os.fsync(self._file.fileno())

    def close(self):
        self._file.close()


def _log_filename(teams, cycles, num_runs=None, mode="SINGLE") -> str:
    teamInfo = f"{len(teams)}Teams"
    runsInfo = f"_{num_runs}Runs" if num_runs is not None else ""
    return f"{LOG_FOLDER}/TeamCalcs_{mode}_{teamInfo}_{cycles}Cycles{runsInfo}.log"


def _95_margin_of_error_pct(values: list, mean: float) -> float:
    """95% confidence-interval margin of error, expressed as a percent of the
    mean (i.e. 'the true mean is avg +/- X%' at 95% confidence).

    Uses the normal approximation (z = 1.96), which is standard for the
    sample sizes typical of these runs (n >= ~30). Returns 0.0 if there's
    no variance to measure (n < 2 or mean == 0).
    """
    n = len(values)
    if n < 2 or mean == 0:
        return 0.0
    mean_val = sum(values) / n
    variance = sum((v - mean_val) ** 2 for v in values) / (n - 1)  # sample variance
    stderr = math.sqrt(variance / n)
    margin = 1.96 * stderr
    return margin / mean * 100


def run_single(teams, cycles, enemy_module, output_log):
    """One run per team, in the order the teams were defined (no sorting)."""
    separator = "=" * 70
    tee = _Tee(_log_filename(teams, cycles, mode="SINGLE"))
    print(f"Logging to: {tee.filename}")

    try:
        tee.log(f"\n{separator}\n  SINGLE MODE  |  {cycles} cycles  |  {len(teams)} team(s)\n{separator}")

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
            tee.log(f"\n  {team['name']}")
            tee.log(f"  DPAV: {dpav:.3f}  |  {sp_info}")

        tee.log(f"\n{separator}\n")
    except Exception:
        import traceback
        tee.log("\n!!! ERROR during run_single — partial results above are still valid !!!")
        tee.log(traceback.format_exc())
        raise
    finally:
        tee.close()

    print(f"\nLog written to {tee.filename}")


def run_multi(teams, num_runs, cycles, enemy_module):
    """N runs per team, in the order the teams were defined (no sorting by DPAV).

    Reports mean DPAV and per-character breakdown, plus:
      - 95% confidence-interval margin of error on team DPAV (in percent)
      - average overkill DMG per enemy and total (when finite-HP mode is on)
      - each character's average damage distribution across their 3 highest
        AtkType damage categories (Basic/Skill/Ult/FUA/etc.)
    """
    av_limit = cycles * 100 + 50
    separator = "=" * 70
    tee = _Tee(_log_filename(teams, cycles, num_runs=num_runs, mode="MULTI"))

    print(f"Logging to: {tee.filename}")
    try:
        tee.log(f"\n{separator}\n  MULTI MODE  |  {num_runs} runs  |  {cycles} cycles  |  {len(teams)} team(s)\n{separator}")

        all_results = []

        for team in teams:
            team_dpavs = []
            char_dpavs = {}      # char_name -> list[float]
            char_dmg_dcts = {}   # char_name -> list[dict[AtkType, float]]  (one dmgDct snapshot per run)
            char_names = []

            enemy_overkills = []  # list[list[float]], one list of per-enemy overkill per run
            enemy_names = []
            enemy_types = []

            print(f"\n  Running: {team['name']} ...", end="", flush=True)

            for i in range(num_runs):
                s1, s2, s3, s4 = team["factory"]()
                slots = [s1, s2, s3, s4]

                # Collect char names on first run
                if i == 0:
                    char_names = [c.name for c in slots]
                    for n in char_names:
                        char_dpavs[n] = []
                        char_dmg_dcts[n] = []

                resultEnemies = []
                result = startSimulator(
                    cycleLimit=cycles,
                    s1=s1, s2=s2, s3=s3, s4=s4,
                    outputLog=False,
                    enemyModule=enemy_module,
                    resultEnemies=resultEnemies,
                )

                team_dpav = _parse_dpav(result)
                team_dpavs.append(team_dpav)

                for char in slots:
                    _, total_dmg = char.getTotalDMG()
                    char_dpavs[char.name].append(total_dmg / av_limit)
                    # dmgDct is per-instance state on Character; snapshot a copy since
                    # this character instance gets discarded after each run.
                    char_dmg_dcts[char.name].append(dict(char.dmgDct))

                if FINITE_ENEMY_HP and resultEnemies:
                    if i == 0:
                        enemy_names = [e.name for e in resultEnemies]
                        enemy_types = [e.enemyType.name for e in resultEnemies]
                    enemy_overkills.append([e.overkillDMG for e in resultEnemies])

                if (i + 1) % 20 == 0:
                    print(".", end="", flush=True)

            print(" done")

            avg_team = sum(team_dpavs) / num_runs
            min_team = min(team_dpavs)
            max_team = max(team_dpavs)
            moe_pct  = _95_margin_of_error_pct(team_dpavs, avg_team)

            # ── Top-3 AtkType damage distribution per character ────────────────
            char_top_types = {}  # char_name -> list[(AtkType, avg_dmg, pct_of_char_total)]
            for name in char_names:
                dcts = char_dmg_dcts[name]
                atk_types = dcts[0].keys() if dcts else []
                avg_by_type = {
                    t: sum(d.get(t, 0.0) for d in dcts) / num_runs
                    for t in atk_types
                }
                char_avg_total = sum(avg_by_type.values())
                ranked_types = sorted(avg_by_type.items(), key=lambda kv: kv[1], reverse=True)[:3]
                char_top_types[name] = [
                    (t, v, (v / char_avg_total * 100 if char_avg_total > 0 else 0.0))
                    for t, v in ranked_types
                ]

            # ── Overkill averages ────────────────────────────────────────────
            avg_overkill_per_enemy = []
            avg_overkill_total = 0.0
            if enemy_overkills:
                num_enemies = len(enemy_overkills[0])
                avg_overkill_per_enemy = [
                    sum(run[e] for run in enemy_overkills) / num_runs for e in range(num_enemies)
                ]
                avg_overkill_total = sum(avg_overkill_per_enemy)

            all_results.append({
                "name":                team["name"],
                "avg":                 avg_team,
                "min":                 min_team,
                "max":                 max_team,
                "moe_pct":             moe_pct,
                "char_names":          char_names,
                "char_dpavs":          char_dpavs,
                "char_top_types":      char_top_types,
                "enemy_names":         enemy_names,
                "enemy_types":         enemy_types,
                "avg_overkill_per_enemy": avg_overkill_per_enemy,
                "avg_overkill_total":  avg_overkill_total,
            })

        # ── Print / log summary ─────────────────────────────────────────────
        # NOTE: results are reported in the same order teams were defined in
        # TEAMS, not sorted by DPAV.
        tee.log(f"\n{separator}\n  RESULTS  ({num_runs} runs, {cycles} cycles)\n{separator}")

        for r in all_results:
            lines = [f"\n  {r['name']}"]
            lines.append(
                f"  Team DPAV  avg: {r['avg']:.3f}  |  min: {r['min']:.3f}  |  max: {r['max']:.3f}  "
                f"|  95% CI margin of error: +/-{r['moe_pct']:.2f}%"
            )
            for name in r["char_names"]:
                dpavs = r["char_dpavs"][name]
                avg_c = sum(dpavs) / num_runs
                pct   = avg_c / r["avg"] * 100 if r["avg"] > 0 else 0
                lines.append(f"    {name:<20} avg DPAV: {avg_c:.3f}  ({pct:.1f}%)")

                top_types = r["char_top_types"].get(name, [])
                for atk_type, avg_val, type_pct in top_types:
                    lines.append(f"      - {atk_type.name:<10} avg DMG: {avg_val:.3f}  ({type_pct:.1f}% of {name}'s DMG)")

            if FINITE_ENEMY_HP and r["avg_overkill_per_enemy"]:
                lines.append(f"  Avg Total Overkill DMG: {r['avg_overkill_total']:.1f}")
                for idx, avg_ok in enumerate(r["avg_overkill_per_enemy"]):
                    eName = r["enemy_names"][idx] if idx < len(r["enemy_names"]) else f"Enemy {idx}"
                    eType = r["enemy_types"][idx] if idx < len(r["enemy_types"]) else "?"
                    lines.append(f"    {eName} ({eType})  avg Overkill: {avg_ok:.1f}")
            elif not FINITE_ENEMY_HP:
                lines.append("  FINITE HP MODE: OFF (overkill not tracked)")

            tee.log("\n".join(lines))

        # ── Order (as defined, NOT sorted by DPAV) ──────────────────────────
        tee.log(f"\n{separator}\n  TEAM ORDER (as defined)\n{separator}")
        for i, r in enumerate(all_results, 1):
            tee.log(f"  #{i}  {r['avg']:.3f}  —  {r['name']}")

        tee.log(f"\n{separator}\n")
    except Exception:
        import traceback
        tee.log("\n!!! ERROR during run_multi — partial results above (if any) are still valid !!!")
        tee.log(traceback.format_exc())
        raise
    finally:
        tee.close()

    print(f"\nLog written to {tee.filename}")


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