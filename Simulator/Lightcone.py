from Equipment import Equipment
from Attributes import *

class Lightcone(Equipment):
    name = "Lightcone"
    path = "None"
    baseHP = 0
    baseATK = 0
    baseDEf = 0

    def __init__(self, wearerRole: Role, level: int):
        super().__init__(wearerRole)
        self.level = level

    def __str__(self):
        return f"{self.name} S{self.level}"