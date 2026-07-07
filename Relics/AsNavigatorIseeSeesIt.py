from Relic import Relic
from Buff import *
from Healing import *
from Result import Result
from Turn_Text import Turn
from Result import Special


class AsNavigatorIseeSeesIt(Relic):
    name = "As Navigator Isee Sees It"

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)
        self.Stacks = 1  # starts at 1 (entering combat counts as one stack)

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("NavigatorATK", StatTypes.ATK_PERCENT, 0.12, self.wearerRole, [AtkType.ALL]))
        if self.setType == 4:
            bl.append(Buff("NavigatorDMG", StatTypes.DMG_PERCENT, 0.18 * min(self.Stacks, 3),
                           self.wearerRole, [AtkType.SKL, AtkType.ULT], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl, sl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, hl, sl = super().useSkl(enemyID)
        self.Stacks = min(self.Stacks + 1, 3)
        if self.setType == 4:
            bl.append(Buff("NavigatorDMG", StatTypes.DMG_PERCENT, 0.18 * min(self.Stacks, 3),
                           self.wearerRole, [AtkType.SKL, AtkType.ULT], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl, sl

    def useUlt(self, enemyID=-1):
        bl, dbl, al, dl, hl, sl = super().useUlt(enemyID)
        self.Stacks = max(self.Stacks - 1, 0)
        if self.setType == 4:
            bl.append(Buff("NavigatorDMG", StatTypes.DMG_PERCENT, 0.18 * min(self.Stacks, 3),
                           self.wearerRole, [AtkType.SKL, AtkType.ULT], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl, sl

    def specialStart(self, special: Special):
        bl, dbl, al, dl, hl, sl = super().specialStart(special)
        self.Stacks = max(self.Stacks - 1, 0)
        if self.setType == 4:
            bl.append(Buff("NavigatorDMG", StatTypes.DMG_PERCENT, 0.18 * min(self.Stacks, 3),
                           self.wearerRole, [AtkType.SKL, AtkType.ULT], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl, sl