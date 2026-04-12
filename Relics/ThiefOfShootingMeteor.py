from Buff import Buff
from Relic import Relic
from Result import Result
from Turn_Text import *


class ThiefOfShootingMeteor(Relic):
    name = "Thief of Shooting Meteor"

    def __init__(self, wearerRole, setType):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(
            Buff("ThiefBE", StatTypes.BE_PERCENT, 0.32 if self.setType == 4 else 0.16, self.wearerRole, [AtkType.ALL], 1, 1,
                 Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        if self.setType == 4 and result.brokenEnemy:
            bl.append(
                Buff("ThiefEnergy", StatTypes.ERR_T, 3.0, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl
