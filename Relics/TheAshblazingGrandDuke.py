from Relic import Relic
from Buff import Buff
from Attributes import *


class DukeTopaz(Relic):
    name = "The Ashblazing Grand Duke"

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(
            Buff("DukeDMG", StatTypes.DMG_PERCENT, 0.20, self.wearerRole, [AtkType.FUA], 1, 1, Role.SELF, TickDown.PERM))
        if self.setType == 4:
            bl.append(Buff("DukeBasicATK", StatTypes.ATK_PERCENT, 0.06, self.wearerRole, [AtkType.BSC], 1, 1, Role.SELF,
                           TickDown.PERM))
            bl.append(Buff("DukeFuaATK", StatTypes.ATK_PERCENT, 0.24, self.wearerRole, [AtkType.TOPAZFUA], 1, 1, Role.SELF,
                           TickDown.PERM))
            bl.append(Buff("DukeUltATK", StatTypes.ATK_PERCENT, 0.312, self.wearerRole, [AtkType.TOPAZULT], 1, 1, Role.SELF,
                           TickDown.PERM))
        return bl, dbl, al, dl, hl


class DukeFeixiao(Relic):
    name = "The Ashblazing Grand Duke"

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(
            Buff("DukeDMG", StatTypes.DMG_PERCENT, 0.20, self.wearerRole, [AtkType.FUA], 1, 1, Role.SELF, TickDown.PERM))
        if self.setType == 4:
            bl.append(Buff("DukeFuaATK", StatTypes.ATK_PERCENT, 0.06, self.wearerRole, [AtkType.DUKEFUA], 1, 1, Role.SELF,
                           TickDown.PERM))
            bl.append(Buff("DukeUltATK", StatTypes.ATK_PERCENT, 0.3543, self.wearerRole, [AtkType.DUKEULT], 1, 1, Role.SELF,
                           TickDown.PERM))
        return bl, dbl, al, dl, hl


class DukeMoze(Relic):
    name = "The Ashblazing Grand Duke"

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(
            Buff("DukeDMG", StatTypes.DMG_PERCENT, 0.20, self.wearerRole, [AtkType.FUA], 1, 1, Role.SELF, TickDown.PERM))
        if self.setType == 4:
            bl.append(Buff("DukeFuaATK", StatTypes.ATK_PERCENT, 0.288, self.wearerRole, [AtkType.DUKEFUA], 1, 1, Role.SELF,
                           TickDown.PERM))
            bl.append(Buff("DukeUltATK", StatTypes.ATK_PERCENT, 0.06, self.wearerRole, [AtkType.DUKEULT], 1, 1, Role.SELF,
                           TickDown.PERM))
        return bl, dbl, al, dl, hl


class DukeJY(Relic):
    name = "The Ashblazing Grand Duke"

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(
            Buff("DukeDMG", StatTypes.DMG_PERCENT, 0.20, self.wearerRole, [AtkType.FUA], 1, 1, Role.SELF, TickDown.PERM))
        if self.setType == 4:
            bl.append(
                Buff("DukeFuaATK", StatTypes.ATK_PERCENT, 0.312, self.wearerRole, [AtkType.FUA], 1, 1))  # lightning lord
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn, result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        if turn.moveName == "LightningLordFUA" and self.setType == 4:
            bl.append(
                Buff("DukeATK", StatTypes.ATK_PERCENT, 0.48, self.wearerRole, [AtkType.BSC, AtkType.SKL, AtkType.ULT], 3, 1,
                     tdType=TickDown.END))
        return bl, dbl, al, dl, hl

class DukeAshveil(Relic):
    name = "The Ashblazing Grand Duke"

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(
            Buff("DukeDMG", StatTypes.DMG_PERCENT, 0.20, self.wearerRole, [AtkType.FUA], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def useFua(self, enemyID=-1):
        bl, dbl, al, dl, hl = super().useFua(enemyID)
        if self.setType == 4:
            bl.append(Buff("DukeATK", StatTypes.ATK_PERCENT, 0.48, self.wearerRole, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, hl
