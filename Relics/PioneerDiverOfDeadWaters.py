from Buff import Buff
from Attributes import *
from Relic import Relic
from Result import Special


class PioneerDiverOfDeadWaters(Relic):
    name = "Pioneer Diver of Dead Waters"

    targetDebuffs = 0

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        if self.setType == 4:
            bl.append(
                Buff("PioneerCR", StatTypes.CR_PERCENT, 0.04, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl


class PioneerRatio(PioneerDiverOfDeadWaters):
    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def specialStart(self, special: Special):
        bl, dbl, al, dl, hl = super().specialStart(special)
        if self.setType == 4:
            bl.append(Buff("PioneerBonusCR", StatTypes.CR_PERCENT, 0.04, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                           TickDown.PERM))
            if special.specialName == "Ratio":
                self.targetDebuffs = special.attr1
                if self.targetDebuffs >= 1:
                    bl.append(Buff("PioneerDMG", StatTypes.DMG_PERCENT, 0.12, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                                   TickDown.PERM))
                    if self.targetDebuffs == 2:
                        bl.append(
                            Buff("PioneerCD", StatTypes.CD_PERCENT, 0.16, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                                 TickDown.PERM))
                    elif self.targetDebuffs >= 3:
                        bl.append(
                            Buff("PioneerCD", StatTypes.CD_PERCENT, 0.24, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                                 TickDown.PERM))
                else:
                    bl.append(Buff("PioneerCD", StatTypes.CD_PERCENT, 0.00, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                                   TickDown.PERM))
        return bl, dbl, al, dl, hl

class PioneerAcheron(PioneerDiverOfDeadWaters):
    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def specialStart(self, special: Special):
        bl, dbl, al, dl, hl = super().specialStart(special)
        if self.setType == 4:
            bl.append(Buff("PioneerBonusCR", StatTypes.CR_PERCENT, 0.04, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                           TickDown.PERM))
            if special.specialName == "Acheron":
                self.targetDebuffs = special.attr2[0]
                if self.targetDebuffs >= 1:
                    bl.append(Buff("PioneerDMG", StatTypes.DMG_PERCENT, 0.12, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                                   TickDown.PERM))
                    if self.targetDebuffs == 2:
                        bl.append(
                            Buff("PioneerCD", StatTypes.CD_PERCENT, 0.16, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                                 TickDown.PERM))
                    elif self.targetDebuffs >= 3:
                        bl.append(
                            Buff("PioneerCD", StatTypes.CD_PERCENT, 0.24, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                                 TickDown.PERM))
                else:
                    bl.append(Buff("PioneerCD", StatTypes.CD_PERCENT, 0.00, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                                   TickDown.PERM))
        return bl, dbl, al, dl, hl

class PioneerCipher(PioneerDiverOfDeadWaters):
    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def specialStart(self, special: Special):
        bl, dbl, al, dl, hl = super().specialStart(special)
        if self.setType == 4:
            bl.append(Buff("PioneerBonusCR", StatTypes.CR_PERCENT, 0.04, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                           TickDown.PERM))
            if special.specialName == "Cipher":
                self.targetDebuffs = special.attr2[0]
                if self.targetDebuffs >= 1:
                    bl.append(Buff("PioneerDMG", StatTypes.DMG_PERCENT, 0.12, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                                   TickDown.PERM))
                    if self.targetDebuffs == 2:
                        bl.append(
                            Buff("PioneerCD", StatTypes.CD_PERCENT, 0.16, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                                 TickDown.PERM))
                    elif self.targetDebuffs >= 3:
                        bl.append(
                            Buff("PioneerCD", StatTypes.CD_PERCENT, 0.24, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                                 TickDown.PERM))
                else:
                    bl.append(Buff("PioneerCD", StatTypes.CD_PERCENT, 0.00, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,
                                   TickDown.PERM))
        return bl, dbl, al, dl, hl