from Buff import *
from Buff import Buff, Debuff
from Delay_Text import *
from Delay_Text import Advance, Delay
from Healing import Healing
from Shields import Shield
from Result import *
from Turn_Text import Turn
from Character import Character
import logging
logger = logging.getLogger(__name__)

class Summon:
    name = "Summon"
    element = None
    currSPD = 100
    currAV = 10000 / currSPD
    maxHP = 0
    currHP = 0
    currEnergy = 0
    maxEnergy = 0
    breakMidTurn = False  # if True, summon acts immediately when AV hits 0 mid-processTurnList
                         # set to False for summons that should only act after a full turn ends

    def __init__(self, ownerRole: Role, role: Role) -> None:
        self.ownerRole = ownerRole
        self.role = role
        self.priority = 0

    @staticmethod
    def isChar() -> bool:
        return True

    @staticmethod
    def isSummon() -> bool:
        return True

    def takeTurn(self) -> tuple[list[Buff], list[Debuff], list[Advance], list[Delay], list[Turn], list[Healing], list[Shield]]:
        return [], [], [], [], [], [], []

    def standardAVred(self, av: float):
        self.currAV = max(0.0, self.currAV - av)

    def reduceAV(self, reduceValue: float):
        self.currAV = max(0.0, self.currAV - reduceValue)

    def allyTurn(self, turn: Turn, result: Result) -> tuple[
        list[Buff], list[Debuff], list[Advance], list[Delay], list[Turn], list[Healing], list[Shield]]:
        return [], [], [], [], [], [], []


class Numby(Summon):
    name = "Numby"
    element = Element.FIRE
    scaling = Scaling.ATK
    currSPD = 80
    baseSPD = 80
    currAV = 10000 / currSPD

    def __init__(self, ownerRole: Role, role: Role) -> None:
        super().__init__(ownerRole, role)

    def takeTurn(self):
        bl, dbl, al, dl, tl, hl, sl = super().takeTurn()
        tl.append(Turn(self.name, self.ownerRole, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                       self.scaling, 0, "NumbyGoGo"))
        return bl, dbl, al, dl, tl, hl, sl


class Fuyuan(Summon):
    name = "Fuyuan"
    element = Element.FIRE
    scaling = Scaling.ATK
    currSPD = 90
    baseSPD = 90
    currAV = 10000 / currSPD

    def __init__(self, ownerRole: Role, role: Role) -> None:
        super().__init__(ownerRole, role)

    def takeTurn(self):
        bl, dbl, al, dl, tl, hl, sl = super().takeTurn()
        tl.append(Turn(self.name, self.ownerRole, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                       self.scaling, 0, "FuyuanGoGo"))
        return bl, dbl, al, dl, tl, hl, sl


class DeHenshin(Summon):
    name = "de-Henshin!"
    element = Element.FIRE
    scaling = Scaling.ATK
    currSPD = 1
    currAV = 10000

    def __init__(self, ownerRole: Role, role: Role) -> None:
        super().__init__(ownerRole, role)

    def takeTurn(self) -> tuple[
        list[Buff], list[Debuff], list[Advance], list[Delay], list[Turn], list[Healing], list[Shield]]:
        self.currAV = 10000
        bl, dbl, al, dl, tl, hl, sl= super().takeTurn()
        tl.append(Turn(self.name, self.ownerRole, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                       self.scaling, 0, self.name))
        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result) -> tuple[
        list[Buff], list[Debuff], list[Advance], list[Delay], list[Turn], list[Healing], list[Shield]]:
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)
        if turn.moveName == "FireflyUlt":
            self.currAV = 10000 / 70
        return bl, dbl, al, dl, tl, hl, sl

