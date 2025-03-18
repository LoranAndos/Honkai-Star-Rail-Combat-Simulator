class SpTracker:
    def __init__(self, startingSP, maxSP) -> None:
        self.startingSP = startingSP
        self.maxSP = maxSP
        self.diSP = min(maxSP, startingSP)
        self.spGain = 0
        self.spUsed = 0

    def getDisp(self):
        return self.diSP

    def getSPGain(self):
        return self.spGain

    def getSPUsed(self):
        return self.spUsed

    def addSP(self, num):
        self.spGain += num
        self.diSP = min(self.diSP + num, self.maxSP)

    def redSP(self, num):
        self.spUsed -= num
        self.diSP = max(0, self.diSP + num)


class DmgTracker:
    def __init__(self) -> None:
        self.actionDMG = 0
        self.debuffDMG = 0
        self.weaknessBreakDMG = 0
        self.actionHPGain = 0
        self.actionHPLoss = 0

    def addDebuffDMG(self, dmg: float):
        self.debuffDMG += dmg

    def addActionDMG(self, dmg: float):
        self.actionDMG += dmg

    def addWeaknessBreakDMG(self, dmg: float):
        self.weaknessBreakDMG += dmg

    def addHPGain(self, Healing: float):
        self.actionHPGain += Healing

    def addHPLoss(self, Damage: float):
        self.actionHPLoss += Damage

    def getDebuffDMG(self):
        return self.debuffDMG

    def getActionDMG(self):
        return self.actionDMG

    def getWeaknessBreakDMG(self):
        return self.weaknessBreakDMG

    def getTotalDMG(self):
        return self.actionDMG + self.debuffDMG + self.weaknessBreakDMG

    def getTotalHPGain(self):
        return self.actionHPGain

    def getTotalHPLoss(self):
        return self.actionHPLoss
