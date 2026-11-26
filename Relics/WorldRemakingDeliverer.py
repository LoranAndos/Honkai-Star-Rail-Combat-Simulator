from Buff import Buff
from Attributes import *
from Relic import Relic
from Character import Character


class WorldRemakingDeliverer(Relic):
    name = "World-Remaking Deliverer"

    def __init__(self, wearerRole: Role, setType: int = 4):
        super().__init__(wearerRole, setType)

    def equip(self):
        bl, dbl, al, dl, hl, sl = super().equip()
        bl.append(Buff("WorldRemakingDelivererCR", StatTypes.CR_PERCENT, 0.08, self.wearerRole))
        return bl, dbl, al, dl, hl, sl

    def _wearerAndMemos(self):
        team = Character._current_player_team or []
        wearer = next((c for c in team if c.role == self.wearerRole), None)
        memos = [c for c in team if wearer is not None and getattr(c, "isMemosprite", False) and getattr(c, "MemoSummonerName", None) == wearer.name]
        return wearer, memos

    def _refresh(self, isSkill: bool, bl: list):
        wearer, memos = self._wearerAndMemos()
        if wearer is None:
            return
        present = bool(memos) and ((isSkill and getattr(wearer, "hasMemosprite", False)) or any(getattr(m, "MemoActive", False) for m in memos))
        HPBuff = 0.24 if present else 0.0
        DMGBuff = 0.15 if present else 0.0
        for role in [self.wearerRole] + [m.role for m in memos]:
            bl.append(Buff("WorldRemakingDelivererHP", StatTypes.HP_PERCENT, HPBuff, role, [AtkType.ALL], 1, 1, self.wearerRole, TickDown.PERM))
        bl.append(Buff("WorldRemakingDelivererDMG", StatTypes.DMG_PERCENT, DMGBuff, Role.ALL, [AtkType.ALL], 1, 1, self.wearerRole, TickDown.PERM))

    def useBsc(self, enemyID=-1):
        bl, dbl, al, dl, hl, sl = super().useBsc(enemyID)
        if self.setType >= 4:
            self._refresh(False, bl)
        return bl, dbl, al, dl, hl, sl

    def useSkl(self, enemyID=-1):
        bl, dbl, al, dl, hl, sl = super().useSkl(enemyID)
        if self.setType >= 4:
            self._refresh(True, bl)
        return bl, dbl, al, dl, hl, sl