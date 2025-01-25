from Attributes import *

class Delay:
    def __init__(self, name: str, delayPercent: float, target, reqBroken: bool, stackable: bool):
        self.name = name
        self.delayPercent = delayPercent
        self.target = target
        self.reqBroken = reqBroken
        self.stackable = stackable

    def __str__(self) -> str:
        return f"{self.name} | Delay%: {self.delayPercent} | Target: {self.target} | ReqBroken: {self.reqBroken} | Stackable: {self.stackable}"


class Advance:
    def __init__(self, name: str, targetRole: Role, advPercent: float):
        self.name = name
        self.targetRole = targetRole
        self.advPercent = advPercent

    def __str__(self) -> str:
        return f"{self.name} | Adv%: {self.advPercent} | Target: {self.targetRole}"