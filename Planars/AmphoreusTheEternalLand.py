from Buff import Buff
from Attributes import *
from Planar import Planar
from Character import Character


class AmphoreusTheEternalLand(Planar):
    def __init__(self, wearerRole: Role):
        super().__init__(wearerRole)
        self._spdActive = False

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("AmphoreusTheEternalLandCR", StatTypes.CR_PERCENT, 0.08, self.wearerRole))
        return bl, dbl, al, dl, hl, sl

    def _memospritePresent(self) -> bool:
        team = Character._current_player_team or []
        wearer = next((c for c in team if c.role == self.wearerRole), None)
        if wearer is None:
            return False
        return any(getattr(c, "isMemosprite", False) and getattr(c, "MemoSummonerName", None) == wearer.name and getattr(c, "MemoActive", False) for c in team)

    def specialStart(self, special):
        bl, dbl, al, dl, hl, sl = super().specialStart(special)
        present = self._memospritePresent()
        if present != self._spdActive:
            self._spdActive = present
            bl.append(Buff("AmphoreusTheEternalLandSPD", StatTypes.SPD_PERCENT, 0.08 if present else 0.0, Role.ALL,[AtkType.ALL], 1, 1, self.wearerRole, TickDown.PERM))
        return bl, dbl, al, dl, hl, sl