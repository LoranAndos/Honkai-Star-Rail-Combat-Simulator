from Buff import *
from Lightcone import Lightcone
from Attributes import *

class IAmAsYouBehold(Lightcone):
    name = "I Am As You Behold"
    path = Path.DESTRUCTION
    baseHP = 953
    baseATK = 635
    baseDEF = 463

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        atkAmount = self.level * 0.03 + 0.15
        errAmount = self.level * 0.025 + 0.075
        dmgAmount = self.level * 0.18 + 0.54
        CdAmount = self.level * 0.06 + 0.18
        bl.append(Buff("AsYouBeholdATK", StatTypes.ATK_PERCENT, atkAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("AsYouBeholdERR", StatTypes.ERR_PERCENT, errAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        bl.append(Buff("AsYouBeholdDMG", StatTypes.DMG_PERCENT, dmgAmount, self.wearerRole, [AtkType.ULT], 1, 1, Role.SELF, TickDown.PERM))
        #If you end up using with characters other than Saber or Gilgamesh then just use Specials and add conditions for characters.
        bl.append(Buff("AsYouBeholdCD", StatTypes.CD_PERCENT, CdAmount, Role.ALL, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useUlt()
        CdAmount = self.level * 0.06 + 0.18
        bl.append(Buff("AsYouBeholdCD", StatTypes.CD_PERCENT, CdAmount, Role.ALL, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl