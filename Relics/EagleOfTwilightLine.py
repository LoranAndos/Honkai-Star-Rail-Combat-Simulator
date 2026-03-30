from Relic import Relic
from Buff import Buff
from Delay_Text import *
from Attributes import *


class EagleOfTwilightLine(Relic):
    name = "Eagle of Twilight Line"

    def __init__(self, wearerRole, setType, wearerEle=Element.WIND):
        super().__init__(wearerRole, setType)
        self.wearerEle = wearerEle

    def equip(self):
        bl, debuffList, advList, delayList = super().equip()
        if self.wearerEle == Element.WIND:
            bl.append(Buff("EagleDMG", StatTypes.DMG_PERCENT, 0.10, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, debuffList, advList, delayList

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl = super().useUlt(enemyID)
        if self.setType == 4:
            al.append(Advance(f"EagleAdv-{self.wearerRole.name}", self.wearerRole, 0.25))
        return bl, dbl, al, dl