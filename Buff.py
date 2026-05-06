from tkinter import BooleanVar

from Attributes import *

class Buff:
    # noinspection PyDefaultArgument
    def __init__(self, name: str, buffType: StatTypes, val: float, target: Role, atkType: list = [AtkType.ALL],
                 turns: int = 1, stackLimit: int = 1, tickDown: Role = Role.SELF, tdType: TickDown = TickDown.PERM,
                 reqBroken: bool = False):
        self.reqBroken = reqBroken
        self.name = name
        self.buffType = buffType
        self.val = val
        self.target = target
        self.atkType = atkType
        self.storedTurns = turns
        self.turns = self.storedTurns
        self.stackLimit = stackLimit
        self.stacks = 1
        self.tickDown = tickDown
        self.tdType = tdType

    def __str__(self) -> str:
        res = f"{self.name} | {self.buffType.value} | Stacks: {self.stacks} | Value: {self.stacks * self.val:.3f} | "
        res += f"Remaining Turns: {self.turns} | TickDown: {self.tickDown.name}, {self.tdType.name} | "
        res += f"Target: {self.target.name} | Affects: {[a.name for a in self.atkType]}"
        return res

    def reduceTurns(self) -> None:
        self.turns = self.turns - 1

    def refreshTurns(self) -> None:
        self.turns = self.storedTurns

    def incStack(self) -> None:
        self.refreshTurns()
        if self.stacks == self.stackLimit:
            return
        self.stacks = self.stacks + 1

    def getBuffVal(self) -> float:
        return self.val * self.stacks

    def atMaxStacks(self) -> bool:
        return True if (self.stacks == self.stackLimit) else False

    def updateBuffVal(self, val: float):
        self.val = val


class Debuff:
    # noinspection PyDefaultArgument
    def __init__(self, name: str, charRole: Role, debuffType: StatTypes, val: float, target, atkType: list, turns: int,
                 stackLimit: int = 1, targeting: Targeting = Targeting.SINGLE,isDot: bool = False, dotSplit: list[float] = [0, 0], isBlast: bool = False,
                 validFor=[Role.ALL]):
        self.name = name
        self.charRole = charRole
        self.debuffType = debuffType
        self.val = val
        self.target = target
        self.atkType = atkType
        self.storedTurns = turns
        self.turns = self.storedTurns
        self.stackLimit = stackLimit
        self.stacks = 1
        self.targeting = targeting
        self.isDot = isDot
        self.dotSplit = dotSplit
        self.isBlast = isBlast
        self.dotMul = 0
        self.validFor = validFor

    def __str__(self) -> str:
        res = f"{self.name} | From: {self.charRole.name} | {self.debuffType.value} | Stacks: {self.stacks} | Value: {self.stacks * self.val:.3f} | "
        res += f"Remaining Turns: {self.turns} | Target: {self.target} | Targeting: {self.targeting.value} | Affects: {[a.name for a in self.atkType]} | DOT: {self.isDot} | Blast: {self.isBlast}"
        return res

    def reduceTurns(self) -> None:
        self.turns = self.turns - 1

    def refreshTurns(self) -> None:
        self.turns = self.storedTurns

    def incStack(self) -> None:
        self.refreshTurns()
        if self.stacks == self.stackLimit:
            return
        self.stacks = self.stacks + 1

    def getDebuffVal(self) -> float:
        if self.name == "AshenRoasted":
            return self.val + self.stacks * (self.val / 2)
        return self.val * self.stacks

    def atMaxStacks(self) -> bool:
        return True if (self.stacks == self.stackLimit) else False

    # Small example for debuffs

    # Single target — specific enemy
    #dbl.append(Debuff("MyDebuff", self.role, StatTypes.VULN, 0.20, enemyID, [AtkType.ALL], 2,
    #                  targeting=Targeting.SINGLE))

    # Single target — default/best enemy (sim picks)
    #dbl.append(Debuff("MyDebuff", self.role, StatTypes.VULN, 0.20, -1, [AtkType.ALL], 2,
    #                  targeting=Targeting.SINGLE))

    # Blast — main + adjacent
    #dbl.append(Debuff("MyDebuff", self.role, StatTypes.SHRED, 0.20, enemyID, [AtkType.ALL], 2,
    #                  targeting=Targeting.BLAST))

    # AOE — all enemies (replaces old Role.ALL)
    #dbl.append(Debuff("MyDebuff", self.role, StatTypes.VULN, 0.20, -1, [AtkType.ALL], 2,
    #                  targeting=Targeting.AOE))