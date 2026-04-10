from Relic import Relic
from Buff import *
from Attributes import *
from Result import *
from Character import Character

class EverGloriousMagicalGirl(Relic):
    name = "Ever-Glorious Magical Girl"
    OldPunchline = 0
    stacks = 0

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("MagicalGirlCD",StatTypes.CD_PERCENT,0.16,self.wearerRole,[AtkType.ALL],1,1,Role.SELF,TickDown.PERM))
        if self.setType == 4:
            bl.append(Buff("MagicalGirlShredBanger",StatTypes.SHRED,0.1,self.wearerRole,[AtkType.ELABANGER],1,1,Role.SELF,TickDown.PERM))
            bl.append(Buff("MagicalGirlShredPunch",StatTypes.SHRED,0.1,self.wearerRole,[AtkType.ELAPUNCH],1,1,Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl


    def specialStart(self, special: Special):
        bl, dbl, al, dl, hl = super().specialStart(special)
        if self.setType == 4 and special.specialName == "Sparxie":
            # 1% DEF ignore per 5 Punchline, max 10 stacks = max 10%
            punchline = Character.SharedPunchline
            if self.OldPunchline <= punchline:
                self.stacks += min(int(punchline-self.OldPunchline) / 5, 10)
            self.stacks = min(self.stacks, 10)
            shredVal = self.stacks * 0.01
            bl.append(Buff("MagicalGirlShredPunchlineBanger", StatTypes.SHRED, shredVal, self.wearerRole, [AtkType.ELABANGER], 1, 1, Role.SELF, TickDown.START))
            bl.append(Buff("MagicalGirlShredPunchlinePunch", StatTypes.SHRED, shredVal, self.wearerRole, [AtkType.ELAPUNCH], 1, 1, Role.SELF, TickDown.START))
            self.OldPunchline = Character.SharedPunchline
        if self.setType == 4 and special.specialName == "SilverWolf999":
            # 1% DEF ignore per 5 Punchline, max 10 stacks = max 10%
            punchline = Character.SharedPunchline
            if self.OldPunchline <= punchline:
                self.stacks += min(int(punchline-self.OldPunchline) / 5, 10)
            self.stacks = min(self.stacks, 10)
            shredVal = self.stacks * 0.01
            bl.append(Buff("MagicalGirlShredPunchlineBanger", StatTypes.SHRED, shredVal, self.wearerRole, [AtkType.ELABANGER], 1, 1, Role.SELF, TickDown.START))
            bl.append(Buff("MagicalGirlShredPunchlinePunch", StatTypes.SHRED, shredVal, self.wearerRole, [AtkType.ELAPUNCH], 1, 1, Role.SELF, TickDown.START))
            self.OldPunchline = Character.SharedPunchline
        if self.setType == 4 and special.specialName == "Evanescia":
            # 1% DEF ignore per 5 Punchline, max 10 stacks = max 10%
            punchline = Character.SharedPunchline
            if self.OldPunchline <= punchline:
                self.stacks += min(int(punchline-self.OldPunchline) / 5, 10)
            self.stacks = min(self.stacks, 10)
            shredVal = self.stacks * 0.01
            bl.append(Buff("MagicalGirlShredPunchlineBanger", StatTypes.SHRED, shredVal, self.wearerRole, [AtkType.ELABANGER], 1, 1, Role.SELF, TickDown.START))
            bl.append(Buff("MagicalGirlShredPunchlinePunch", StatTypes.SHRED, shredVal, self.wearerRole, [AtkType.ELAPUNCH], 1, 1, Role.SELF, TickDown.START))
            self.OldPunchline = Character.SharedPunchline
        return bl, dbl, al, dl, hl