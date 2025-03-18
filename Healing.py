from Attributes import *

class Healing:
    def __init__(self, name: str, val: list, scaling: Scaling, target: Role, applier: Role,targeting: Targeting):
        self.name = name
        self.val = val
        self.scaling = scaling
        self.target = target
        self.applier = applier
        self.targeting = targeting


    def __str__(self) -> str:
        res = f"{self.name} | Targeting: {self.targeting} | Healing Value: {self.val} | "
        res += f"Target: {self.target.name}"
        return res

    def getHealingVal(self) -> list:
        return self.val

    def updateHealVal(self, val: float):
        self.val = val