class InfiniteFury(Summon):
    name = "InfiniteFury"
    element = Element.FIRE
    scaling = Scaling.HP
    currSPD = 1
    baseSPD = 1
    currAV = 10000

    def __init__(self, ownerRole: Role, role: Role) -> None:
        super().__init__(ownerRole, role)

    def takeTurn(self) -> tuple[
        list[Buff], list[Debuff], list[Advance], list[Delay], list[Turn], list[Healing], list[Shield]]:
        self.currAV = 10000
        bl, dbl, al, dl, tl, hl, sl = super().takeTurn()
        tl.append(Turn(self.name, self.ownerRole, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                       self.scaling, 0, self.name))
        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn: Turn, result: Result) -> tuple[
        list[Buff], list[Debuff], list[Advance], list[Delay], list[Turn], list[Healing], list[Shield]]:
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)
        if turn.moveName == "MortenaxBladeUlt":
            self.currAV = 10000 / 70
        if turn.moveName == "MortenaxBladeUltDelay":
            self.currAV += 0.15*(10000 / 70)
        return bl, dbl, al, dl, tl, hl, sl


class LightningLord(Summon):
    name = "LightningLord"
    element = Element.LIGHTNING
    scaling = Scaling.ATK
    currSPD = 90  # max of 130 at 10 stacks
    currAV = 10000 / currSPD
    stacks = 6

    def __init__(self, ownerRole: Role, role: Role) -> None:
        super().__init__(ownerRole, role)

    def takeTurn(self):
        bl, dbl, al, dl, tl, hl, sl = super().takeTurn()
        paddedStacks = "0" + str(self.stacks) if self.stacks < 10 else str(self.stacks)
        tl.append(Turn(self.name, self.ownerRole, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                       self.scaling, 0, f"LightningLordGoGo{paddedStacks}"))
        self.adjSpeed(60)
        self.stacks = 3
        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn, result):
        addStacks = 2 if turn.moveName == "JingYuanSkill" else (3 if turn.moveName == "JingYuanUlt" else 0)
        self.stacks = min(10, self.stacks + addStacks)
        self.adjSpeed(self.stacks * 10 + 30)
        return super().allyTurn(turn, result)

    def adjSpeed(self, spd):
        if spd == 60:
            self.currSPD = 60
            self.currAV = 10000 / self.currSPD
        else:
            self.currAV = self.currAV * (self.currSPD / spd)
            self.currSPD = spd


