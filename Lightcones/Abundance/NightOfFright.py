from Buff import Buff
from Delay_Text import *
from Lightcone import Lightcone
from Healing import Healing
from Turn_Text import Turn
from Result import Result

class NightOfFright(Lightcone):
    name = "Night of Fright"
    path = Path.ABUNDANCE
    baseHP = 1164
    baseATK = 476
    baseDEF = 529

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        err = self.level * 0.02 + 0.10
        bl.append(Buff("NightERR", StatTypes.ERR_PERCENT, err, self.wearerRole))
        return bl, dbl, al, dl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().allyTurn(turn, result)
        # When any ally uses their Ultimate, heal the ally with lowest HP
        if turn.moveName in UltimateList:
            HealAmount = self.level * 0.01 + 0.09
            # Target Role.ALL with Targeting.SINGLE — parseHealing will find lowest HP target
            hl.append(Healing("NightUltHeal", [HealAmount, 0], Scaling.HP,
                             Role.ALL, self.wearerRole, Targeting.SINGLE))
        # When wearer provides healing, buff the healed ally's ATK
        if result.HPGain > 0 and result.charRole == self.wearerRole:
            atkBuff = self.level * 0.004 + 0.02  # 2.4% at S1
            bl.append(Buff("NightATK", StatTypes.ATK_PERCENT, atkBuff, Role.ALL,
                          [AtkType.ALL], 2, 5, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, tl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, tl, hl = super().ownTurn(turn, result)
        # Wearer's own ult also triggers the heal
        if AtkType.ULT in turn.atkType:
            HealAmount = self.level * 0.01 + 0.09
            hl.append(Healing("NightUltHeal", [HealAmount, 0], Scaling.MAXHP,Role.ALL, self.wearerRole, Targeting.SINGLE))
        # When wearer provides healing, buff the healed ally's ATK
        if result.HPGain > 0:
            atkBuff = self.level * 0.004 + 0.02
            bl.append(Buff("NightATK", StatTypes.ATK_PERCENT, atkBuff, Role.ALL,[AtkType.ALL], 2, 5, Role.SELF, TickDown.END))
        return bl, dbl, al, dl, tl, hl