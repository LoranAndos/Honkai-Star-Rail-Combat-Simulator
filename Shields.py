from Attributes import *


class Shield:
    """A shield absorbs incoming damage before it reaches a character's HP.

    Shields behave like Healing in how they are applied (val, scaling, target,
    applier, targeting) but persist like Buffs (turns, tickDown, tdType) and
    track a live absorbable amount (currentAmount) separate from the value
    that creates/refreshes them (val).

    Cap semantics (capValue):
        - None means uncapped.
        - When isDefining=True, the applying source recalculates capValue
          fresh from its own current shield value every time it applies or
          refreshes this shield (e.g. "300% of the shield provided by Skill"
          recalculates 3.0 * currentSkillShieldValue each time Skill is used).
        - Non-defining sources never change capValue; they only add their
          val to currentAmount, clamped to whatever capValue is currently in
          effect.
        - All sources (defining or not) ADD their val to the remaining
          currentAmount, clamped at capValue (or uncapped if capValue is None).
    """

    def __init__(self, name: str, val: float | list, scaling: Scaling, target: Role, applier: Role,
                 targeting: Targeting, capMultiplier: float = None, isDefining: bool = True,
                 turns: int = 1, tickDown: Role = Role.SELF, tdType: TickDown = TickDown.END,
                 atkType: list = None):
        self.name = name
        self.val = val                  # raw value(s): float for pure-scaling shields,
                                        # or [percentVal, flatVal] for mixed shields
                                        # (e.g. [0.20, 400] = 20% ATK + 400 flat)
        self.scaling = scaling          # Scaling.ATK / HP / DEF / Other / MAXHP -- mirrors Healing
        self.target = target            # Role being shielded
        self.applier = applier          # Role of the caster
        self.targeting = targeting      # SINGLE / BLAST / AOE -- mirrors Healing
        self.atkType = atkType if atkType is not None else [AtkType.ALL]  # used for buff-filtering during scaling lookup

        self.capMultiplier = capMultiplier  # e.g. 3.0 for "300% of shield provided by Skill"; None = uncapped
        self.isDefining = isDefining        # whether this application source defines/recalculates the cap

        self.currentAmount = 0.0        # live absorbable shield HP (set once the granted amount is computed)
        self.capValue = None            # the actual numeric cap currently in effect (capMultiplier * defining amount)

        self.turns = turns
        self.tickDown = tickDown        # Role whose turn ticks this shield down
        self.tdType = tdType            # TickDown.START / END / PERM

    def __str__(self) -> str:
        capStr = f"{self.capValue:.1f}" if self.capValue is not None else "Uncapped"
        return (f"{self.name} | Target: {self.target.name} | Current: {self.currentAmount:.1f} | "
                f"Cap: {capStr} | Turns: {self.turns}")

    def getShieldVal(self) -> float | list:
        return self.val

    def reduceTurns(self):
        self.turns -= 1

    def applyAmount(self, grantedAmount: float):
        """Add grantedAmount to currentAmount, recalculating/respecting the cap.

        If this application is defining, capValue is recalculated as
        capMultiplier * grantedAmount (the amount THIS application would
        grant on its own, before adding to any remaining amount). Non-defining
        applications never touch capValue.
        """
        if self.isDefining and self.capMultiplier is not None:
            self.capValue = self.capMultiplier * grantedAmount
        self.currentAmount += grantedAmount
        if self.capValue is not None:
            self.currentAmount = min(self.currentAmount, self.capValue)

    def absorb(self, dmg: float) -> float:
        """Drain dmg from this shield's currentAmount. Returns leftover damage
        that this shield could not absorb (0 if fully absorbed)."""
        if dmg <= 0 or self.currentAmount <= 0:
            return max(0.0, dmg)
        absorbed = min(self.currentAmount, dmg)
        self.currentAmount -= absorbed
        return dmg - absorbed