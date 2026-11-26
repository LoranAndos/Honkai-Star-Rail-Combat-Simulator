"""
BattleSheet.py
==============
Turns Combat_Simulator logs into an Excel workbook with one tab per team:

    build blocks (relic/planar/lightcone, main stats, sub rolls, final stats at battle start)
    + the whole battle, one row per unit turn, with the individual hits underneath each turn
      (collapsed row groups) and every buff / debuff that applied to every hit.

Usage from code (this is what TeamCalcs.py does):

    from BattleSheet import build_battle_workbook
    build_battle_workbook([(1, "Team name", "Output/team1.log"), ...], "TeamCalcs_BattleSheets.xlsx")

Usage from the command line:

    python BattleSheet.py out.xlsx first.log second.log ...        (tab names come from the file names)

The log must have been written by Combat_Simulator with outputLog=True (DEBUG level, so that the
buff lists are in it). Logs that predate the BUILD section still convert; the build blocks then
only show what the old "Player Team" header contained (gear names, no stats).

Requires:  pip install xlsxwriter
"""
import ast
import os
import re
import sys
from collections import OrderedDict, defaultdict


# ════════════════════════════════════════════════════════════════════════════════════════════
#  PART 1 — PARSER
# ════════════════════════════════════════════════════════════════════════════════════════════

class Buff:
    __slots__ = ("name", "stat", "stacks", "value", "turns", "tick", "target", "affects")

    def __init__(self, name, stat, stacks, value, turns, tick, target, affects):
        self.name, self.stat, self.stacks, self.value = name, stat, stacks, value
        self.turns, self.tick, self.target, self.affects = turns, tick, target, affects

    @property
    def tick_owner(self):
        return self.tick.split(",")[0].strip()

    @property
    def tick_kind(self):
        return self.tick.split(",")[-1].strip()

    def signature(self):
        return (self.name, self.stat, self.stacks, round(self.value, 6), self.turns, self.tick, self.target)


class Debuff:
    __slots__ = ("name", "source", "stat", "stacks", "value", "turns", "target", "targeting", "affects", "dot")

    def __init__(self, name, source, stat, stacks, value, turns, target, targeting, affects, dot):
        self.name, self.source, self.stat, self.stacks, self.value = name, source, stat, stacks, value
        self.turns, self.target, self.targeting, self.affects, self.dot = turns, target, targeting, affects, dot

    def signature(self):
        return (self.name, self.source, self.stat, self.stacks, round(self.value, 6), self.turns, self.target)


class Sub:
    """One logged action (TURN + RESULT) inside a unit turn. Repeats are merged: `count` hits."""

    def __init__(self):
        self.move = ""
        self.owner = ""
        self.role = ""
        self.kind = ""
        self.elements = []
        self.atk_types = []
        self.scaling = ""
        self.target = ""
        self.splits = ""
        self.energy_gain = 0.0
        self.sp_change = 0.0
        self.phase = "turn"            # "pre" = happened before the unit's ACTION line (ults, techniques)
        self.buffs = []
        self.debuffs = []
        self.toughness = defaultdict(float)
        self.total = 0.0
        self.dmg = 0.0
        self.ela = 0.0
        self.wb = 0.0
        self.hit = []
        self.broken = []
        self.heal = 0.0
        self.hp_lost = 0.0
        self.sp = None
        self.max_sp = None
        self.count = 1
        self.is_enemy_hit = False       # enemy attack on one of our characters
        self.note = ""

    @property
    def family(self):
        return re.sub(r"_\d+$", "", self.move)

    @property
    def is_ult(self):
        return "ULT" in self.atk_types

    def merge_key(self):
        return (self.family, self.owner, self.phase, tuple(self.atk_types), self.target, self.is_enemy_hit,
                tuple(b.signature() for b in self.buffs), tuple(d.signature() for d in self.debuffs))

    def absorb(self, other):
        self.count += other.count
        for attr in ("total", "dmg", "ela", "wb", "heal", "hp_lost", "energy_gain", "sp_change"):
            setattr(self, attr, getattr(self, attr) + getattr(other, attr))
        for k, v in other.toughness.items():
            self.toughness[k] += v
        for e in other.hit:
            if e not in self.hit:
                self.hit.append(e)
        for e in other.broken:
            if e not in self.broken:
                self.broken.append(e)
        if other.sp is not None:
            self.sp, self.max_sp = other.sp, other.max_sp


