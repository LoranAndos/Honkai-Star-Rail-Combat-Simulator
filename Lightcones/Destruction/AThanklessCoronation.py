from Buff import *
from Lightcone import Lightcone
from Attributes import *

class AThanklessCoronation(Lightcone):
    name = "A Thankless Coronation"
    path = Path.DESTRUCTION
    baseHP = 953
    baseATK = 582
    baseDEF = 529

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        cdAmount = self.level * 0.09 + 0.27
        bl.append(Buff("ThanklessCoronationCD", StatTypes.CR_PERCENT, cdAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt()
        atkAmount = self.level * 0.30 + 0.10
        bl.append(Buff("ThanklessCoronationATK", StatTypes.ATK_PERCENT, atkAmount, self.wearerRole, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        #If you end up using with characters other than Saber or Gilgamesh then just use Specials and add conditions for characters.
        bl.append(Buff("ThanklessCoronationERR", StatTypes.ERR_F, 36, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.START))
        bl.append(Buff("ThanklessCoronationATKExtra", StatTypes.ATK_PERCENT, atkAmount, self.wearerRole, [AtkType.ALL], 2, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl