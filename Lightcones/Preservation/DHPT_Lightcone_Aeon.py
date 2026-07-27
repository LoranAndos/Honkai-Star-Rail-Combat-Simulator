from Buff import *
from Lightcone import Lightcone
from Attributes import *
from HPChecks import getCharHPRatio
from Turn_Text import Turn
from Result import Result

class DHPT_Lightcone_Aeon(Lightcone):
    name = "Dan Heng Permansor Terrae Lightcone Aeon"
    path = Path.DESTRUCTION
    baseHP = 1058
    baseATK = 529
    baseDEF = 397

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)