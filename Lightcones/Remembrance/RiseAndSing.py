from Buff import *
from Lightcone import Lightcone
from Attributes import *
from Delay_Text import Advance


class RiseAndSing(Lightcone):
    name = "Rise and Sing"
    path = Path.REMEMBRANCE
    baseHP = 1164
    baseATK = 582
    baseDEF = 396

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        HPAmount = 0.075 * self.level + 0.225
        AdvanceAmount = 0.025 * self.level + 0.275
        SpdAmount = 0.05 * self.level + 0.15
        bl.append(Buff("RiseAndSingHP", StatTypes.HP_PERCENT, HPAmount, self.wearerRole))
        al.append(Advance("RiseAndSingADV", self.wearerRole, AdvanceAmount))
        bl.append(Buff("RiseAndSingNewMelody", StatTypes.SPD_PERCENT, SpdAmount, Role.ALL, [AtkType.ALL],2, 1, self.wearerRole, TickDown.END))
        return bl, dbl, al, dl, hl, sl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl, sl = super().useUlt(enemyID)
        bl.append(Buff("RiseAndSingSP", StatTypes.SKLPT, 1, self.wearerRole, [AtkType.ALL], 1, 1, self.wearerRole, TickDown.START))
        return bl, dbl, al, dl, hl, sl