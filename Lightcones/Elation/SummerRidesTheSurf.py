from Buff import *
from Lightcone import Lightcone
from Attributes import *
from Character import Character
from Healing import Healing
from Turn_Text import Turn
from math import floor


class SummerRidesTheSurf(Lightcone):
    name = "Summer Rides the Surf"
    path = Path.ELATION
    baseHP = 953
    baseATK = 582
    baseDEF = 529

    def __init__(self, wearerRole, level=1):
        super().__init__(wearerRole, level)
        self._surfWrapped = False
        self._surfLastVariant = None   # variant of the Elation Skill used last time
        self._surfUses = 0
        self._surfWaveSPDone = False

    @staticmethod
    def _variantOf(wearer, tl):
        hook = getattr(wearer, "elaSkillVariant", None)
        names = tuple(t.moveName for t in tl if hasattr(t, "moveName"))
        return (hook, names)

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        CRAmount = 0.03 * self.level + 0.15
        SPDAmount = 0.04 * self.level + 0.20
        ELAAmount = 0.15 * self.level + 0.25
        bl.append(Buff("SummerRidesTheSurfCR", StatTypes.CR_PERCENT, CRAmount, self.wearerRole))

        wearer = getattr(self, "wearer", None)
        if wearer is not None and not self._surfWrapped:
            self._surfWrapped = True
            origEla = wearer.useElaSkill
            origSpecial = wearer.handleSpecialStart

            def elaWithSurf(*args, **kwargs):
                res = list(origEla(*args, **kwargs))
                bl_, tl_ = res[0], res[4]
                variant = self._variantOf(wearer, tl_)
                bl_.append(Buff("SummerRidesTheSurfUpdraft", StatTypes.SPD_PERCENT, SPDAmount,
                                self.wearerRole, [AtkType.ALL], 1, 1, self.wearerRole, TickDown.PERM))

                if self._surfLastVariant is not None and variant != self._surfLastVariant:
                    bl_.append(Buff("SummerRidesTheSurfUptrend", StatTypes.ELA, ELAAmount,
                                    self.wearerRole, [AtkType.ALL], 1, 1, self.wearerRole, TickDown.PERM))

                self._surfLastVariant = variant
                self._surfUses += 1
                if self._surfUses % 3 == 0:
                    tl_.append(Turn(wearer.name, self.wearerRole, -1, Targeting.NA, [AtkType.ALL], [wearer.element],
                                    [0, 0], [0, 0], 0, Scaling.ELA, 1, "SummerRidesTheSurfSP"))
                return tuple(res)

            def specialWithSurf(*args, **kwargs):
                res = list(origSpecial(*args, **kwargs))
                # When the wave starts (battle start): recover 1 Skill Point, once.
                if not self._surfWaveSPDone:
                    self._surfWaveSPDone = True
                    res[4].append(Turn(wearer.name, self.wearerRole, -1, Targeting.NA, [AtkType.ALL],
                                       [wearer.element], [0, 0], [0, 0], 0, Scaling.ELA, 1, "SummerRidesTheSurfWaveSP"))
                return tuple(res)

            wearer.useElaSkill = elaWithSurf
            wearer.handleSpecialStart = specialWithSurf
        return bl, dbl, al, dl, hl, sl