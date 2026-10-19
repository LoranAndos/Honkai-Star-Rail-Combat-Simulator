from Buff import *
from Lightcone import Lightcone
from Character import Character
from Attributes import *


class UponTheFirstEchoOfAha(Lightcone):
    name = "Upon the First Echo of Aha"
    path = Path.ELATION
    baseHP = 953
    baseATK = 582
    baseDEF = 529

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)
        self._echoRole = wearerRole
        self._echoOnCooldown = False
        self._echoWrapped = False
        self._echoSpdApplied = False

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        BaseSPDAmount = self.level * 2 + 10
        wearer = getattr(self, "wearer", None)
        if wearer is not None and not self._echoSpdApplied:
            wearer.baseSPD = wearer.baseSPD + BaseSPDAmount
            self._echoSpdApplied = True
        # The 1-turn interval resets whenever the wearer starts a new turn.
        if wearer is not None and not self._echoWrapped:
            originalTakeTurn = wearer.takeTurn
            def takeTurnWithEcho(*args, **kwargs):
                self._echoOnCooldown = False
                return originalTakeTurn(*args, **kwargs)
            wearer.takeTurn = takeTurnWithEcho
            self._echoWrapped = True
        return bl, dbl, al, dl, hl, sl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, hl, sl = super().useSkl(enemyID)
        PunchlineAmount = self.level * 2 + 8
        ShredAmount = self.level * 0.02 + 0.14
        if not self._echoOnCooldown:
            self._echoOnCooldown = True
            Character.SharedPunchline += PunchlineAmount
            # Then all allies ignore 16% of the enemy target's DEF for the rest of the combat.
            # Same buff name -> overwrites instead of stacking.
            bl.append(Buff("UponTheFirstEchoOfAhaShred", StatTypes.SHRED, ShredAmount, Role.ALL,
                           [AtkType.ALL], 1, 1, self._echoRole, TickDown.PERM))
        return bl, dbl, al, dl, hl, sl