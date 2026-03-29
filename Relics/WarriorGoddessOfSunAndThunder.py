from MainFunctions import resetUnitAV
from Relic import Relic
from Buff import *
from Healing import *
from Result import Result
from Turn_Text import Turn


class WarriorGoddessOfSunAndThunder(Relic):
    name = "Warrior Goddess of Sun and Thunder"

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("WarriorGoddessSPD",StatTypes.SPD_PERCENT,0.06,self.wearerRole,[AtkType.ALL],1,1,Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        if result.HPGain > 0 and self.setType == 4:
            bl.append(Buff("WarriorGoddessHealSPD", StatTypes.SPD_PERCENT, 0.06, self.wearerRole, [AtkType.ALL], 2, 1, Role.SELF,TickDown.START))
            bl.append(Buff("WarriorGoddessHealCD", StatTypes.CD_PERCENT, 0.15, Role.ALL, [AtkType.ALL], 2, 1,Role.SELF, TickDown.START))
        return bl, dbl, al, dl, hl