class Aha(Summon):
    name = "Aha"
    element = Element.QUANTUM
    scaling = Scaling.ATK
    currSPD = 80
    baseSPD = 80
    currAV = 10000 / currSPD
    i = 0
    last_turnName = "0"
    last_role = Role.DPS
    IsAhaTurn = False
    IsEMCTurn = False

    def __init__(self, ownerRole: Role, role: Role, elationTeam: list = None) -> None:
        super().__init__(ownerRole, role)
        self.elationTeam = elationTeam if elationTeam else [(ownerRole, "AhaSparxieGoGo")]

        # Check if Evanescia is in the team
        self.hasEvanescia = any("AhaEvanesciaGoGo" in turnName for _, turnName in self.elationTeam)
        self.hasYaoGuang = any("AhaYaoGuangGoGo" in turnName for _, turnName in self.elationTeam)
        self.hasElationMC = any("AhaElationMCGoGo" in turnName for _, turnName in self.elationTeam)

    def takeTurn(self):
        bl, dbl, al, dl, tl, hl, sl = super().takeTurn()
        self.IsAhaTurn = True
        Character.ahaFixedPunchline = False
        Character.savedPunchline = Character.SharedPunchline
        for role, turnName in self.elationTeam:
            ElationAmount = 0
            tl.append(
                Turn(self.name, role, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0, self.scaling,
                     0, turnName))

            # MODIFIED: Only reduce Banger if Evanescia is in team AND current character is NOT Evanescia
            if self.hasEvanescia and turnName != "AhaEvanesciaGoGo":
                BangerReduction = 0.5
            else:
                BangerReduction = 1.0

            if self.hasElationMC and turnName == "AhaElationMCGoGo":
                BonusPunchline = 3
            else:
                BonusPunchline = 0

            # Determine BangerDuration based on character
            if self.hasYaoGuang and turnName == "AhaYaoGuangGoGo": # or "AhaEvanesciaGoGo": #If Evanescia = E6 then 4.
                BangerDuraction = 3
            else:
                BangerDuraction = 2

            bl.append(
                Buff(f"BangerELASkill{turnName}{self.i}", StatTypes.BANGER, (Character.savedPunchline+BonusPunchline) * BangerReduction,
                     role, [AtkType.ALL], BangerDuraction, 1, role, TickDown.END))
            ElationAmount += 1
        self.i += 1
        if self.elationTeam:
            last_role, self.last_turnName = self.elationTeam[-1]
        tl.append(Turn(self.name, self.ownerRole, -1, Targeting.NA, [AtkType.ALL], [self.element],
                       [0, 0], [0, 0], 0, self.scaling, 0, "AhaEndGoGo"))
        Character.SharedPunchline = Character.savedPunchline
        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn, result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)
        if result.turnName == "YaoGuangUlt":
            self.IsAhaTurn = True
            ElationAmount = 0
            Character.ahaFixedPunchline = True
            for role, turnName in self.elationTeam:
                # MODIFIED: Only reduce Banger if Evanescia is in team AND current character is NOT Evanescia
                if self.hasEvanescia and turnName != "AhaEvanesciaGoGo":
                    BangerReduction = 0.5
                else:
                    BangerReduction = 1.0

                if self.hasElationMC and turnName == "AhaElationMCGoGo":
                    BonusPunchline = 3
                else:
                    BonusPunchline = 0

                # Determine BangerDuration based on character
                if self.hasYaoGuang and turnName == "AhaYaoGuangGoGo":  # or "AhaEvanesciaGoGo": #If Evanescia = E6 then 4.
                    BangerDuraction = 3
                else:
                    BangerDuraction = 2
                tl.append(Turn(self.name, role, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                               self.scaling,
                               0, turnName))
                bl.append(Buff(f"BangerELASkill{turnName}{self.i}", StatTypes.BANGER,
                               (Character.SharedPunchline+BonusPunchline) * BangerReduction, role, [AtkType.ALL], BangerDuraction, 1,
                               role, TickDown.END))
                ElationAmount += 1
            self.i += 1
            if self.elationTeam:
                last_role, self.last_turnName = self.elationTeam[-1]
            tl.append(Turn(self.name, self.ownerRole, -1, Targeting.NA, [AtkType.ALL], [self.element],
                           [0, 0], [0, 0], 0, self.scaling, 0, "AhaYaoEndGoGo"))

        if result.turnName == "ElationMCUlt":
            Character.savedPunchline = Character.SharedPunchline
            Character.SharedPunchline = 20
            self.IsEMCTurn = True

        if (
                result.turnName == "SilverWolf999ELASkill") and Character.ahaFixedPunchline == True and self.IsAhaTurn == True and self.IsEMCTurn == False and result.charRole == Role.DPS:
            tl.append(
                Turn(self.name, Role.SUS, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                     self.scaling, 0, "AhaElationFixedSequenceComplete"))
            Character.SharedPunchline = Character.savedPunchline + len(self.elationTeam)
            Character.ahaYaoGuangUlt = False
            Character.ahaFixedPunchline = False
            Character.ahaElaDMGBoost = 1.0
            self.IsAhaTurn = False
        elif (
                result.turnName == "SilverWolf999ELASkill") and Character.ahaFixedPunchline == False and self.IsAhaTurn == True and self.IsEMCTurn == False and result.charRole == Role.DPS:
            tl.append(
                Turn(self.name, Role.SUS, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                     self.scaling, 0, "AhaElationSequenceComplete"))
            Character.SharedPunchline = len(self.elationTeam)
            Character.ahaFixedPunchline = False
            Character.ahaElaDMGBoost = 1.0
            self.IsAhaTurn = True
        elif (
                result.turnName == "SilverWolf999NormalELASkill") and Character.ahaFixedPunchline == True and self.IsAhaTurn == True and self.IsEMCTurn == False and result.charRole == Role.DPS:
            tl.append(
                Turn(self.name, Role.SUS, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                     self.scaling, 0, "AhaElationFixedSequenceComplete"))
            Character.SharedPunchline = Character.savedPunchline + len(self.elationTeam)
            Character.ahaYaoGuangUlt = False
            Character.ahaFixedPunchline = False
            Character.ahaElaDMGBoost = 1.0
            self.IsAhaTurn = False
        elif (
                result.turnName == "SilverWolf999NormalELASkill") and Character.ahaFixedPunchline == False and self.IsAhaTurn == True and self.IsEMCTurn == False and result.charRole == Role.DPS:
            tl.append(
                Turn(self.name, Role.SUS, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                     self.scaling, 0, "AhaElationSequenceComplete"))
            Character.SharedPunchline = len(self.elationTeam)
            Character.ahaFixedPunchline = False
            Character.ahaElaDMGBoost = 1.0
            self.IsAhaTurn = True
        elif (
                result.turnName == "EvanesciaELASkill") and Character.ahaFixedPunchline == True and self.IsAhaTurn == True and self.IsEMCTurn == False and result.charRole == Role.DPS:
            tl.append(
                Turn(self.name, Role.SUS, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                     self.scaling, 0, "AhaElationFixedSequenceComplete"))
            Character.SharedPunchline = Character.savedPunchline + len(self.elationTeam)
            Character.ahaYaoGuangUlt = False
            Character.ahaFixedPunchline = False
            Character.ahaElaDMGBoost = 1.0
            self.IsAhaTurn = False
        elif (
                result.turnName == "EvanesciaELASkill") and Character.ahaFixedPunchline == False and self.IsAhaTurn == True and self.IsEMCTurn == False and result.charRole == Role.DPS:
            tl.append(
                Turn(self.name, Role.SUS, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                     self.scaling, 0, "AhaElationSequenceComplete"))
            Character.SharedPunchline = len(self.elationTeam)
            Character.ahaFixedPunchline = False
            Character.ahaElaDMGBoost = 1.0
            self.IsAhaTurn = True

        elif (
                result.turnName == "SilverWolf999ELASkill") and Character.ahaFixedPunchline == True and self.IsEMCTurn == True and result.charRole == Role.DPS:
            tl.append(
                Turn(self.name, Role.SUS, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                     self.scaling, 0, "AhaElationFixedEMCSequenceComplete"))
            Character.SharedPunchline = Character.savedPunchline
            Character.ahaFixedPunchline = False
            Character.ahaElaDMGBoost = 1.0
            self.IsEMCTurn = False

        elif (
                result.turnName == "SilverWolf999NormalELASkill") and Character.ahaFixedPunchline == True and self.IsEMCTurn == True and result.charRole == Role.DPS:
            tl.append(
                Turn(self.name, Role.SUS, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                     self.scaling, 0, "AhaElationFixedEMCSequenceComplete"))
            Character.SharedPunchline = Character.savedPunchline
            Character.ahaFixedPunchline = False
            Character.ahaElaDMGBoost = 1.0
            self.IsEMCTurn = False
        elif (
                result.turnName == "EvanesciaELASkill") and Character.ahaFixedPunchline == True and self.IsEMCTurn == True and result.charRole == Role.DPS:
            tl.append(
                Turn(self.name, Role.SUS, -1, Targeting.NA, [AtkType.ALL], [self.element], [0, 0], [0, 0], 0,
                     self.scaling, 0, "AhaElationFixedEMCSequenceComplete"))
            Character.SharedPunchline = Character.savedPunchline
            Character.ahaFixedPunchline = False
            Character.ahaElaDMGBoost = 1.0
            self.IsEMCTurn = False

        return bl, dbl, al, dl, tl, hl, sl

