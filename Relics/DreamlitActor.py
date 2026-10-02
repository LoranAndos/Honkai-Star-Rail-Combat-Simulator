from Relic import Relic
from Buff import *
from Healing import *
from MainFunctions import Special
from Character import Character

class DreamlitActor(Relic):
    name = "Dreamlit Actor"
    BangerStat = 1
    ExtraBuff = False

    def __init__(self, wearerRole, setType, targetRole=Role.DPS):
        super().__init__(wearerRole, setType)
        self.targetRole = targetRole

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("DreamlitSPD",StatTypes.SPD_PERCENT,0.06,self.wearerRole,[AtkType.ALL],1,1,Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl, sl

    def useUlt(self, enemyID = -1):
        bl, dbl, al, dl, hl, sl = super().useSkl()
        if self.setType == 4:
            bl.append(Buff(f"DreamlitELA{self.wearerRole}", StatTypes.ELA,0.16, self.targetRole,[AtkType.ALL],3,1,Role.SELF, TickDown.END))
            if self.ExtraBuff == True:
                bl.append(Buff(f"DreamlitCD{self.wearerRole}", StatTypes.CD_PERCENT, 0.12, Role.ALL, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl, sl

    def specialStart(self, special: Special):
        bl, dbl, al, dl, hl, sl = super().specialStart(special)
        if self.setType == 4:
            if special.specialName == "Pearl" :
                pearl = next((c for c in (Character._current_player_team or []) if c.name == "Pearl"), None)
                self.targetRole = pearl.targetRole
                self.BangerStat = special.attr5
                if self.BangerStat >= 10:
                    self.ExtraBuff = True
            if special.specialName == "ElationMC" :
                ElationMC = next((c for c in (Character._current_player_team or []) if c.name == "ElationMC"), None)
                self.targetRole = ElationMC.targetRole
                self.BangerStat = special.attr5
                if self.BangerStat >= 10:
                    self.ExtraBuff = True
        return bl, dbl, al, dl, hl, sl