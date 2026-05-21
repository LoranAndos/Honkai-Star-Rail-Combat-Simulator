from Relic import Relic
from Buff import *
from Attributes import *


class PrisonerInDeepConfinement(Relic):
    name = "Prisoner in Deep Confinement"

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl, hl  = super().equip()
        bl.append(
            Buff("PrisonerATK", StatTypes.ATK_PERCENT, 0.12, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        if self.setType == 4:
            dbl.append(
                Debuff("PrisonerSHRED", self.wearerRole, StatTypes.SHRED, 0.18, Role.ALL, [AtkType.ALL], 1000, 1, Targeting.AOE,False,
                       [0, 0], False))
        return bl, dbl, al, dl, hl