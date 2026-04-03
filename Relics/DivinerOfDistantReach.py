from Relic import Relic
from Buff import *
from Healing import *
from MainFunctions import Special

class DivinerOfDistantReach(Relic):
    name = "Diviner of Distant Reach"
    SPDStat = 1

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("DivinerSPD",StatTypes.SPD_PERCENT,0.06,self.wearerRole,[AtkType.ALL],1,1,Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useElaSkill(self, enemyID = -1):
        bl, dbl, al, dl, hl = super().useElaSkill()
        if self.setType == 4:
            bl.append(Buff("DivinerELA",StatTypes.ELA,0.1,Role.ALL,[AtkType.ALL],1,1,Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl

    def specialStart(self, special: Special):
        bl, dbl, al, dl, hl = super().specialStart(special)
        if self.setType == 4:
            if special.specialName == "YaoGuang" :
                self.SPDStat = special.attr5
                if 160 > self.SPDStat >= 120:
                    bl.append(Buff("DivinerCR", StatTypes.CR_PERCENT, 0.10, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
                elif self.SPDStat >= 160:
                    bl.append(Buff("DivinerCR", StatTypes.CR_PERCENT, 0.18, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
            if special.specialName == "ElationMC" :
                self.SPDStat = special.attr4
                if 160 > self.SPDStat >= 120:
                    bl.append(Buff("DivinerCR", StatTypes.CR_PERCENT, 0.10, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
                elif self.SPDStat >= 160:
                    bl.append(Buff("DivinerCR", StatTypes.CR_PERCENT, 0.18, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl