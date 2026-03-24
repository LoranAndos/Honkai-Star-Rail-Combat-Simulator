from Healing import *
from Lightcone import Lightcone
from MainFunctions import getCharMaxHP
from Turn_Text import Turn
from Attributes import *

class Defense(Lightcone):
    name = "Defense"
    path = Path.PRESERVATION
    baseHP = 953
    baseATK = 265
    baseDEF = 265

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def useUlt(self, enemyID=-1):
        bl, dl, al, dl, hl = super().useUlt(enemyID)
        HealAmount = (self.level * 0.03 + 0.15)
        hl.append(Healing("DefenseHeal",[HealAmount,0],Scaling.HP,self.wearerRole,self.wearerRole,Targeting.SINGLE))
        return bl, dl, al, dl, hl