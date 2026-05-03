from Buff import *
from Lightcone import Lightcone
from Turn_Text import Turn
from Result import Result
from Attributes import *
from MainFunctions import countDebuffs

class GoodNightAndSleepWell(Lightcone):
    name = "Good Night and Sleep Well"
    path = Path.NIHILITY
    baseHP = 953
    baseATK = 476
    baseDEF = 331

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)
        self.debuffList = []  # injected from MainFunctions before processTurnList runs

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        if not result.enemiesHit:
            return bl, dbl, al, dl, hl

        # Count debuffs on the primary target (first enemy hit)
        targetEnemy = result.enemiesHit[0]
        debuffCount = countDebuffs(targetEnemy.enemyID, self.debuffList)
        stacks = min(debuffCount, 3)

        if stacks > 0:
            dmgBuff = (self.level * 0.03 + 0.09) * stacks
            bl.append(Buff("GoodNightDMG", StatTypes.DMG_PERCENT, dmgBuff, self.wearerRole,[AtkType.ALL], 1, 1, Role.SELF, TickDown.END))

        return bl, dbl, al, dl, hl