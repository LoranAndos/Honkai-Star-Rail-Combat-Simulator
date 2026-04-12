from Buff import Buff
from Attributes import *
from Planar import Planar
from MainFunctions import Special
from Result import Result
from Turn_Text import Turn


class PunklordeStageZero(Planar):
    name = "Punklorde Stage Zero"
    ELAStat = 0

    def __init__(self, wearerRole: Role):
        super().__init__(wearerRole)
        self.spConsumedThisTurn = 0

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        bl.append(Buff("PunklordeELA", StatTypes.ELA, 0.08, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def specialStart(self, special: Special):
        bl, dbl, al, dl, hl = super().specialStart(special)
        if special.specialName == "Evanescia" :
            self.ELAStat = special.attr3
            if  self.ELAStat >= 0.40:
                bl.append(Buff("PunklordeCDFirst", StatTypes.CD_PERCENT, 0.20, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
            if self.ELAStat >= 0.80:
                bl.append(Buff("PunklordeCDSecond", StatTypes.CD_PERCENT, 0.12, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        elif special.specialName == "SilverWolf999":
            self.ELAStat = special.attr3
            if  self.ELAStat >= 0.40:
                bl.append(Buff("PunklordeCDFirst", StatTypes.CD_PERCENT, 0.20, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
            if self.ELAStat >= 0.80:
                bl.append(Buff("PunklordeCDSecond", StatTypes.CD_PERCENT, 0.12, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        if turn.charName == "Evanescia" :
            self.ELAStat = self.ELAStat
            if  self.ELAStat >= 0.40:
                bl.append(Buff("PunklordeCDFirst", StatTypes.CD_PERCENT, 0.20, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
            elif self.ELAStat >= 0.80:
                bl.append(Buff("PunklordeCDSecond", StatTypes.CD_PERCENT, 0.12, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        elif turn.charName == "SilverWolf999":
            self.ELAStat = self.ELAStat
            if  self.ELAStat >= 0.40:
                bl.append(Buff("PunklordeCDFirst", StatTypes.CD_PERCENT, 0.20, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
            if self.ELAStat >= 0.80:
                bl.append(Buff("PunklordeCDSecond", StatTypes.CD_PERCENT, 0.12, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF,TickDown.PERM))
        return bl, dbl, al, dl, hl