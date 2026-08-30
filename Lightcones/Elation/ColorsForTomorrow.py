from Buff import *
from Lightcone import Lightcone
from Attributes import *
from Character import Character
from Healing import Healing
from math import floor

class ColorsForTomorrow(Lightcone):
    name = "Colors for Tomorrow"
    path = Path.ELATION
    baseHP = 1058
    baseATK = 476
    baseDEF = 595

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        DefBuff = self.level * 0.12 + 0.36
        bl.append(Buff("ColorsDef", StatTypes.DEF_PERCENT, DefBuff, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl, sl

    def useElaSkill(self, enemyID = -1):
        bl, dbl, al, dl, hl, sl = super().equip()
        VulnAmount = self.level * 0.025 + 0.075
        HealAmount = self.level * 0.01 + 0.09
        dbl.append(Debuff("ColorsELASkillVuln", self.wearerRole, StatTypes.VULN, VulnAmount, Role.ALL, [AtkType.ALL], 3, 1, Targeting.AOE,False, [0, 0], False))
        hl.append(Healing("ColorsELASkillHeal", [HealAmount, 0], Scaling.DEF, Role.ALL, self.wearerRole, Targeting.AOE))

        otherElationCount = sum(
            1 for c in (Character._current_player_team or [])
            if c.path == Path.ELATION and c.role != self.wearerRole
        )
        if otherElationCount > 0:
            teamVulnAmount = otherElationCount * (self.level * 0.01 + 0.03)
            dbl.append(Debuff("ColorsTeamElationVuln", self.wearerRole, StatTypes.VULN, teamVulnAmount, Role.ALL,[AtkType.ALL], 3, 1, Targeting.AOE, False, [0, 0], False))

        return bl, dbl, al, dl, hl, sl