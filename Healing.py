from Attributes import *

class Healing:
    def __init__(self, name: str, val: list, scaling: Scaling, target: Targeting, stackLimit: int = 1,tickDown: Role = Role.SELF,
                 turns: int = 1,tdType: TickDown = TickDown.PERM):
        self.name = name
        self.val = val
        self.scaling = scaling
        self.target = target
        self.stackLimit = stackLimit
        self.tickDown = tickDown
        self.storedTurns = turns
        self.turns = self.storedTurns
        self.tickDown = tickDown
        self.tdType = tdType

    def __str__(self) -> str:
        res = f"{self.name} | Healing Scaling: { self.val:.3f} | "
        res += f"Remaining Turns: {self.turns} | TickDown: {self.tickDown.name}, {self.tdType.name} | "
        res += f"Target: {self.target.name}"
        return res

    def reduceTurns(self) -> None:
        self.turns = self.turns - 1

    def refreshTurns(self) -> None:
        self.turns = self.storedTurns

    def getHealingVal(self) -> list:
        return self.val

    def updateBuffVal(self, val: float):
        self.val = val