class Souldragon(Summon):
    name = "Souldragon"
    element = Element.PHYSICAL
    scaling = Scaling.ATK
    currSPD = 165
    baseSPD = 165
    currAV = 10000 / currSPD
    breakMidTurn = False  # Souldragon waits until the full turn ends before acting

    def __init__(self, ownerRole: Role, role: Role, owner=None) -> None:
        super().__init__(ownerRole, role)
        self.owner = owner      # reference to DanHengPermansorTerrae instance for stat/bondmate access
        self.ultEnhanced = 0    # remaining enhanced actions from Dan Heng's Ult (max 2)
        self.E2Multiplier = 1.0

    def takeTurn(self):
        bl, dbl, al, dl, tl, hl, sl = super().takeTurn()

        # ── Talent shield: 10% ATK + 200, AOE, non-defining (shares cap with Skill) ──
        # isDefining=False so this doesn't reset the cap; it just tops up
        # currentAmount within whatever cap Dan Heng's Skill last established.
        tl.append(Turn(self.name, self.ownerRole, -1, Targeting.NA, [AtkType.ALL], [self.element],
                       [0, 0], [0, 0], 0, self.scaling, 0, "SoulDragonShield"))
        logger.debug(f"Souldragon.takeTurn: ultEnhanced={self.ultEnhanced}")

        # ── Ult enhancement: extra FUA + bondmate additional DMG ─────────────
        if self.ultEnhanced > 0:
            self.ultEnhanced -= 1

            # Extra physical FUA (80% Dan Heng ATK, AOE) — charRole = owner so
            # getBaseValue resolves Dan Heng's ATK buffs correctly via playerTeam
            tl.append(Turn(self.name, self.ownerRole, -1, Targeting.NA, [AtkType.ALL], [self.element],
                           [0, 0], [0, 0], 0, self.scaling, 0, "SoulDragonAttack"))

            # Bondmate additional DMG: 80% of Bondmate's ATK, Bondmate's element, AOE
            # Emitted with bondmateRole as charRole so getBaseValue resolves
            # the bondmate's ATK% buffs correctly via their role.
            if self.owner is not None and self.owner.bondmateRole is not None:
                bondmateRole = self.owner.bondmateRole
                # Resolve bondmate's element from the player team
                bondmateElement = Element.PHYSICAL  # fallback
                bondmateName = "DanHengPermansorTerrae"
                if Character._current_player_team:
                    for char in Character._current_player_team:
                        if char.role == bondmateRole:
                            bondmateElement = char.element
                            bondmateName = char.name
                            break
                e3Mul = 0.88 if self.owner.eidolon >= 3 else 0.80
                tl.append(Turn(
                    bondmateName, bondmateRole, -1, Targeting.AOE,
                    [AtkType.ADD], [bondmateElement],
                    [e3Mul*self.E2Multiplier, 0], [0, 0], 0, Scaling.ATK, 0, "SouldragonBondmateADD"))
                tl.append(Turn(
                    bondmateName, bondmateRole, -1, Targeting.SINGLE,
                    [AtkType.ADD], [bondmateElement],
                    [0.40*self.E2Multiplier, 0], [0, 0], 0, Scaling.ATK, 0, "SouldragonBondmateADD"))

        return bl, dbl, al, dl, tl, hl, sl

    def allyTurn(self, turn, result):
        bl, dbl, al, dl, tl, hl, sl = super().allyTurn(turn, result)

        if turn.moveName == "DanHengPermansorTerraeE6UltDamage":
            if self.owner is not None and self.owner.bondmateRole is not None:
                bondmateRole = self.owner.bondmateRole
                bondmateElement = Element.PHYSICAL
                bondmateName = "DanHengPermansorTerrae"
                if Character._current_player_team:
                    for char in Character._current_player_team:
                        if char.role == bondmateRole:
                            bondmateElement = char.element
                            bondmateName = char.name
                            break
                tl.append(Turn(
                    bondmateName, bondmateRole, -1, Targeting.AOE,
                    [AtkType.ADD], [bondmateElement],
                    [3.30, 0], [0, 0], 0, Scaling.ATK, 0, "SouldragonBondmateADD"))

        return bl, dbl, al, dl, tl, hl, sl