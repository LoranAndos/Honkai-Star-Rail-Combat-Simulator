# src: Who is taking the turn DPS/SUBDPS/SUP/SUS/MEMO
# targetID: Enemy ID to be attacked, middle enemy if it is a blast attack
# targeting: ST, BLAST, AOE, NA | NA refers to a non-attacking move
# atkType: BSC, SKL, ULT, FUA, MEMO, NA
# element: WIN, FIR, ICE, LNG, PHY, IMG, QUA
# dmgSplit: Base multiplier split [main, adjacent], set adjacent to 0 for ST and AOE attacks
# brkSplit: Toughness reduction split [main, adjacent], set adjacent to 0 for ST and AOE attacks
from Attributes import *

class Turn:
    def __init__(self, charName: str, charRole: Role, targetID: int, targeting: Targeting, atkType: list, element: list,
                 dmgSplit: list, brkSplit: list, errGain: float, scaling: Scaling, spChange: int, moveName: str,
                 omniBreak: bool = False, omniBreakMod: float = 1.0):
        self.charName = charName
        self.charRole = charRole
        self.targetID = targetID
        self.targeting = targeting
        self.atkType = atkType
        self.element = element
        self.dmgSplit = dmgSplit
        self.brkSplit = brkSplit
        self.errGain = errGain
        self.scaling = scaling
        self.spChange = spChange
        self.moveName = moveName
        self.omniBreak = omniBreak
        self.omniBreakMod = omniBreakMod

    def __str__(self) -> str:
        res = f"{self.moveName} | {self.charName} | {self.charRole.name} | "
        res += f"{self.targeting.value} attack | {[e.value for e in self.element]} | {[a.name for a in self.atkType]} | "
        res += f"Scaling: {self.scaling.name} | TargetID: {self.targetID} | "
        res += f"DMG/BREAK Splits: {self.dmgSplit}/{self.brkSplit} | "
        res += f"Energy Gained: {self.errGain}"
        return res