from Relic import Relic
from Buff import *
from Attributes import *

#

class PoetsDillWreathTribbie(Relic):
    name = "Poet's Dill Wreath"

    def __init__(self, wearerRole, setType, wearerEle = Element.QUANTUM):
        super().__init__(wearerRole, setType)
        self.wearerEle = wearerEle

    def equip(self):
        bl, dbl, al, dl = super().equip()
        if self.wearerEle == Element.QUANTUM:
            bl.append(Buff("PoetQuantumDmg",StatTypes.DMG_PERCENT,0.1,self.wearerRole,[AtkType.ALL]))
        if self.setType == 4:
            bl.append(Buff("PoetSpdDecrease",StatTypes.SPD_PERCENT,-0.8,self.wearerRole,[AtkType.ALL]))
            bl.append(Buff("PoetCrIncrease",StatTypes.CR_PERCENT,0.32,self.wearerRole,[AtkType.ALL]))
        return bl, dbl, al, dl

class PoetsDillWreathCastorice(Relic):
    name = "Poet's Dill Wreath"

    def __init__(self, wearerRole, setType, wearerEle = Element.QUANTUM):
        super().__init__(wearerRole, setType)
        self.wearerEle = wearerEle

    def equip(self):
        bl, dbl, al, dl = super().equip()
        if self.wearerEle == Element.QUANTUM:
            bl.append(Buff("PoetQuantumDmg",StatTypes.DMG_PERCENT,0.1,self.wearerRole,[AtkType.ALL]))
        if self.setType == 4:
            bl.append(Buff("PoetSpdDecrease",StatTypes.SPD_PERCENT,-0.8,self.wearerRole,[AtkType.ALL]))
            bl.append(Buff("PoetCrIncrease", StatTypes.CR_PERCENT, 0.32, self.wearerRole, [AtkType.ALL]))
        return bl, dbl, al, dl