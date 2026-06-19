from Buff import *
from Lightcone import Lightcone
from Attributes import *
from Turn_Text import Turn
from Result import Result

class FlickeringStars(Lightcone):
    name = "Flickering Stars"
    path = Path.ERUDITION
    baseHP = 847
    baseATK = 635
    baseDEF = 529

    def __init__(self, wearerRole, level=5):
        super().__init__(wearerRole, level)

    def equip(self):
        bl, dbl, al, dl, hl = super().equip()
        CRAmount = self.level * 0.03 + 0.15
        bl.append(Buff("FlickeringStarsCR", StatTypes.CR_PERCENT, CRAmount, self.wearerRole, [AtkType.ALL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def ownTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().ownTurn(turn, result)
        TeamShred = self.level * 0.04 + 0.16
        SKLDmgAount = self.level * 0.10 + 0.50
        if turn.moveName == "ArcherSkill" or (turn.moveName == "RinTohsakaSkillSingle" and turn.spChange <= -4):
            bl.append(Buff("FlickeringStarsTeamShred", StatTypes.SHRED, TeamShred, Role.ALL, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
            bl.append(Buff("FlickeringStarsDMG", StatTypes.DMG_PERCENT, SKLDmgAount, self.wearerRole, [AtkType.SKL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl

    def allyTurn(self, turn: Turn, result: Result):
        bl, dbl, al, dl, hl = super().allyTurn(turn, result)
        TeamShred = self.level * 0.04 + 0.16
        SKLDmgAount = self.level * 0.10 + 0.50
        if turn.moveName == "ArcherSkill" or (turn.moveName == "RinTohsakaSkillSingle" and turn.spChange <= -4):
            bl.append(Buff("FlickeringStarsTeamShred", StatTypes.SHRED, TeamShred, Role.ALL, [AtkType.ALL], 3, 1, Role.SELF, TickDown.END))
            bl.append(Buff("FlickeringStarsDMG", StatTypes.DMG_PERCENT, SKLDmgAount, self.wearerRole, [AtkType.SKL], 1, 1, Role.SELF, TickDown.PERM))
        return bl, dbl, al, dl, hl