class Row:
    """One unit turn (an ACTION line in the log) or the pseudo-row "battle start"."""

    def __init__(self, kind, unit, total_av, turn_av=0.0, move="", attacks=0):
        self.kind = kind               # START | CHAR | SUMMON | ENEMY | CIRCUIT
        self.unit = unit
        self.total_av = total_av
        self.turn_av = turn_av
        self.move = move               # E / A for characters
        self.attacks = attacks
        self.start_state = {}          # unit -> dict(av, energy, maxhp, hp, shield) at the start of the turn
        self.end_state = {}            # same, taken from the next turn's start listing
        self.reset = None              # (new AV, SPD) of the acting unit
        self.av_changes = []           # (unit, new AV, text) from ADV / DELAY lines
        self.subs = []
        self.punchline = None
        self.sp = None
        self.max_sp = None

    @property
    def cycle(self):
        return 0 if self.total_av <= 150.0001 else int(-(-(self.total_av - 150.0) // 100))

    @property
    def total_dmg(self):
        """Damage dealt during this turn, weakness-break damage included (it is logged separately)."""
        return sum(s.total + s.wb for s in self.subs if not s.is_enemy_hit)


class Build:
    def __init__(self, idx):
        self.idx = idx
        self.name = ""
        self.eidolon = 0
        self.element = ""
        self.path = ""
        self.role = ""
        self.pos = idx
        self.scaling = ""
        self.rotation = ""
        self.max_energy = None
        self.start_energy = None
        self.lightcone = ""
        self.relic1 = ""
        self.relic2 = ""
        self.planar = ""
        self.mains = {}
        self.rolls = OrderedDict()
        self.stats = OrderedDict()     # stat -> dict(final, relic, buffs, base)


class Battle:
    def __init__(self):
        self.builds = []
        self.context = {}
        self.enemies = []              # dict(idx, name, level, spd, weakness, toughness, max_hp)
        self.rows = []
        self.summary = {}
        self.units = []                # unit names in the order of the first turn listing
        self.role_to_name = {}
        self.char_names = []
        self.log_path = ""

    def name_for_role(self, role):
        return self.role_to_name.get(role, role)


_NUM = r"-?[\d.]+(?:e[-+]?\d+)?"
RE_UNIT = re.compile(rf"^-\s+(.+?) AV: ({_NUM}) ENERGY: ({_NUM}) MaxHP: ({_NUM}) CurrHp ({_NUM}) ShieldHP: ({_NUM})")
RE_BUFF = re.compile(
    rf"^(?P<name>.+?) \| (?P<stat>.+?) \| Stacks: (?P<stacks>\d+) \| Value: (?P<val>{_NUM}) \| "
    rf"Remaining Turns: (?P<turns>-?\d+) \| TickDown: (?P<tick>.+?) \| Target: (?P<target>\S+) \| Affects: (?P<aff>\[.*\])\s*$")
RE_DEBUFF = re.compile(
    rf"^(?P<name>.+?) \| From: (?P<src>\S+) \| (?P<stat>.+?) \| Stacks: (?P<stacks>\d+) \| Value: (?P<val>{_NUM}) \| "
    rf"Remaining Turns: (?P<turns>-?\d+) \| Target: (?P<target>\S+) \| Targeting: (?P<tg>\S+) \| Affects: (?P<aff>\[.*?\])"
    rf"(?: \| DOT: (?P<dot>\w+))?")
RE_ENEMY_HIT = re.compile(
    rf"^ENEMY  - (?P<enemy>.+?) \[(?P<kind>\w+)\] dealt (?P<dmg>{_NUM}) to (?P<tgt>.+?) \(energy: (?P<en>{_NUM}).*?\)"
    rf"(?: \| Shield Absorbed: (?P<sh>{_NUM}))?(?: \| HP Lost: (?P<lost>{_NUM}))?(?: \| HP: (?P<hp>[\d.]+/[\d.]+))?")


def _num(text, default=0.0):
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def _list(text):
    try:
        return list(ast.literal_eval(text))
    except (ValueError, SyntaxError):
        return []


def _kv(line):
    """'a=1 | b=2' fields -> dict (values stay strings)."""
    out = OrderedDict()
    for part in line.split(" | "):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def parse_log(path: str) -> Battle:
    battle = Battle()
    battle.log_path = path

    cur_row = None                      # row receiving sub-actions after its ACTION line
    pending = []                        # sub-actions logged before the next ACTION line (ults, techniques)
    block_listing = {}
    in_listing = False
    block_no = 0
    section = None
    sub = None
    last_punch = None
    pending_notes = []
    result_lines = []
    in_results = False
    header_mode = None
    header_chars = []
    cur_header_char = None
    unit_order = []

    def finish_sub():
        nonlocal sub
        if sub is None:
            return
        target = cur_row.subs if cur_row is not None else pending
        if cur_row is None:
            sub.phase = "pre"
        else:
            sub.phase = "turn"
        # merge with the previous sub when it is an identical repeat (e.g. the 33 bounce hits)
        if target and target[-1].merge_key() == sub.merge_key() and not sub.is_ult:
            target[-1].absorb(sub)
        else:
            target.append(sub)
        sub = None

    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            s = line.strip()
            if not s:
                in_listing = False
                continue

            # ── header: enemies / player team / build snapshot ─────────────────────────────
            if block_no == 0 and not in_results:
                if s == "Enemy Team:":
                    header_mode = "enemies"
                    continue
                if s == "Player Team:":
                    header_mode = "players"
                    continue
                if s.startswith("BUILD   >"):
                    body = s[len("BUILD   >"):].strip()
                    kind, _, rest = body.partition(" | ")
                    f = _kv(rest)
                    if kind == "CONTEXT":
                        battle.context = {k: _num(v) for k, v in f.items()}
                    elif kind == "CHAR":
                        b = Build(int(f["idx"]))
                        b.name, b.eidolon = f["name"], int(_num(f["eidolon"]))
                        b.element, b.path, b.role = f["element"], f["path"], f["role"]
                        b.pos, b.scaling, b.rotation = int(_num(f.get("pos", b.idx))), f.get("scaling", ""), f.get("rotation", "")
                        b.max_energy, b.start_energy = _num(f.get("maxEnergy")), _num(f.get("startEnergy"))
                        battle.builds.append(b)
                    elif f.get("idx") is not None:
                        b = next((x for x in battle.builds if x.idx == int(f["idx"])), None)
                        if b is not None:
                            if kind == "GEAR":
                                b.lightcone, b.relic1, b.relic2, b.planar = (f.get("lightcone", ""), f.get("relic1", ""),
                                                                             f.get("relic2", ""), f.get("planar", ""))
                            elif kind == "MAINS":
                                b.mains = dict(f)
                                b.mains.pop("idx", None)
                            elif kind == "ROLLS":
                                for k, v in f.items():
                                    if k != "idx":
                                        b.rolls[k] = int(_num(v))
                            elif kind == "STAT":
                                b.stats[f["stat"]] = {k: _num(v) for k, v in f.items() if k not in ("idx", "stat")}
                    continue
                if header_mode == "enemies":
                    m = re.match(r"^(Enemy \d+) \| LVL: (\d+) \| SPD: ([\d.]+) \| Weakness: (\[.*?\]) \| Toughness: ([\d.]+)", s)
                    if m:
                        battle.enemies.append(dict(name=m.group(1), level=int(m.group(2)), spd=_num(m.group(3)),
                                                   weakness=_list(m.group(4)), toughness=_num(m.group(5)), max_hp=None))
                        continue
                if header_mode == "players":
                    m = re.match(r"^(\S+) E(\d+) \| (\w+)-(\w+) \| (\w+) \| POS:(\d+)$", s)
                    if m:
                        cur_header_char = dict(name=m.group(1), eidolon=int(m.group(2)), element=m.group(3),
                                               path=m.group(4), role=m.group(5), pos=int(m.group(6)), gear=[])
                        header_chars.append(cur_header_char)
                        continue
                    if cur_header_char is not None and not s.startswith(("PUNCH", "=", "<<<", "Combat", "Registered")):
                        cur_header_char["gear"].append(s)
                        continue
                m = re.match(r"^PUNCH\s+> SharedPunchline: ([\d.]+) -> ([\d.]+)", s)
                if m:
                    last_punch = _num(m.group(2))
                    continue

            # ── start of a unit turn block ─────────────────────────────────────────────────
            if s == "<<< NEW TURN >>>":
                finish_sub()
                block_no += 1
                cur_row = None
                block_listing = {}
                in_listing = True
                section = None
                continue

            m = RE_UNIT.match(s) if in_listing else None
            if m:
                name = m.group(1)
                block_listing[name] = dict(av=_num(m.group(2)), energy=_num(m.group(3)), maxhp=_num(m.group(4)),
                                           hp=_num(m.group(5)), shield=_num(m.group(6)))
                if name not in unit_order:
                    unit_order.append(name)
                continue
            if in_listing and s.startswith("-"):
                continue
            in_listing = False

            if s == "==========SIMULATION RESULTS==========":
                finish_sub()
                in_results = True
                continue
            if in_results:
                result_lines.append(s)
                continue

            # ── ACTION line = a new row ────────────────────────────────────────────────────
            if s.startswith("ACTION >"):
                finish_sub()
                m = re.match(r"^ACTION > \[(\w+)\] TotalAV: ([\d.]+)(.*)$", s)
                if not m:
                    continue
                kind, total_av = m.group(1), _num(m.group(2))
                toks = [t.strip() for t in m.group(3).split(" | ") if t.strip()]
                turn_av = 0.0
                if toks and toks[0].startswith("TurnAV:"):
                    turn_av = _num(toks[0].split(":", 1)[1])
                    toks = toks[1:]
                unit = toks[0] if toks else ""
                move, attacks = "", 0
                if len(toks) > 1:
                    if toks[1].endswith("-move"):
                        move = toks[1].split("-")[0]
                    elif toks[1].endswith("attacks"):
                        attacks = int(_num(toks[1].split()[0]))
                    else:
                        move = toks[1]
                # the first block can hold techniques before anyone acts -> "battle start" row
                if pending and not battle.rows:
                    start = Row("START", "Battle start", 0.0)
                    start.start_state = dict(block_listing)
                    start.subs = pending
                    for p in start.subs:
                        p.phase = "turn"
                    battle.rows.append(start)
                    pending = []
                row = Row(kind, unit, total_av, turn_av, move, attacks)
                row.start_state = dict(block_listing)
                for p in pending:
                    p.phase = "pre"
                row.subs = pending
                pending = []
                row.punchline = last_punch
                battle.rows.append(row)
                cur_row = row
                continue

            # ── sub-action pieces ─────────────────────────────────────────────────────────
            if s.startswith("TURN   -"):
                finish_sub()
                f = [x.strip() for x in s[len("TURN   -"):].split(" | ")]
                sub = Sub()
                sub.move = f[0]
                if len(f) > 4:
                    sub.owner, sub.role, sub.kind = f[1], f[2], f[3]
                    sub.elements = _list(f[4]) if f[4].startswith("[") else []
                if len(f) > 5:
                    sub.atk_types = _list(f[5])
                for tok in f[6:]:
                    if tok.startswith("Scaling:"):
                        sub.scaling = tok.split(":", 1)[1].strip()
                    elif tok.startswith("TargetID:"):
                        sub.target = tok.split(":", 1)[1].strip()
                    elif tok.startswith("DMG/BREAK Splits:"):
                        sub.splits = tok.split(":", 1)[1].strip()
                    elif tok.startswith("Energy Gained:"):
                        sub.energy_gain = _num(tok.split(":", 1)[1])
                    elif tok.startswith("SP Change:"):
                        sub.sp_change = _num(tok.split(":", 1)[1])
                section = None
                continue

            if s.startswith("----------"):
                if "Char Buffs" in s:
                    section = "buffs"
                elif "Enemy Debuffs" in s:
                    section = "debuffs"
                elif s.startswith("----------End of"):
                    section = None
                else:
                    section = "other"
                continue

            if sub is not None and section == "buffs":
                m = RE_BUFF.match(s)
                if m:
                    sub.buffs.append(Buff(m["name"], m["stat"], int(m["stacks"]), _num(m["val"]), int(m["turns"]),
                                          m["tick"], m["target"], _list(m["aff"])))
                continue
            if sub is not None and section == "debuffs":
                m = RE_DEBUFF.match(s)
                if m:
                    sub.debuffs.append(Debuff(m["name"], m["src"], m["stat"], int(m["stacks"]), _num(m["val"]),
                                              int(m["turns"]), m["target"], m["tg"], _list(m["aff"]),
                                              (m["dot"] or "False") == "True"))
                continue
            if section == "other":
                continue

            if sub is not None and s.startswith("GAUGE"):
                m = re.match(r"^GAUGE  - (Enemy \d+) toughness reduced by ([\d.]+)", s)
                if m:
                    sub.toughness[m.group(1)] += _num(m.group(2))
                continue

            if sub is not None and s.startswith("RESULT -"):
                body = s[len("RESULT -"):]
                for key, attr in (("TOTALDMG", "total"), ("DMG", "dmg"), ("ELADMG", "ela"), ("WB DMG", "wb"),
                                  ("Amount HP Healed", "heal"), ("Amount HP Lost", "hp_lost")):
                    mm = re.search(rf"\| {re.escape(key)}: ({_NUM})", body)
                    if mm:
                        setattr(sub, attr, _num(mm.group(1)))
                if "| TOTALDMG:" not in body:          # logs from before TOTALDMG existed
                    sub.total = sub.dmg + sub.ela
                mm = re.search(r"Enemies Hit: (\[.*?\])", body)
                sub.hit = _list(mm.group(1)) if mm else []
                mm = re.search(r"Enemies Broken: (\[.*?\])", body)
                sub.broken = _list(mm.group(1)) if mm else []
                mm = re.search(r"SP: (\d+) \| MaxSP: (\d+)", body)
                if mm:
                    sub.sp, sub.max_sp = int(mm.group(1)), int(mm.group(2))
                finish_sub()
                continue

            # ── events between sub-actions ───────────────────────────────────────────────
            m = re.match(r"^PUNCH\s+> SharedPunchline: ([\d.]+) -> ([\d.]+)", s)
            if m:
                last_punch = _num(m.group(2))
                if cur_row is not None:
                    cur_row.punchline = last_punch
                continue
            if s.startswith("REPELLENCY"):
                pending_notes.append(s.split(">", 1)[1].strip())
                continue
            # Damage that is counted in the team total but has no RESULT line of its own, e.g. Cipher's ult releasing
            # her tally as True DMG ("TRUE   - Cipher Ult 25% tally True DMG: 123.4 to enemy 1").
            # (Lines like "TRUE   - AeonAha dealt 12.3 True DMG to Enemy 0" are already inside a RESULT line: skipped.)
            m = re.match(r"^TRUE\s+- (\S+) (.+?True DMG): ([\d.]+) to enemy (\d+)", s)
            if m:
                finish_sub()
                ex = Sub()
                ex.owner = m.group(1)
                ex.move = m.group(1) + re.sub(r"[^A-Za-z0-9]+", "", m.group(2))
                ex.kind = "True DMG"
                ex.target = m.group(4)
                ex.total = ex.dmg = _num(m.group(3))
                ex.hit = [int(m.group(4))]
                ex.note = "True DMG, logged as its own line (no RESULT line)"
                if cur_row is not None:
                    ex.phase = "turn"
                    cur_row.subs.append(ex)
                else:
                    ex.phase = "pre"
                    pending.append(ex)
                continue
            m = RE_ENEMY_HIT.match(s)
            if m and cur_row is not None:
                hit = Sub()
                hit.is_enemy_hit = True
                hit.move = f"{m['enemy']} [{m['kind']}]"
                hit.owner = m["enemy"]
                hit.target = m["tgt"]
                hit.total = _num(m["lost"]) if m["lost"] else _num(m["dmg"])
                hit.dmg = _num(m["dmg"])
                hit.energy_gain = _num(m["en"])
                hit.note = " · ".join(pending_notes + ([f"HP {m['hp']}"] if m["hp"] else []) +
                                     ([f"shield absorbed {m['sh']}"] if m["sh"] and _num(m["sh"]) else []))
                pending_notes = []
                cur_row.subs.append(hit)
                continue
            m = re.match(r"^AV     > (.+?) AV reset to ([\d.\-]+) \| ([\d.]+) SPD", s)
            if m and cur_row is not None:
                if m.group(1) == cur_row.unit and cur_row.reset is None:
                    cur_row.reset = (_num(m.group(2)), _num(m.group(3)))
                continue
            m = re.match(r"^(ADV|DELAY)\s+> (.+?) (advanced|delayed) by ([\d.\-]+)% from (\S+) \| NewAV: ([\d.\-]+)", s)
            if m and cur_row is not None:
                cur_row.av_changes.append((m.group(2), _num(m.group(6)),
                                           f"{m.group(2)} {m.group(3)} {m.group(4)}% ({m.group(5)})"))
                continue
        finish_sub()

    # leftover pre-actions that never got an ACTION line (should not happen) are dropped on purpose

    # ── post-processing ───────────────────────────────────────────────────────────────────────
    battle.units = unit_order
    if not battle.builds:           # old log without a BUILD section: use the "Player Team" header
        for i, hc in enumerate(header_chars):
            b = Build(i)
            b.name, b.eidolon, b.element, b.path, b.role, b.pos = (hc["name"], hc["eidolon"], hc["element"],
                                                                    hc["path"], hc["role"], hc["pos"])
            gear = hc["gear"]
            b.lightcone = gear[0] if gear else ""
            b.relic1 = gear[1] if len(gear) > 1 else ""
            b.planar = gear[-1] if len(gear) > 2 else ""
            battle.builds.append(b)
    battle.role_to_name = {b.role: b.name for b in battle.builds}
    battle.role_to_name.setdefault("AHA", "Aha")
    battle.char_names = [b.name for b in battle.builds]

    # enemy max HP from the first listing
    if battle.rows:
        first = battle.rows[0].start_state
        for e in battle.enemies:
            e["max_hp"] = first.get(e["name"], {}).get("maxhp")

    # SP after each row = SP printed by the last sub that printed one; punchline carried forward
    sp, mx, punch = None, None, None
    for row in battle.rows:
        for sbn in row.subs:
            if sbn.sp is not None:
                sp, mx = sbn.sp, sbn.max_sp
        row.sp, row.max_sp = sp, mx
        if row.punchline is not None:
            punch = row.punchline
        row.punchline = punch

    # end-of-turn state = the next turn's start listing; last row = final state from the summary
    for i, row in enumerate(battle.rows):
        nxt = battle.rows[i + 1] if i + 1 < len(battle.rows) else None
        if nxt is not None:
            row.end_state = nxt.start_state
    battle.summary = _parse_summary(result_lines, battle)
    if battle.rows:
        battle.rows[-1].end_state = battle.summary.get("final_state") or battle.rows[-1].start_state
    return battle


def _parse_summary(lines, battle):
    out = {"chars": OrderedDict(), "enemies": OrderedDict(), "final_state": {}}
    for s in lines:
        m = re.match(r"^TOTAL TEAM DMG: ([\d.]+) \| AV: (\d+)", s)
        if m:
            out["team_dmg"], out["av_limit"] = _num(m.group(1)), int(m.group(2))
        m = re.match(r"^TEAM DPAV: ([\d.]+)", s)
        if m:
            out["team_dpav"] = _num(m.group(1))
        m = re.match(r"^SP GAINED: (\d+) \| SP USED: (\d+) \| Enemy Attacks: (\d+)", s)
        if m:
            out["sp_gained"], out["sp_used"], out["enemy_attacks"] = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        m = re.match(r"^FINITE HP MODE: ON \| Total Overkill DMG: ([\d.]+)", s)
        if m:
            out["overkill"] = _num(m.group(1))
        m = re.match(r"^(Enemy \d+) \((\w+)\) \| Overkill: ([\d.]+) \| HP: ([\d.]+)/([\d.]+)", s)
        if m:
            out["enemies"][m.group(1)] = dict(type=m.group(2), overkill=_num(m.group(3)), hp=_num(m.group(4)),
                                              max_hp=_num(m.group(5)))
            out["final_state"][m.group(1)] = dict(av=None, energy=0.0, maxhp=_num(m.group(5)), hp=_num(m.group(4)),
                                                  shield=0.0)
        m = re.match(r"^(\S+) DPAV: ([\d.]+), ([\d.]+)%$", s)
        if m:
            out["chars"].setdefault(m.group(1), {}).update(dpav=_num(m.group(2)), pct=_num(m.group(3)))
        m = re.match(r"^(\S+) > Total DMG: ([\d.]+) \|.*Excess Energy: ([\d.]+)", s)
        if m:
            out["chars"].setdefault(m.group(1), {}).update(total=_num(m.group(2)))
            out["final_state"][m.group(1)] = dict(av=None, energy=_num(m.group(3)), maxhp=0.0, hp=0.0, shield=0.0)
    return out


# ════════════════════════════════════════════════════════════════════════════════════════════
#  PART 2 — EXCEL WRITER
# ════════════════════════════════════════════════════════════════════════════════════════════
#
#  Everything that decides how the sheet looks is in this block, so it can be changed in one place.
#  Colours/fonts follow the user's own team sheets (dark grey cells, white text, Lexend).

FONT_NAME = "Lexend"

C_BG = "2F2F32"          # cell background
C_BG_ALT = "2A2A2D"      # second shade (hit rows, banding)
C_HEAD = "1F1F1F"        # header bars
C_HEAD2 = "1C1C1E"       # section titles / cycle dividers
C_TEXT = "FFFFFF"
C_MUTED = "A6A6AD"
C_LINE = "505058"        # separators between groups
C_TEAL = "A2C4C9"
C_PURPLE = "8E7CC3"
C_GOLD = "F2C14E"
C_RED = "E57373"
C_GREEN = "81C784"
C_TINT_ENEMY = "3A2E2F"
C_TINT_SUMMON = "322F3D"
C_TINT_START = "2C3A3E"

ELEMENT_COLOR = {"FIRE": "F4845F", "ICE": "7FD6F5", "IMAGINARY": "F6E27F", "QUANTUM": "A58BF0",
                 "PHYSICAL": "D0D0D0", "WIND": "7FE3B0", "LIGHTNING": "D58CF0"}

MAX_DAMAGE_COLUMNS_PER_CHAR = 6       # biggest damage sources per character get a column, the rest go to "Other"
COLLAPSE_NUMBERED_BUFFS_FROM = 4      # FooGo0..FooGo13 style buffs become ONE summed column once there are this many
BUFF_HEADER_MAX_CHARS = 26            # longer buff names are shortened in the header (full name = hover note)
ULT_SHOW_HIT_COUNT = False            # True: 'ULT x6' = number of ULT-tagged HITS (one ultimate can have several), False: 'ULT'
ULT_SHOW_BEFORE_MARK = False          # True: add '(before)' when the ult was cast before that unit's own turn started
BUFF_COL_WIDTH = 7.5                  # width of one buff/debuff matrix column
SHOW_RAW_BUFF_TEXT = True             # the full "name [stat] value xstacks 1T SUP2/PERM" text per hit

PCT_STATS = {"SPD%", "HP%", "ATK%", "DEF%", "CR%", "CD%", "BE%", "WBE%", "BRK_DMG%", "SBRK_DMG%", "OGH%", "SHD%",
             "ERR%", "EHR%", "ERS%", "DMG%", "SHRED", "VULN", "PEN", "Elation", "DMG_REDUCTION", "ICEPEN", "FIRPEN",
             "LNGPEN", "WINPEN", "PHYPEN", "QUAPEN", "IMGPEN"}

MODIFIER_COLUMNS = [("ATK%", "ATK%"), ("HP%", "HP%"), ("DEF%", "DEF%"), ("SPD%", "SPD%"), ("CR%", "Crit rate"),
                    ("CD%", "Crit DMG"), ("DMG%", "DMG%"), ("Elation", "Elation"), ("SHRED", "DEF shred"),
                    ("PEN", "RES pen"), ("BANGER", "Banger")]

STAT_ROWS = [("HP", "HP", "num"), ("ATK", "ATK", "num"), ("DEF", "DEF", "num"), ("SPD", "SPD", "num"),
             ("CR", "Crit rate", "pct"), ("CD", "Crit DMG", "pct"), ("DMG", "DMG%", "pct"),
             ("ERR", "Energy regen", "pct"), ("BE", "Break effect", "pct"), ("EHR", "Effect hit rate", "pct"),
             ("ERS", "Effect RES", "pct"), ("HEAL", "Healing", "pct"), ("ELA", "Elation%", "pct")]

ROLL_ROWS = [("spd", "SPD"), ("hpFlat", "HP flat"), ("atkFlat", "ATK flat"), ("defFlat", "DEF flat"),
             ("hpPct", "HP%"), ("atkPct", "ATK%"), ("defPct", "DEF%"), ("be", "Break effect"),
             ("ehr", "Effect hit rate"), ("ers", "Effect RES"), ("cr", "Crit rate"), ("cd", "Crit DMG")]
BASE_ROLLS_PER_STAT = 2               # every sub stat starts with 2 rolls; "free" rolls = total - 12 * 2
FREE_ROLLS = 24


def _require_xlsxwriter():
    try:
        import xlsxwriter
        return xlsxwriter
    except ImportError as e:
        raise RuntimeError("xlsxwriter is required for the battle sheets. Install it with:\n"
                           "    pip install xlsxwriter") from e


class _Fmt:
    """Format factory with a cache (xlsxwriter formats are workbook-level objects)."""

    def __init__(self, wb):
        self.wb = wb
        self.cache = {}

    def __call__(self, **props):
        base = dict(font_name=FONT_NAME, font_size=9, font_color=C_TEXT, bg_color=C_BG, valign="vcenter")
        base.update(props)
        key = tuple(sorted(base.items()))
        if key not in self.cache:
            self.cache[key] = self.wb.add_format(base)
        return self.cache[key]


class _Link:
    def __init__(self, url, text):
        self.url, self.text = url, text


class _Grid:
    """Sparse cell model of one tab; written row by row at the end (xlsxwriter constant-memory mode)."""

    def __init__(self):
        self.cells = {}
        self.merges = {}
        self.heights = {}
        self.notes = {}

    def put(self, r, c, value=None, **props):
        self.cells[(r, c)] = (value, props)

    def merge(self, r, c1, c2, value=None, **props):
        if c1 == c2:
            self.put(r, c1, value, **props)
        else:
            self.merges.setdefault(r, []).append((c1, c2, value, props))

    def fill(self, r1, r2, c1, c2, **props):
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                if (r, c) not in self.cells:
                    self.cells[(r, c)] = (None, props)

    def emit(self, ws, F):
        by_row = defaultdict(list)
        for (r, c), (v, p) in self.cells.items():
            by_row[r].append((c, v, p))
        max_row = max(list(by_row) + list(self.merges) + [0])
        for r in range(max_row + 1):
            if r in self.heights:
                ws.set_row(r, self.heights[r])
            merged = self.merges.get(r, [])
            covered = set()
            for c1, c2, v, p in merged:
                covered.update(range(c1, c2 + 1))
                ws.merge_range(r, c1, r, c2, "" if v is None else v, F(**p))
            for c, v, p in sorted(by_row.get(r, [])):
                if c in covered:
                    continue
                f = F(**p)
                if isinstance(v, _Link):
                    ws.write_url(r, c, v.url, f, string=v.text)
                elif v is None or v == "":
                    ws.write_blank(r, c, None, f)
                elif isinstance(v, (int, float)):
                    ws.write_number(r, c, v, f)
                else:
                    ws.write_string(r, c, str(v), f)
                if (r, c) in self.notes:
                    ws.write_comment(r, c, self.notes[(r, c)], {"x_scale": 1.6, "y_scale": 0.5, "font_name": FONT_NAME,
                                                                 "font_size": 8})


class _Cols:
    """Assigns consecutive column numbers and remembers groups."""

    def __init__(self, start):
        self.next = start
        self.items = []
        self.groups = OrderedDict()
        self.index = {}

    def add(self, group, key, header, width, sub="", **extra):
        c = self.next
        self.next += 1
        self.items.append(dict(col=c, group=group, key=key, header=header, width=width, sub=sub, **extra))
        self.index[key] = c
        self.groups.setdefault(group, [c, c])[1] = c
        return c

    def skip(self, n=1):
        self.next += n


def _shorten_middle(text, n):
    """Keep the start and the end of a long name ('BangerELASkill…hereGoGo#'): the end is what tells variants apart."""
    if len(text) <= n:
        return text
    head = (n - 1) // 2 + 1
    return text[:head] + "…" + text[-(n - 1 - head):]


def _numbered_stem(name):
    """'FooGo13' -> 'FooGo' (name without its trailing counter); names without a counter come back unchanged."""
    m = re.match(r"^(.*?[A-Za-z_])\d+$", name)
    return m.group(1) if m else name


def _camel(name):
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", name)


def _strip_owner(family, owner):
    return family[len(owner):] if owner and family.startswith(owner) and len(family) > len(owner) else family


def _short(text, n):
    return text if len(text) <= n else text[:n - 1] + "…"


# Short codes for tab names (Excel limits tab names to 31 characters). Unknown names fall back to their initials.
TAB_CODES = {"SilverWolf999": "SW999", "Yao Guang": "YG", "YaoGuang": "YG", "AeonAha": "AA", "Pearl": "PE",
             "Sparxie": "SX"}


def _tab_code(base):
    if base in TAB_CODES:
        return TAB_CODES[base]
    words = base.split()
    if len(words) > 1:
        return "".join(w[0].upper() for w in words)
    humps = re.findall(r"[A-Z][a-z]+|[A-Z]+(?![a-z])|\d+", base)
    if len(humps) > 1:
        return "".join(h if (len(h) > 1 and h.isupper()) or h.isdigit() else h[0] for h in humps)
    return base[:2].upper()


def _tab_title(index, team_name, used):
    """'12 SW999 0.1 AA 2.1 YG PE': NN + one code per character; 'E.S' = eidolon.superimposition (left out at 0.0)."""
    segs = [x.strip() for x in team_name.split("|")]
    parsed = []
    for seg in segs:
        m = re.match(r"^(.*?)(?:\s+e(\d+)s(\d+))?$", seg)
        code = _tab_code(m.group(1).strip())
        tag = "" if m.group(2) is None or (m.group(2), m.group(3)) == ("0", "0") else f"{m.group(2)}.{m.group(3)}"
        parsed.append((code, tag))
    title = ""
    for shorten in (False, True):
        parts = [(("SW" if shorten and c == "SW999" else c) + (f" {t}" if t else "")) for c, t in parsed]
        title = f"{index:02d} " + " ".join(parts)
        if len(title) <= 31:
            break
    title = re.sub(r"[\[\]:*?/\\']", "", title)[:31].rstrip()
    base_title, n = title, 2
    while title.lower() in used:
        suffix = f" ({n})"
        title = base_title[:31 - len(suffix)] + suffix
        n += 1
    used.add(title.lower())
    return title


def _fmt_buff_text(b):
    aff = "" if b.affects == ["ALL"] else f" → {','.join(b.affects)}"
    return f"{b.name} [{b.stat}] {b.value:.3f} ×{b.stacks} · {b.turns}T · {b.tick}{aff}"


def _fmt_debuff_text(d):
    aff = "" if d.affects == ["ALL"] else f" → {','.join(d.affects)}"
    return f"{d.name} [{d.stat}] {d.value:.3f} ×{d.stacks} · {d.turns}T · from {d.source} on {d.target}{aff}"


def _write_team_tab(ws, F, battle, title, team_name, index):
    g = _Grid()
    builds = battle.builds
    chars = [b.name for b in builds]
    role_order = [b.role for b in builds]
    elem_of = {b.name: ELEMENT_COLOR.get(b.element, C_TEXT) for b in builds}
    max_energy = {b.name: b.max_energy for b in builds}
    summary = battle.summary
    enemies = [e["name"] for e in battle.enemies] or sorted(
        {u for u in battle.units if u.startswith("Enemy")})

    # ── column plan ────────────────────────────────────────────────────────────────────────
    LEFT0, LEFT1 = 1, 8                 # builds live in B..I
    T = _Cols(10)                       # turn table starts in K
    T.add("TURN", "n", "#", 5)
    T.add("TURN", "cycle", "Cycle", 6)
    T.add("TURN", "av", "AV", 8)
    T.add("TURN", "unit", "Unit", 17)
    T.add("TURN", "move", "Move", 7)
    T.add("TURN", "sp", "SP", 5)
    for n in chars:
        T.add("ULTIMATES", ("ult", n), n, 11)
    for n in chars:
        T.add("ENERGY (after turn)", ("en", n), n, 11)

    plan = OrderedDict()
    totals = defaultdict(lambda: defaultdict(float))
    for row in battle.rows:
        for s in row.subs:
            if not s.is_enemy_hit:
                totals[s.owner][s.family] += s.total + s.wb
    for owner in chars + [o for o in totals if o not in chars and sum(totals[o].values()) > 0]:
        fams = [f for f, v in sorted(totals[owner].items(), key=lambda kv: -kv[1]) if v > 0]
        shown = fams[:MAX_DAMAGE_COLUMNS_PER_CHAR]
        plan[owner] = (shown, len(fams) > len(shown))
    for owner, (shown, other) in plan.items():
        for fam in shown:
            T.add(f"DAMAGE · {owner}", ("dmg", owner, fam), _camel(_strip_owner(fam, owner)), 13)
        if other:
            T.add(f"DAMAGE · {owner}", ("dmg", owner, "__other__"), "Other", 13)
        if not shown and not other:
            T.add(f"DAMAGE · {owner}", ("dmg", owner, "__none__"), "—", 6)
    T.add("TOTALS", "turn_dmg", "Turn DMG", 14)
    T.add("TOTALS", "cum_dmg", "Total DMG", 15)
    T.add("TOTALS", "punch", "Punchline", 9)
    for e in enemies:
        T.add("ENEMY HP (after turn)", ("hp", e), e, 12)
    units = chars + [u for u in battle.units if u not in chars and not u.startswith("Enemy")] + \
        [e for e in enemies]
    for u in units:
        T.add("AV AT TURN START", ("av0", u), u, 11)
    for u in units:
        T.add("AV AFTER ACTION", ("av1", u), u, 11)
    T.add("AV AFTER ACTION", "spd", "SPD (actor)", 9)
    T.add("AV AFTER ACTION", "avnote", "Advances / delays", 34)
    turn_last = T.next - 1

    # hit log
    H = _Cols(T.next + 1)
    H.add("HIT", "h_turn", "Turn #", 6)
    H.add("HIT", "h_av", "AV", 8)
    H.add("HIT", "h_unit", "Turn of", 15)
    H.add("HIT", "h_src", "Source", 15)
    H.add("HIT", "h_move", "Move", 28)
    H.add("HIT", "h_hits", "Hits", 6)
    H.add("HIT", "h_tgt", "Target", 13)
    H.add("HIT", "h_types", "Attack types", 17)
    H.add("HIT", "h_scal", "Scaling", 8)
    H.add("HIT", "h_sp", "SP Δ", 6)
    H.add("HIT", "h_en", "Energy +", 8)
    H.add("HIT", "h_tough", "Toughness −", 10)
    H.add("DAMAGE", "h_dmg", "DMG", 13)
    H.add("DAMAGE", "h_ela", "Elation DMG", 13)
    H.add("DAMAGE", "h_wb", "Break DMG", 11)
    H.add("DAMAGE", "h_tot", "Hit total", 13)
    for key, label in MODIFIER_COLUMNS:
        H.add("MODIFIERS APPLIED TO THIS HIT (sum)", ("mod", key), label, 8)
    H.add("MODIFIERS APPLIED TO THIS HIT (sum)", ("mod", "VULN"), "Enemy VULN", 8)
    H.add("NOTES", "h_note", "Note", 30)

    # buff matrix: collect every (target, buff) that ever applied
    bcols = OrderedDict()
    dcols = OrderedDict()
    variants = defaultdict(set)
    for row in battle.rows:
        for s in row.subs:
            for b in s.buffs:
                variants[(b.target, _numbered_stem(b.name), b.stat)].add(b.name)
    collapse = {k for k, v in variants.items() if len(v) >= COLLAPSE_NUMBERED_BUFFS_FROM}

    def bkey(b):
        st = _numbered_stem(b.name)
        return (b.target, st + "#") if (b.target, st, b.stat) in collapse else (b.target, b.name)

    for row in battle.rows:
        for s in row.subs:
            per = {}
            for b in s.buffs:
                k = bkey(b)
                v, perm = per.get(k, (0.0, True))
                per[k] = (v + b.value, perm and b.tick_kind == "PERM")
                bcols.setdefault(k, dict(stat=b.stat, vals=set(), perm=True))
            for k, (v, perm) in per.items():
                info = bcols[k]
                info["vals"].add(round(v, 6))
                if not perm:
                    info["perm"] = False
            for d in s.debuffs:
                info = dcols.setdefault((d.source, d.name), dict(stat=d.stat))
    for info in bcols.values():
        info["constant"] = info["perm"] and len(info["vals"]) == 1
    target_order = role_order + [t for t in {k[0] for k in bcols} if t not in role_order]

    def role_label(role):
        return battle.name_for_role(role)

    for t in target_order:
        for key in sorted((k for k, v in bcols.items() if k[0] == t and not v["constant"]),
                          key=lambda k: (bcols[k]["stat"], k[1])):
            H.add(f"BUFFS · {role_label(t)}", ("b", key), key[1], BUFF_COL_WIDTH, sub=bcols[key]["stat"], rot=True)
    for key in sorted(dcols, key=lambda k: (dcols[k]["stat"], k[1], k[0])):
        H.add("ENEMY DEBUFFS", ("d", key), key[1], BUFF_COL_WIDTH, sub=f"{dcols[key]['stat']} · {key[0]}", rot=True)
    const_first = H.next
    for t in target_order:
        for key in sorted((k for k, v in bcols.items() if k[0] == t and v["constant"]),
                          key=lambda k: (bcols[k]["stat"], k[1])):
            H.add(f"PERMANENT, UNCHANGED · {role_label(t)}", ("b", key), key[1], BUFF_COL_WIDTH, sub=bcols[key]["stat"], rot=True)
    const_last = H.next - 1
    if SHOW_RAW_BUFF_TEXT:
        H.add("FULL TEXT", "h_rawb", "Buffs (name [stat] value ×stacks · turns left · tick-down owner/kind)", 60)
        H.add("FULL TEXT", "h_rawd", "Enemy debuffs", 60)
    last_col = H.next - 1

    ROW_GROUP, ROW_HEAD, ROW_SUB, DATA0 = 1, 2, 3, 4

    # ── background of the used areas (columns carry the colour for everything beyond) ───────────
    # ── header rows ───────────────────────────────────────────────────────────────────────────────
    rot_len = min(BUFF_HEADER_MAX_CHARS, max([len(it["header"]) for cols in (T, H) for it in cols.items if it.get("rot")] + [0]))
    g.heights.update({0: 22, 1: 16, 2: max(58, 14 + rot_len * 4.0), 3: 13})
    gh = dict(bold=True, font_size=9, bg_color=C_HEAD, font_color=C_TEAL, align="center", bottom=1,
              bottom_color=C_LINE, left=1, left_color=C_LINE)
    ch = dict(bold=True, font_size=8, bg_color=C_HEAD2, font_color=C_TEXT, align="center", valign="bottom",
              text_wrap=True, left=1, left_color=C_LINE)
    sh = dict(font_size=7, bg_color=C_HEAD2, font_color=C_MUTED, align="center", text_wrap=False)
    for cols in (T, H):
        for name, (c1, c2) in cols.groups.items():
            colr = C_PURPLE if name.startswith(("BUFFS", "ENEMY DEBUFFS", "PERMANENT", "FULL")) else C_TEAL
            wide = (c2 - c1) >= 8
            g.merge(ROW_GROUP, c1, c2, name, **{**gh, "font_color": colr,
                                                **({"align": "left", "indent": 1} if wide else {})})
        for it in cols.items:
            if it.get("rot"):
                g.put(ROW_HEAD, it["col"], _shorten_middle(it["header"], BUFF_HEADER_MAX_CHARS),
                      **{**ch, "rotation": 90, "text_wrap": False, "font_size": 7, "align": "center"})
                if len(it["header"]) > BUFF_HEADER_MAX_CHARS:
                    g.notes[(ROW_HEAD, it["col"])] = it["header"]
            else:
                g.put(ROW_HEAD, it["col"], it["header"], **ch)
            g.put(ROW_SUB, it["col"], it["sub"] or None, **{**sh, "shrink": True})

    # title bar
    result_txt = ""
    if summary.get("team_dpav"):
        result_txt = f"   ·   first battle DPAV {summary['team_dpav']:,.0f}"
    g.merge(0, LEFT0, LEFT1, team_name, bold=True, font_size=11, bg_color=C_HEAD, font_color=C_TEXT)
    g.merge(1, LEFT0, LEFT1, f"First battle · {int(battle.context.get('cycles', 0)) or '?'} cycles{result_txt}",
            font_size=8, bg_color=C_HEAD, font_color=C_MUTED)
    g.merge(2, LEFT0, LEFT1,
            "HOW TO READ\n"
            "• Left: build and stats of every character at the start of the battle (Base / Relic / Buffs / Final).\n"
            "• Middle: one row per unit turn - ults used, energy afterwards, damage per move, enemy HP, AV before and after. "
            "Click the # of a turn to jump to its hits.\n"
            "• Right: every single hit with the buffs and debuffs that applied to it (identical repeats are merged: 'Hits' column). "
            "Columns grouped under 'Permanent, unchanged' can be expanded with the + above the sheet.\n"
            "• Gold energy = ready for ult; red enemy HP = dead.\n"
            "• A = Basic attack and E = Skill attack\n",
            font_size=8, font_color=C_MUTED, bg_color=C_HEAD, text_wrap=True, valign="top")
    g.fill(3, 3, LEFT0, LEFT1, bg_color=C_HEAD)
    g.merge(0, T.items[0]["col"], turn_last, "BATTLE · one row per unit turn  (# links to its hits →)", bold=True,
            font_size=11, bg_color=C_HEAD, font_color=C_TEXT)
    g.merge(0, H.items[0]["col"], last_col, "HIT LOG · every hit with the buffs and debuffs that applied to it",
            bold=True, font_size=11, bg_color=C_HEAD, font_color=C_TEXT)

    # ── left: context + builds ───────────────────────────────────────────────────────────────────
    lab = dict(font_size=8, font_color=C_MUTED)
    r = 5
    g.merge(r, LEFT0, LEFT1, "CONTEXT", bold=True, bg_color=C_HEAD2, font_color=C_TEAL, align="center")
    r += 1
    ctx = battle.context
    for label, val in (("Cycle cap", ctx.get("cycles")), ("AV cap", ctx.get("avLimit")),
                       ("Start SP", ctx.get("startSP")), ("Max SP", ctx.get("maxSP"))):
        pass
    g.put(r, 1, "Cycle cap", **lab); g.put(r, 2, ctx.get("cycles"), num_format="0", align="center")
    g.put(r, 3, "AV cap", **lab); g.put(r, 4, ctx.get("avLimit"), num_format="0", align="center")
    g.put(r, 5, "Start SP", **lab); g.put(r, 6, ctx.get("startSP"), num_format="0", align="center")
    g.put(r, 7, "Max SP", **lab); g.put(r, 8, ctx.get("maxSP"), num_format="0", align="center")
    r += 1
    g.put(r, 1, "Enemy", bold=True, font_size=8, bg_color=C_HEAD)
    g.put(r, 2, "SPD", bold=True, font_size=8, bg_color=C_HEAD, align="center")
    g.put(r, 3, "Toughness", bold=True, font_size=8, bg_color=C_HEAD, align="center")
    g.merge(r, 4, 5, "HP", bold=True, font_size=8, bg_color=C_HEAD, align="center")
    g.merge(r, 6, 8, "Weakness", bold=True, font_size=8, bg_color=C_HEAD, align="center")
    r += 1
    for e in battle.enemies:
        g.put(r, 1, e["name"])
        g.put(r, 2, e["spd"], num_format="0.0", align="center")
        g.put(r, 3, e["toughness"], num_format="0", align="center")
        g.merge(r, 4, 5, e.get("max_hp"), num_format="#,##0", align="center")
        g.merge(r, 6, 8, ", ".join(e["weakness"]), align="center")
        r += 1
    if summary.get("team_dmg"):
        r += 1
        g.merge(r, LEFT0, LEFT1, "RESULT OF THIS BATTLE", bold=True, bg_color=C_HEAD2, font_color=C_TEAL, align="center")
        r += 1
        g.put(r, 1, "Team DMG", **lab); g.merge(r, 2, 3, summary["team_dmg"], num_format="#,##0", align="center")
        g.put(r, 5, "Team DPAV", **lab); g.merge(r, 6, 8, summary.get("team_dpav"), num_format="#,##0.0", align="center")
        r += 1
        g.put(r, 1, "Character", **lab)
        g.merge(r, 2, 3, "Total DMG", **{**lab, "align": "center"})
        g.merge(r, 5, 6, "DPAV", **{**lab, "align": "center"})
        g.put(r, 7, "Share", **{**lab, "align": "center"})
        r += 1
        for n in chars:
            cs = summary["chars"].get(n)
            if cs:
                g.put(r, 1, n, font_color=elem_of.get(n, C_TEXT))
                g.merge(r, 2, 3, cs.get("total"), num_format="#,##0", align="center")
                g.merge(r, 5, 6, cs.get("dpav"), num_format="#,##0.0", align="center")
                g.put(r, 7, (cs.get("pct") or 0) / 100.0, num_format="0.0%", align="center")
                r += 1
        ok = summary.get("overkill")
        if ok is not None:
            g.put(r, 1, "Overkill", **lab); g.merge(r, 2, 3, ok, num_format="#,##0", align="center")
            r += 1
        row_sum = sum(rw.total_dmg for rw in battle.rows)
        gap = summary["team_dmg"] - row_sum
        g.put(r, 1, "Check", **lab)
        if abs(gap) <= max(1.0, 1e-4 * summary["team_dmg"]):
            g.merge(r, 2, LEFT1, "✓ turn rows add up to the team DMG of the log", font_size=8, font_color=C_GREEN)
        else:
            g.merge(r, 2, LEFT1, f"⚠ {gap:,.0f} of the log's team DMG is not on any turn row", font_size=8,
                    font_color=C_RED, bold=True)
        r += 1
    r += 1
    for b in builds:
        r = _write_build_block(g, b, r, elem_of.get(b.name, C_TEXT))
    left_last = r
    g.fill(4, max(left_last, 5), LEFT0, LEFT1, bg_color=C_BG)

    # ── turn table + hit log rows ────────────────────────────────────────────────────────────────
    tint = {"ENEMY": C_TINT_ENEMY, "SUMMON": C_TINT_SUMMON, "START": C_TINT_START}
    cum = 0.0
    r = DATA0
    hit_r = DATA0
    last_cycle = None
    hit_first_row = {}
    build_by_name = {b.name: b for b in builds}
    # pre-compute the hit-log start row of every turn (for the # hyperlinks)
    _rr = DATA0
    for ti, row in enumerate(battle.rows):
        hit_first_row[ti] = _rr
        _rr += len(row.subs)
    safe = title.replace("'", "''")

    for ti, row in enumerate(battle.rows):
        # cycle divider
        if row.kind != "START" and row.cycle != last_cycle:
            last_cycle = row.cycle
            lo = 0 if row.cycle == 0 else 150 + (row.cycle - 1) * 100
            hi = 150 if row.cycle == 0 else lo + 100
            g.merge(r, T.items[0]["col"], turn_last, f"CYCLE {row.cycle}   ·   AV {lo} – {hi}", bold=True,
                    font_size=8, bg_color=C_HEAD2, font_color=C_GOLD, align="left", top=1, top_color=C_LINE)
            g.heights[r] = 14
            r += 1
        bg = tint.get(row.kind, C_BG)
        turn_row = r
        base = dict(bg_color=bg, bottom=1, bottom_color=C_BG_ALT)
        is_char = row.unit in elem_of
        cum += row.total_dmg
        g.fill(r, r, T.items[0]["col"], turn_last, **base)
        if row.subs:
            g.put(r, T.index["n"], _Link(f"internal:'{safe}'!{_cell(hit_first_row[ti], H.index['h_turn'])}", str(ti)),
                  **{**base, "font_color": C_TEAL, "align": "center", "underline": 0})
        else:
            g.put(r, T.index["n"], str(ti), **{**base, "align": "center", "font_color": C_MUTED})
        g.put(r, T.index["cycle"], row.cycle if row.kind != "START" else None, **{**base, "align": "center", "num_format": "0"})
        g.put(r, T.index["av"], row.total_av, **{**base, "num_format": "0.0", "align": "center"})
        ucolor = elem_of.get(row.unit, C_RED if row.kind == "ENEMY" else (C_PURPLE if row.kind == "SUMMON" else C_TEXT))
        g.put(r, T.index["unit"], row.unit, **{**base, "bold": True, "font_color": ucolor})
        mv = row.move or (f"{row.attacks} atk" if row.kind == "ENEMY" else "")
        g.put(r, T.index["move"], mv, **{**base, "align": "center"})
        g.put(r, T.index["sp"], row.sp, **{**base, "align": "center", "num_format": "0"})
        # ultimates
        ults = defaultdict(list)
        for s in row.subs:
            if s.is_ult and not s.is_enemy_hit:
                ults[s.owner].append(s.phase)
        for n in chars:
            if n in ults:
                phases = ults[n]
                txt = f"ULT ×{len(phases)}" if (ULT_SHOW_HIT_COUNT and len(phases) > 1) else "ULT"
                if ULT_SHOW_BEFORE_MARK and all(p == "pre" for p in phases):
                    txt += " (before)"
                g.put(r, T.index[("ult", n)], txt, **{**base, "bold": True, "font_color": C_GOLD, "align": "center",
                                                        "bg_color": "4A4130"})
        # energy
        for n in chars:
            e = row.end_state.get(n, {}).get("energy")
            ready = e is not None and max_energy.get(n) and e >= max_energy[n] - 1e-6
            g.put(r, T.index[("en", n)], e, **{**base, "num_format": "0.0", "align": "center",
                                                 **({"font_color": C_GOLD, "bold": True} if ready else {})})
        # damage per family
        acc = defaultdict(float)
        for s in row.subs:
            if s.is_enemy_hit:
                continue
            fams, other = plan.get(s.owner, ([], False))
            key = ("dmg", s.owner, s.family if s.family in fams else "__other__")
            acc[key] += s.total + s.wb
        for key, v in acc.items():
            if key in T.index and v:
                g.put(r, T.index[key], v, **{**base, "num_format": "#,##0", "align": "right"})
        g.put(r, T.index["turn_dmg"], row.total_dmg or None, **{**base, "num_format": "#,##0", "bold": True})
        g.put(r, T.index["cum_dmg"], cum, **{**base, "num_format": "#,##0", "font_color": C_MUTED})
        g.put(r, T.index["punch"], row.punchline, **{**base, "num_format": "0", "align": "center"})
        for e in enemies:
            st = row.end_state.get(e)
            if st is not None:
                dead = st["hp"] <= 0
                g.put(r, T.index[("hp", e)], st["hp"], **{**base, "num_format": "#,##0",
                                                         **({"font_color": C_RED} if dead else {})})
        # AV blocks
        av_after = {u: row.start_state.get(u, {}).get("av") for u in units}
        if row.reset is not None and row.unit in av_after:
            av_after[row.unit] = row.reset[0]
        for who, new_av, _ in row.av_changes:
            if who in av_after:
                av_after[who] = new_av
        for u in units:
            a0 = row.start_state.get(u, {}).get("av")
            if a0 is not None:
                g.put(r, T.index[("av0", u)], a0, **{**base, "num_format": "0.0", "align": "center",
                                                      **({"font_color": C_GOLD, "bold": True} if u == row.unit else {})})
            a1 = av_after.get(u)
            if a1 is not None:
                g.put(r, T.index[("av1", u)], a1, **{**base, "num_format": "0.0", "align": "center"})
        if row.reset is not None:
            g.put(r, T.index["spd"], row.reset[1], **{**base, "num_format": "0.0", "align": "center"})
        if row.av_changes:
            g.put(r, T.index["avnote"], "; ".join(t for _, _, t in row.av_changes), **{**base, "font_size": 7, "font_color": C_MUTED})
        r += 1

        # hit log rows
        for s in row.subs:
            hb = dict(bg_color=C_BG if (hit_r - DATA0) % 2 == 0 else C_BG_ALT)
            hb2 = dict(hb, bottom=1, bottom_color=C_BG_ALT)
            g.fill(hit_r, hit_r, H.items[0]["col"], H.index["h_note"], **hb2)
            g.put(hit_r, H.index["h_turn"], _Link(f"internal:'{safe}'!{_cell(turn_row, T.index['n'])}", str(ti)),
                  **{**hb2, "align": "center", "font_color": C_MUTED, "underline": 0})
            g.put(hit_r, H.index["h_av"], row.total_av, **{**hb2, "num_format": "0.0", "align": "center", "font_color": C_MUTED})
            g.put(hit_r, H.index["h_unit"], row.unit, **{**hb2, "font_color": C_MUTED})
            src_color = elem_of.get(s.owner, C_RED if s.is_enemy_hit else C_TEXT)
            g.put(hit_r, H.index["h_src"], s.owner, **{**hb2, "font_color": src_color, "bold": s.is_ult})
            g.put(hit_r, H.index["h_move"], s.family if not s.is_enemy_hit else s.move,
                  **{**hb2, **({"bold": True, "font_color": C_GOLD} if s.is_ult else {})})
            g.put(hit_r, H.index["h_hits"], s.count if s.count > 1 else None, **{**hb2, "align": "center", "num_format": "0"})
            g.put(hit_r, H.index["h_tgt"], ("→ " + s.target) if s.is_enemy_hit else (_target(s.target)),
                  **{**hb2, "font_color": C_MUTED})
            g.put(hit_r, H.index["h_types"], "ENEMY ATTACK" if s.is_enemy_hit else ", ".join(s.atk_types),
                  **{**hb2, "font_size": 8, "font_color": C_RED if s.is_enemy_hit else C_MUTED})
            g.put(hit_r, H.index["h_scal"], s.scaling or None, **{**hb2, "align": "center", "font_color": C_MUTED, "font_size": 8})
            g.put(hit_r, H.index["h_sp"], (s.sp_change or None), **{**hb2, "align": "center", "num_format": "0;-0"})
            g.put(hit_r, H.index["h_en"], (s.energy_gain or None), **{**hb2, "align": "center", "num_format": "0.0"})
            tough = sum(s.toughness.values())
            g.put(hit_r, H.index["h_tough"], tough or None, **{**hb2, "align": "center", "num_format": "0.0"})
            if s.is_enemy_hit:
                g.put(hit_r, H.index["h_tot"], s.total, **{**hb2, "num_format": "#,##0.0", "font_color": C_RED})
            else:
                g.put(hit_r, H.index["h_dmg"], s.dmg or None, **{**hb2, "num_format": "#,##0"})
                g.put(hit_r, H.index["h_ela"], s.ela or None, **{**hb2, "num_format": "#,##0"})
                g.put(hit_r, H.index["h_wb"], s.wb or None, **{**hb2, "num_format": "#,##0"})
                g.put(hit_r, H.index["h_tot"], (s.total + s.wb) or None, **{**hb2, "num_format": "#,##0", "bold": True})
                sums = defaultdict(float)
                for b in s.buffs:
                    sums[b.stat] += b.value
                for key, _label in MODIFIER_COLUMNS:
                    if key in sums:
                        pct = key in PCT_STATS
                        g.put(hit_r, H.index[("mod", key)], sums[key],
                              **{**hb2, "num_format": "0.0%" if pct else "0.##", "align": "center"})
                vuln = sum(d.value for d in s.debuffs if d.stat == "VULN")
                if vuln:
                    g.put(hit_r, H.index[("mod", "VULN")], vuln, **{**hb2, "num_format": "0.0%", "align": "center"})
            notes = []
            if s.phase == "pre":
                notes.append("before the turn")
            if s.note:
                notes.append(s.note)
            if s.broken:
                notes.append("broke " + ",".join(str(x) for x in s.broken))
            g.put(hit_r, H.index["h_note"], " · ".join(notes) or None, **{**hb2, "font_size": 7, "font_color": C_MUTED})
            cell_sum, cell_stat = defaultdict(float), {}
            for b in s.buffs:
                k = bkey(b)
                cell_sum[k] += b.value
                cell_stat[k] = b.stat
            for k, v in cell_sum.items():
                c = H.index.get(("b", k))
                if c is not None:
                    g.put(hit_r, c, v, **{**hb, "num_format": "0.0%" if cell_stat[k] in PCT_STATS else "0.###",
                                          "align": "center", "font_size": 8})
            for d in s.debuffs:
                c = H.index.get(("d", (d.source, d.name)))
                if c is not None:
                    g.put(hit_r, c, d.value, **{**hb, "num_format": "0.0%" if d.stat in PCT_STATS else "0.###",
                                                  "align": "center", "font_size": 8})
            if SHOW_RAW_BUFF_TEXT:
                g.put(hit_r, H.index["h_rawb"], " ; ".join(_fmt_buff_text(b) for b in s.buffs) or None,
                      **{**hb, "font_size": 7, "font_color": C_MUTED})
                g.put(hit_r, H.index["h_rawd"], " ; ".join(_fmt_debuff_text(d) for d in s.debuffs) or None,
                      **{**hb, "font_size": 7, "font_color": C_MUTED})
            hit_r += 1

    # ── write out ────────────────────────────────────────────────────────────────────────────────
    ws.hide_gridlines(2)
    ws.set_zoom(90)
    ws.set_tab_color("#" + C_TEAL)
    ws.freeze_panes(DATA0, 0)
    bgfmt = F()
    ws.set_column(0, last_col + 12, 9, bgfmt)
    ws.set_column(0, 0, 2, bgfmt)
    ws.set_column(LEFT0, LEFT0, 16, bgfmt)
    ws.set_column(LEFT0 + 1, LEFT0 + 4, 10.5, bgfmt)
    ws.set_column(7, 7, 11, bgfmt)
    ws.set_column(8, 8, 9, bgfmt)
    ws.set_column(9, 9, 3, bgfmt)
    for cols in (T, H):
        for it in cols.items:
            ws.set_column(it["col"], it["col"], it["width"], bgfmt)
    ws.set_column(T.next, T.next, 3, bgfmt)
    if const_last >= const_first:
        ws.outline_settings(True, False, True, False)
        for c in range(const_first, const_last + 1):
            ws.set_column(c, c, 9, bgfmt, {"level": 1, "hidden": True})
        ws.set_column(const_last + 1, const_last + 1, 60 if SHOW_RAW_BUFF_TEXT else 9, bgfmt, {"collapsed": True})
    g.emit(ws, F)
    return dict(title=title, name=team_name, index=index, dpav=summary.get("team_dpav"),
                team_dmg=summary.get("team_dmg"), rows=len(battle.rows), hits=hit_r - DATA0)


def _cell(row, col):
    from xlsxwriter.utility import xl_rowcol_to_cell
    return xl_rowcol_to_cell(row, col, row_abs=True, col_abs=True)


def _target(tid):
    return {"-1": "—", "": ""}.get(tid, f"Enemy {tid}" if tid.lstrip("-").isdigit() else tid)


def _write_build_block(g, b, r0, color):
    LEFT0, LEFT1 = 1, 8
    head = dict(bold=True, bg_color=C_HEAD2, font_size=10, font_color=color, bottom=1, bottom_color=C_LINE)
    g.merge(r0, LEFT0, 3, b.name, **head)
    g.put(r0, 4, b.element.title(), **{**head, "font_size": 8, "align": "center"})
    g.put(r0, 5, b.path.title(), **{**head, "font_size": 8, "align": "center", "font_color": C_TEXT})
    g.put(r0, 6, b.role, **{**head, "font_size": 8, "align": "center", "font_color": C_TEXT})
    g.merge(r0, 7, LEFT1, f"E{b.eidolon} · POS {b.pos}", **{**head, "font_size": 8, "align": "center", "font_color": C_TEXT})
    lab = dict(font_size=8, font_color=C_MUTED)
    g.put(r0 + 1, 1, "Lightcone", **lab); g.merge(r0 + 1, 2, LEFT1, b.lightcone or "—")
    relic = b.relic1 + (f"  +  {b.relic2}" if b.relic2 else "")
    g.put(r0 + 2, 1, "Relic set", **lab); g.merge(r0 + 2, 2, LEFT1, relic or "—")
    g.put(r0 + 3, 1, "Planar set", **lab); g.merge(r0 + 3, 2, LEFT1, b.planar or "—")
    if not b.stats:
        g.merge(r0 + 4, 1, LEFT1, "(no build data in this log — run it again with the current Combat_Simulator.py)",
                font_size=8, font_color=C_MUTED)
        return r0 + 6
    g.put(r0 + 4, 1, "Main stats", **lab)
    for i, (lbl, key) in enumerate((("Chest", "body"), ("Feet", "boots"), ("Sphere", "sphere"), ("Link rope", "rope"))):
        g.put(r0 + 4, 2 + i, lbl, **{**lab, "align": "center"})
        g.put(r0 + 5, 2 + i, b.mains.get(key, ""), **{"bold": True, "align": "center", "font_color": color})
    hdr = dict(bold=True, font_size=8, bg_color=C_HEAD, align="center")
    g.put(r0 + 6, 1, "Stats at battle start", **{**hdr, "align": "left"})
    for i, t in enumerate(("Base", "Relic", "Buffs", "Final")):
        g.put(r0 + 6, 2 + i, t, **hdr)
    g.put(r0 + 6, 7, "Sub rolls", **{**hdr, "align": "left"})
    total_rolls = (b.rolls.get("total") if b.rolls.get("total") is not None else
                   sum(v for k, v in b.rolls.items() if k != "total")) if b.rolls else 0
    free = total_rolls - len(ROLL_ROWS) * BASE_ROLLS_PER_STAT
    g.put(r0 + 6, 8, f"{free}/{FREE_ROLLS}", **{**hdr, **({"font_color": C_RED} if free > FREE_ROLLS else {})})
    for i, (key, label, kind) in enumerate(STAT_ROWS):
        rr = r0 + 7 + i
        st = b.stats.get(key)
        g.put(rr, 1, label)
        if not st:
            continue
        nf = "#,##0.0" if kind == "num" else "0.0%"
        base, relic_v, buff_v, final = st.get("base", 0.0), st.get("relic", 0.0), st.get("buffs", 0.0), st.get("final", 0.0)
        if key == "ERR":                  # shown as total energy regen rate: 100% + bonuses
            base, final = 1.0, 1.0 + final
        if key == "ELA":
            base = 0.0
        g.put(rr, 2, base or None, num_format=nf, align="center", font_color=C_MUTED)
        g.put(rr, 3, relic_v or None, num_format=nf, align="center", font_color=C_MUTED)
        g.put(rr, 4, buff_v or None, num_format=nf, align="center", font_color=C_MUTED)
        g.put(rr, 5, final, num_format=nf, align="center", bold=True, font_color=color if key in ("SPD", "CR", "CD") else C_TEXT)
    for i, (key, label) in enumerate(ROLL_ROWS):
        rr = r0 + 7 + i
        g.put(rr, 7, label, font_size=8)
        v = b.rolls.get(key)
        g.put(rr, 8, v, align="center", num_format="0", bold=(v is not None and v > BASE_ROLLS_PER_STAT))
    return r0 + 7 + len(STAT_ROWS) + 1


def build_battle_workbook(entries, out_path, progress=None, errors=None):
    """entries: list of (team_index, team_name, log_path). Returns out_path.

    One tab per entry (parsed from its log) plus a first tab "Teams" that lists them with links.
    A log that cannot be parsed/written is skipped; the reason is appended to `errors` (if given) and the
    team shows up on the Teams tab as failed, so one bad log never costs you the other tabs.
    """
    xw = _require_xlsxwriter()
    out_dir = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(out_dir, exist_ok=True)
    wb = xw.Workbook(out_path, {"constant_memory": True})
    F = _Fmt(wb)
    index_ws = wb.add_worksheet("Teams")
    used = {"teams"}
    infos = []
    for n, (idx, name, path) in enumerate(entries, 1):
        try:
            battle = parse_log(path)
            if not battle.rows:
                raise ValueError("no turns found in the log")
            title = _tab_title(idx, name, used)
            ws = wb.add_worksheet(title)
            infos.append(_write_team_tab(ws, F, battle, title, name, idx))
        except Exception as e:                                     # noqa: BLE001 - report, keep going
            msg = f"#{idx} {name}: {type(e).__name__}: {e}"
            if errors is not None:
                errors.append(msg)
            infos.append(dict(title=None, name=name, index=idx, dpav=None, team_dmg=None, error=str(e)))
        if progress:
            progress(n, len(entries), infos[-1].get("title") or "FAILED")
    _write_index(index_ws, F, infos)
    wb.close()
    return out_path


def _write_index(ws, F, infos):
    g = _Grid()
    g.heights[0] = 26
    g.merge(0, 1, 5, "TEAM BATTLE SHEETS · first logged battle of every team", bold=True, font_size=12, bg_color=C_HEAD)
    g.merge(1, 1, 5, "Tab names: team number + character codes (SW999 = SilverWolf999, YG = Yao Guang, AA = AeonAha, "
                     "PE = Pearl, SX = Sparxie); 'E.S' after a code = eidolon.superimposition, left out at 0.0",
            font_size=8, font_color=C_MUTED, bg_color=C_HEAD)
    for c, t in enumerate(("#", "Team", "DPAV (this battle)", "Total DMG", "Tab"), start=1):
        g.put(2, c, t, bold=True, bg_color=C_HEAD2, font_color=C_TEAL, align="center" if c != 2 else "left")
    for i, info in enumerate(infos):
        r = 3 + i
        bg = C_BG if i % 2 == 0 else C_BG_ALT
        g.put(r, 1, info["index"], bg_color=bg, align="center")
        if info.get("title") is None:
            g.put(r, 2, info["name"], bg_color=bg)
            g.merge(r, 3, 5, "FAILED: " + str(info.get("error"))[:80], bg_color=bg, font_color=C_RED)
            continue
        safe = info["title"].replace("'", "''")
        g.put(r, 2, info["name"], bg_color=bg)
        g.put(r, 3, info["dpav"], bg_color=bg, num_format="#,##0.0", align="center")
        g.put(r, 4, info["team_dmg"], bg_color=bg, num_format="#,##0", align="center")
        g.put(r, 5, _Link(f"internal:'{safe}'!A1", info["title"]), bg_color=bg, font_color=C_TEAL, underline=0)
    bg = F()
    ws.hide_gridlines(2)
    ws.set_column(0, 30, 10, bg)
    ws.set_column(0, 0, 2, bg)
    ws.set_column(1, 1, 5, bg)
    ws.set_column(2, 2, 70, bg)
    ws.set_column(3, 4, 18, bg)
    ws.set_column(5, 5, 32, bg)
    g.emit(ws, F)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    out = sys.argv[1]
    logs = sys.argv[2:]
    items = [(i + 1, os.path.splitext(os.path.basename(p))[0], p) for i, p in enumerate(logs)]
    build_battle_workbook(items, out, progress=lambda n, t, title: print(f"  [{n}/{t}] {title}"))
    print("written:", out)