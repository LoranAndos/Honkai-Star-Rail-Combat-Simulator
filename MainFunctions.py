import logging
from argparse import Action
from unittest.mock import DEFAULT
from wsgiref.handlers import CGIHandler

import Character
import Turn_Text
from Character import *
from Enemy import Enemy
from Attributes import *
from Healing import *
from Lightcone import Lightcone
from Memosprite import Memosprite
from Summons import *
from Memosprites import Mem
from Trackers import *
from random import randrange

logger = logging.getLogger(__name__)

def manualPrint(prnt, msg: any):
    print(msg) if prnt else 0

def getBuffNames(lst: list) -> list:
    return [entry.name for entry in lst]

def parseBuffs(lst: list[Buff], playerTeam: list[Character]) -> list:
    buffList = []
    for buff in lst:
        if buff.target == Role.ALL: #teamwide buff, need to add 4 instances
            for char in playerTeam:
                target = char.role if (buff.tickDown == Role.SELF) else buff.tickDown
                buffList.append(Buff(buff.name, buff.buffType, buff.val, char.role, buff.atkType, buff.turns, buff.stackLimit, target, buff.tdType, buff.reqBroken))
        elif buff.target == Role.TEAM:
            if buff.name == "HMCE4BuffBE":
                excludeRole = findCharName(playerTeam, "HarmonyMC").role
            else:
                excludeRole = None
            for char in playerTeam:
                if char.role == excludeRole:
                    continue
                target = char.role if (buff.tickDown == Role.SELF) else buff.tickDown
                buffList.append(Buff(buff.name, buff.buffType, buff.val, char.role, buff.atkType, buff.turns, buff.stackLimit, target, buff.tdType, buff.reqBroken))
        else: #single target buff, only add one instance
            target = buff.target if (buff.tickDown == Role.SELF) else buff.tickDown
            buffList.append(Buff(buff.name, buff.buffType, buff.val, buff.target, buff.atkType, buff.turns, buff.stackLimit, target, buff.tdType, buff.reqBroken))
    return buffList

def parseDebuffs(lst: list[Debuff], enemyTeam: list[Enemy]) -> list[Debuff]:
    debuffList = []
    for d in lst:
        if d.target == Role.ALL: # AoE debuff, need to add 1 instance per enemy
            for i in range(len(enemyTeam)):
                newDebuff = Debuff(d.name, d.charRole, d.debuffType, d.val, i, d.atkType, d.turns, d.stackLimit, d.isDot, d.dotSplit, d.isBlast)
                newDebuff.dotMul = d.dotSplit[0]
                debuffList.append(newDebuff)
        else:
            enemy = enemyTeam[d.target]
            newDebuff = Debuff(d.name, d.charRole, d.debuffType, d.val, d.target, d.atkType, d.turns, d.stackLimit, d.isDot, d.dotSplit, d.isBlast)
            newDebuff.dotMul = d.dotSplit[0] # main target dot
            debuffList.append(newDebuff)
            if enemy.hasAdj() and d.isBlast:
                for adjID in enemy.adjacent:
                    newDebuff = Debuff(d.name, d.charRole, d.debuffType, d.val, adjID, d.atkType, d.turns, d.stackLimit, d.isDot, d.dotSplit, d.isBlast)
                    newDebuff.dotMul = d.dotSplit[1] # adjacent target dot
                    debuffList.append(newDebuff)
    return debuffList

def parseAdvance(lst: list[Advance], playerTeam: list[Character]) -> list[Advance]:
    advList = []
    for adv in lst:
        if adv.targetRole == Role.ALL: # Team wide advance
            for char in playerTeam:
                advList.append(Advance(adv.name, char.role, adv.advPercent))
        else: # Single advance
            advList.append(adv)
    return advList

def parseDelay(lst: list[Delay], enemyTeam: list[Enemy]) -> list[Delay]:
    delayList = []
    for delay in lst:
        if delay.target == Role.ALL:
            for enemy in enemyTeam:
                delayList.append(Delay(delay.name, delay.delayPercent, enemy.enemyID, delay.reqBroken, delay.stackable))
        else:
            delayList.append(delay)
    return delayList

def parseTurns(lst: list[Turn], playerTeam: list[Character]) -> list[Turn]:
    turnList = []
    for turn in lst:
        if turn.charRole == Role.ALL:
            for char in playerTeam:
                turnList.append(Turn(turn.charName, char.role, turn.targetID, turn.targeting, turn.atkType, turn.element, turn.dmgSplit, turn.brkSplit, turn.errGain, turn.scaling, turn.spChange, turn.moveName))
        elif turn.charRole == Role.TEAM:
            for char in playerTeam:
                if char.name == turn.charName:
                    continue
                turnList.append(Turn(turn.charName, char.role, turn.targetID, turn.targeting, turn.atkType, turn.element, turn.dmgSplit, turn.brkSplit, turn.errGain, turn.scaling, turn.spChange, turn.moveName))
        else:
            turnList.append(turn)
    return turnList

def addDelay(currList: list[Delay], newList: list[Delay]) -> list[Delay]:
    def checkValidAdd(delayToCheck: Delay, currDelayList: list[Delay]) -> bool:
        return all(delayToCheck.name != existingDelay.name or delayToCheck.stackable or delayToCheck.target != existingDelay.target for existingDelay in currDelayList)

    for delay in newList:
        if checkValidAdd(delay, currList):
            currList.append(delay)

    return currList

def addAdvance(currList: list[Advance], newList: list[Advance]) -> list[Advance]:
    currList.extend(newList)
    return currList

def addBuffs(currList: list, newList: list) -> list:
    def checkValidAdd(buffToCheck: Buff, currentList: list) -> tuple[bool, int]:
        for i in range(len(currentList)):
            checkAgainst = currentList[i]
            if buffToCheck.name == checkAgainst.name:
                if buffToCheck.target == checkAgainst.target:
                    checkAgainst.val = buffToCheck.val
                    return False, i
        return True, -1

    # Only add a new entry if unique name or repeated name but different target
    for buff in newList:
        check, buffID = checkValidAdd(buff, currList)
        if check:
            currList.append(buff)
        else:
            if not currList[buffID].atMaxStacks():
                currList[buffID].incStack()
            currList[buffID].refreshTurns()
    return currList

def findBuffs(charRole: Role, buffType: StatTypes, buffList: list[Buff]) -> list:
    return [x for x in buffList if (x.buffType == buffType and x.target == charRole)]

def sumBuffs(buffList: list[Buff]):
    return sum([x.getBuffVal() for x in buffList])

def getCharSPD(char: Character, buffList: list[Buff]) -> float:
    baseSPD = char.baseSPD
    spdPercent = sumBuffs(findBuffs(char.role, StatTypes.SPD_PERCENT, buffList))
    spdFlat = sumBuffs(findBuffs(char.role, StatTypes.Spd, buffList)) + char.getSPD()
    return baseSPD * (1 + spdPercent) + spdFlat

def getCharMaxHP(char: Character, lightcone: Lightcone ,buffList: list[Buff]) -> float:
    baseHP= char.baseHP
    baseLcHP = lightcone.baseHP
    HPPercent = sumBuffs(findBuffs(char.role, StatTypes.HP_PERCENT, buffList)) + char.getHPPercent()
    HPFlat = sumBuffs(findBuffs(char.role,StatTypes.HP, buffList)) + char.getHPFlat()
    if char.name == "Mem":
        HPFlat = 0.86*HPFlat + 688 # 688 if eidolon higher than 3 else 640
        baseLcHP = baseLcHP*0.86
    return ((baseHP + baseLcHP)*(1 + HPPercent) + HPFlat)

def initCharCurrentHP_MaxHp(playerTeam: list[Character], buffList: list[Buff]):
    for char in playerTeam:
        char.maxHP = getCharMaxHP(char, char.lightcone, buffList)
        char.currHP = getCharMaxHP(char, char.lightcone, buffList)

def parseHealing(lst: list[Healing], playerTeam: list[Character]) -> list:
    HealingList = []
    HpList = []
    for character in playerTeam:
        HpList.append(character.currHP)
    LowestHp = min(HpList)
    NumberLowestHp = HpList.index(LowestHp)
    for Heal in lst:
        if Heal.target == Role.ALL:
            if Heal.targeting == Targeting.AOE: #teamwide Heal
                for char in playerTeam:
                    HealingList.append(Healing(Heal.name,Heal.val,Heal.scaling,Heal.target,Heal.targeting))
            elif Heal.targeting == Targeting.BLAST:
                for i in range(len(playerTeam)):
                    if i == NumberLowestHp and NumberLowestHp > 0:
                        HealingList[i-1] = (Healing(Heal.name, [Heal.val[1]], Heal.scaling, Heal.target, Heal.targeting))
                        HealingList[i] = (Healing(Heal.name, [Heal.val[0]], Heal.scaling, Heal.target, Heal.targeting))
                        HealingList[i+1] = (Healing(Heal.name, [Heal.val[1]], Heal.scaling, Heal.target, Heal.targeting))
                    elif i == NumberLowestHp and NumberLowestHp == 0:
                        HealingList[i] = (Healing(Heal.name, [Heal.val[0]], Heal.scaling, Heal.target, Heal.targeting))
                        HealingList[i+1] = (Healing(Heal.name, [Heal.val[1]], Heal.scaling, Heal.target, Heal.targeting))
                    elif i == NumberLowestHp and NumberLowestHp == len(playerTeam):
                        HealingList[i-1] = (Healing(Heal.name, [Heal.val[1]], Heal.scaling, Heal.target, Heal.targeting))
                        HealingList[i] = (Healing(Heal.name, [Heal.val[0]], Heal.scaling, Heal.target, Heal.targeting))
                    else:
                        HealingList[i] = (Healing(Heal.name,[0], Heal.scaling, Heal.target, Heal.targeting))
            else:
                for i in range(len(playerTeam)):
                    if i == NumberLowestHp:
                        HealingList[i] = (Healing(Heal.name, [Heal.val[0]], Heal.scaling, Heal.target, Heal.targeting))
                    else:
                        HealingList[i] = (Healing(Heal.name, [0], Heal.scaling, Heal.target, Heal.targeting))
        elif Heal.target != Role.ALL:
            for character in playerTeam:
                if character.role == Heal.target:
                    HealingList.append(Healing(Heal.name, [Heal.val[0]], Heal.scaling, Heal.target, Heal.targeting))
                else:
                    HealingList.append((Healing(Heal.name, [0], Heal.scaling, Heal.target, Heal.targeting)))

    return HealingList

def addHealing(currList: list[Healing], newList: list[Healing]) -> list[Healing]:
    for Heal in newList:
        currList.append(Heal)
    return currList

def getEnemySPD(enemy: Enemy, debuffList: list[Debuff]) -> float:
    baseSPD = enemy.spd
    debuffSum = 0
    for debuff in debuffList:
        if (debuff.debuffType == StatTypes.SPD_PERCENT) and (debuff.target == enemy.enemyID):
            debuffSum += debuff.getDebuffVal()
    return baseSPD * (1 - debuffSum)

def initCharAV(char: Character, buffList: list[Buff]):
    charSPD = getCharSPD(char, buffList)
    char.reduceAV(char.currAV - (10000 / charSPD))
    char.currSPD = charSPD

def resetUnitAV(unit, buffList: list[Buff], debuffList: list[Debuff]):
    # check if unit is a char or enemy
    if unit.isChar() and not unit.isSummon(): # Character, check buffList for spd buffs
        initCharAV(unit, buffList)
    elif unit.isChar() and unit.isSummon():
        unit.currAV = 10000 / unit.currSPD
    else: # Enemy, check debuffList for spd debuffs
        eSPD = getEnemySPD(unit, debuffList)
        unit.currAV = 10000 / eSPD
        unit.currSPD = eSPD

def spdAdjustment(teamList: list[Character], buffList: list[Buff]):
    for char in teamList:
        newSPD = getCharSPD(char, buffList)
        if newSPD != char.currSPD:
            char.reduceAV(char.currAV - (char.currAV * char.currSPD / newSPD))
            char.currSPD = newSPD
            logger.info(f"SPD    > {char.name} speed changed to {newSPD:.3f} | NewAV: {char.currAV:.3f}")
    return

def enemySPDAdjustment(enemyTeam: list[Enemy], debuffList: list[Debuff]):
    for enemy in enemyTeam:
        newSPD = getEnemySPD(enemy, debuffList)
        if newSPD != enemy.currSPD:
            enemy.currAV = enemy.currAV * enemy.currSPD / newSPD
        enemy.currSPD = newSPD
    return

def avAdjustment(teamList: list[Character], advList: list[Advance]):
    for adv in advList:
        char = findCharRole(teamList, adv.targetRole)
        avRed = (10000 / char.currSPD)  * adv.advPercent
        char.reduceAV(avRed)
        char.priority = char.priority + 15
        logger.info(f"ADV    > {char.name} advanced by {adv.advPercent * 100:.3f}% from {adv.name} | NewAV: {char.currAV:.3f} | Priority: {char.priority}")
    return

def sortUnits(allUnits: list) -> list:
    return sorted(allUnits, key=lambda x: (x.currAV, -x.priority))

def setPriority(allUnits: list):
    for i in range(len(allUnits)):
        allUnits[i].priority = len(allUnits) - i

def delayAdjustment(enemyTeam: list[Enemy], delayList: list[Delay], debuffList: list[Debuff]) -> list[Delay]:
    def findEnemy(enemyID: int) -> Enemy:
        return next((currEnemy for currEnemy in enemyTeam if currEnemy.enemyID == enemyID), None)

    res = []
    for delay in delayList:
        enemy = findEnemy(delay.target)
        enemyAV = 10000 / getEnemySPD(enemy, debuffList)
        if not delay.reqBroken or (delay.reqBroken and enemy.broken):
            avRed = enemyAV * delay.delayPercent * -1
            enemy.reduceAV(avRed)
            logger.info(f"DELAY  > {enemy.name} delayed by {delay.delayPercent * 100:.1f}% from {delay.name} | NewAV: {enemy.currAV:.3f}")
        else:
            res.append(delay) # keep the delay in delayList until it can be applied
    return res


# noinspection PyUnresolvedReferences
def addEnergy(playerTeam: list[Character], enemyTeam: list[Enemy], numAttacks: int, attackTypeRatio: list[float], buffList: list[Buff]):
    aggroLst = []
    for char in playerTeam:
        aggro = char.aggro
        aggroLst.append(aggro)
    actAttacks = 1 if numAttacks == 0 else numAttacks
    aggroSum = sum(aggroLst)
    AggroNumber = randrange(1,aggroSum+1, 1)
    finalEnergy = [0]*len(playerTeam)
    for enemy in enemyTeam:
        Number_Keeper = 0
        if enemy.enemyType == EnemyType.ADD:
            for a in range(len(playerTeam)-1):
                if AggroNumber > Number_Keeper and AggroNumber < Number_Keeper + aggroLst[a] - 1:
                    finalEnergy[a] = (finalEnergy[a] + 10)*actAttacks/len(enemyTeam) # Single Target hit = 10 energy
                    Number_Keeper = Number_Keeper + aggroLst[a]
                else:
                    finalEnergy[a] = 0
                Number_Keeper = Number_Keeper + aggroLst[a]
        elif enemy.enemyType == EnemyType.ELITE:
            AttackTypeChooser = randrange(1,3,1)
            if AttackTypeChooser == 1:
                for a in range(len(playerTeam)-1):
                    if AggroNumber > Number_Keeper and AggroNumber < Number_Keeper + aggroLst[a] - 1:
                        finalEnergy[a] = (finalEnergy[a] + 10)*actAttacks/len(enemyTeam) # Single Target hit = 10 energy
                        Number_Keeper = Number_Keeper + aggroLst[a]
                    else:
                        finalEnergy[a] = finalEnergy[a] + 0
                        Number_Keeper = Number_Keeper + aggroLst[a]
            if AttackTypeChooser == 2:
                for a in range(len(playerTeam)-1):
                    if AggroNumber > Number_Keeper and AggroNumber < Number_Keeper + aggroLst[a] -1 and a == 1:
                        finalEnergy[a] = (finalEnergy[a] + 10)*actAttacks/len(enemyTeam) # Blast hit = 10 energy
                        finalEnergy[a+1] = (finalEnergy[a] + 10)*actAttacks/len(enemyTeam) # Blast hit = 10 energy
                        Number_Keeper = Number_Keeper + aggroLst[a]
                    elif AggroNumber > Number_Keeper and AggroNumber < Number_Keeper + aggroLst[a] -1 and (a != 1 and a != len(playerTeam)):
                        finalEnergy[a] = (finalEnergy[a] + 10)*actAttacks/len(enemyTeam) # Blast hit = 10 energy
                        finalEnergy[a-1] = (finalEnergy[a] + 10)*actAttacks/len(enemyTeam) # Blast hit = 10 energy
                        finalEnergy[a+1] = (finalEnergy[a] + 10)*actAttacks/len(enemyTeam) # Blast hit = 10 energy
                        Number_Keeper = Number_Keeper + aggroLst[a]
                    elif AggroNumber > Number_Keeper and AggroNumber < Number_Keeper + aggroLst[a] -1 and a == len(playerTeam):
                        finalEnergy[a] = (finalEnergy[a] + 10)*actAttacks/len(enemyTeam) # Blast hit = 10 energy
                        finalEnergy[a-1] = (finalEnergy[a] + 10)*actAttacks/len(enemyTeam) # Blast hit = 10 energy
                        Number_Keeper = Number_Keeper + aggroLst[a]
                    else:
                        finalEnergy[a] = finalEnergy[a] + 0
                        Number_Keeper = Number_Keeper + aggroLst[a]
        elif enemy.enemyType == EnemyType.BOSS:
            AttackTypeChooser = randrange(1,3,1)
            if AttackTypeChooser == 1:
                for a in range(len(playerTeam)-1):
                    if AggroNumber > Number_Keeper and AggroNumber < Number_Keeper + aggroLst[a] -1 and a == 1:
                        finalEnergy[a] = (finalEnergy[a] + 10)*actAttacks/len(enemyTeam) # Blast hit = 10 energy
                        finalEnergy[a+1] = (finalEnergy[a] + 10)*actAttacks/len(enemyTeam) # Blast hit = 10 energy
                        Number_Keeper = Number_Keeper + aggroLst[a]
                    elif AggroNumber > Number_Keeper and AggroNumber < Number_Keeper + aggroLst[a] -1 and (a != 1 and a != len(playerTeam)):
                        finalEnergy[a] = (finalEnergy[a] + 10)*actAttacks/len(enemyTeam) # Blast hit = 10 energy
                        finalEnergy[a-1] = (finalEnergy[a] + 10)*actAttacks/len(enemyTeam) # Blast hit = 10 energy
                        finalEnergy[a+1] = (finalEnergy[a] + 10)*actAttacks/len(enemyTeam) # Blast hit = 10 energy
                        Number_Keeper = Number_Keeper + aggroLst[a]
                    elif AggroNumber > Number_Keeper and AggroNumber < Number_Keeper + aggroLst[a] -1 and a == len(playerTeam):
                        finalEnergy[a] = (finalEnergy[a] + 10)*actAttacks/len(enemyTeam) # Blast hit = 10 energy
                        finalEnergy[a-1] = (finalEnergy[a] + 10)*actAttacks/len(enemyTeam) # Blast hit = 10 energy
                        Number_Keeper = Number_Keeper + aggroLst[a]
                    else:
                        finalEnergy[a] = finalEnergy[a]
                        Number_Keeper = Number_Keeper + aggroLst[a]
            if AttackTypeChooser == 2:
                for a in range(len(playerTeam)):
                    finalEnergy[a] = (finalEnergy[a] + 5)*actAttacks
    for i in range(len(playerTeam)):
        char = playerTeam[i]
        placeHolderTurn = Turn(char.name, char.role, -1, Targeting.NA, [AtkType.SPECIAL], [char.element], [0, 0], [0, 0], 0, char.scaling, 0, "HitEnergyPlaceholder")
        errMul = getMulERR(char, enemyTeam[0], buffList, [], placeHolderTurn) if not char.specialEnergy else 0
        if numAttacks != 0:
            char.addEnergy(finalEnergy[i] * errMul)
    return [i / (actAttacks) for i in finalEnergy]


def checkInTeam(name: str, team: list[Character]) -> bool:
    for char in team:
        if char.name == name:
            return True
    return False

def hasWeakness(weakness: Element, enemyTeam: list[Enemy]) -> bool:
    return weakness in enemyTeam[0].weakness

def tickDebuffs(enemy: Enemy, debuffList: list[Debuff]) -> list[Debuff]:
    newList = []
    for debuff in debuffList:
        if debuff.target == enemy.enemyID:
            if debuff.turns > 1:
                debuff.reduceTurns()
                newList.append(debuff)
            else:
                logging.info(f"        Debuff {debuff.name} expired")
        else:
            newList.append(debuff)
    return newList


# noinspection PyUnresolvedReferences
def tickBuffs(char: Character, buffList: list[Buff], tdType: str) -> list[Buff]:
    newList = []
    cmp = TickDown.START if tdType == "START" else TickDown.END
    for buff in buffList:
        if char.name == "Robin" and not char.canBeAdv and cmp == TickDown.END:
            return buffList
        if buff.tdType == cmp: # must match tdType to tickdown
            if buff.tickDown == char.role: # must match char role to tickdown
                if buff.turns <= 1:
                    logging.info(f"        Buff {buff.name} expired")
                    continue
                buff.reduceTurns()
        newList.append(buff)
    return newList

def takeDebuffDMG(enemy: Enemy, playerTeam: list[Character], buffList: list[Buff], debuffList: list[Debuff]) -> float:
    dmg = 0
    dotList = [debuff for debuff in debuffList if ((debuff.target == enemy.enemyID) and (debuff.isDot or debuff.debuffType == StatTypes.FREEZE or debuff.debuffType == StatTypes.ENTANGLE))]
    for dot in dotList:
        char = findCharRole(playerTeam, dot.charRole)
        pTurn = Turn(char.name, char.role, enemy.enemyID, Targeting.DOT, ["DOT"], [char.element], [0, 0], [0, 0], 0, char.scaling, 0, "Placeholder")
        if dot.debuffType in {StatTypes.BLEED, StatTypes.BURN, StatTypes.WINDSHEAR, StatTypes.SHOCK}: # normal dot debuff damage
            dotDmg = dot.getDebuffVal() * getMulENEMY(char, enemy, buffList, debuffList, pTurn)
            dmg += dotDmg
            logger.warning(f"    DEBUFF - {enemy.name} took {dotDmg:.3f} Debuff damage from {dot.name}")
        elif dot.debuffType == StatTypes.FREEZE or dot.name == StatTypes.ENTANGLE: # not dot-type damage from breaks, can't be buffed by dot buffs
            pTurn = Turn(char.name, char.role, enemy.enemyID, Targeting.DEBUFF, [], [char.element], [0, 0], [0, 0], 0, char.scaling, 0, "Placeholder")
            dotDmg = dot.getDebuffVal() * getMulENEMY(char, enemy, buffList, debuffList, pTurn)
            dmg += dotDmg
            logger.warning(f"    DEBUFF - {enemy.name} took {dotDmg:.3f} Debuff damage from {dot.name}")
        else: # dots applied by char
            baseValue = getBaseValue(char, buffList, pTurn)
            percentMul = dot.dotMul
            dmgMul = getMulDMG(char, enemy, buffList, debuffList, pTurn)
            enemyMul = getMulENEMY(char, enemy, buffList, debuffList, pTurn)
            dotDmg = baseValue * percentMul * dmgMul * enemyMul
            dmg += dotDmg
            logger.warning(f"    DEBUFF - {enemy.name} took {dotDmg:.3f} Debuff damage from {dot.name}")
    enemy.addDebuffDMG(dmg)
    return dmg

def findCharRole(playerTeam: list[Character], charRole: Role) -> Character:
    for char in playerTeam:
        if char.role == charRole:
            return char

def findCharName(playerTeam: list, charName: str):
    for char in playerTeam:
        if char.name == charName:
            return char

def findBuffName(lst: list, name: str): # works for both buffs and debuffs
    for entry in lst:
        if entry.name == name:
            return entry

def countDebuffs(enemyID: int, debuffList: list[Debuff]) -> int:
    return len([debuff for debuff in debuffList if (debuff.target == enemyID and debuff.val != 0)])

def inTeam(playerTeam: list[Character], charName) -> bool:
    for char in playerTeam:
        if char.name == charName:
            return True
    return False

def addSummons(playerTeam: list[Character]) -> list:
    summons = []
    return summons

def handleAdditions(playerTeam: list, enemyTeam: list[Enemy], buffList: list[Buff], debuffList: list[Debuff], advList: list[Advance], delayList: list[Delay], healingList: list[Healing],
                    buffToAdd: list[Buff], DebuffToAdd: list[Debuff], advToAdd: list[Advance], delayToAdd: list[Delay], healingToAdd: list[Healing]) -> tuple[list[Buff], list[Debuff], list[Advance], list[Delay], list[Healing]]:
    buffs, debuffs, advs, delays, heals = parseBuffs(buffToAdd, playerTeam), parseDebuffs(DebuffToAdd, enemyTeam), parseAdvance(advToAdd, playerTeam), parseDelay(delayToAdd, enemyTeam), parseHealing(healingToAdd, playerTeam)
    buffList = addBuffs(buffList, buffs)
    debuffList = addBuffs(debuffList, debuffs)
    advList = addAdvance(advList, advs)
    delayList = addDelay(delayList, delays)
    healingList = addHealing(healingList, heals)

    return buffList, debuffList, advList, delayList, healingList

def handleTurn(turn: Turn, playerTeam: list[Character], enemyTeam: list[Enemy], buffList: list[Buff], debuffList: list[Debuff], healingList: list[Healing], manualMode = False) -> tuple[Result, list[Debuff], list[Delay]]:
    char = findCharRole(playerTeam, turn.charRole)
    charERR = getMulERR(char, enemyTeam[0], buffList, debuffList, turn)
    baseValue = getBaseValue(char, buffList, turn)
    anyBroken = []
    turnDmg = 0
    wbDmg = 0
    Total_HP_Change = 0
    newDebuff, newDelay = [], []

    def processEnemy(currTurn: Turn, currEnemy: Enemy, breakUnits: float, percentMultiplier: float, charCR=0.0, charCD=0.0) -> tuple[list[Debuff], list[Delay]]:
        nonlocal turnDmg, wbDmg, anyBroken

        charWBE = getMulWBE(char, currEnemy, buffList, debuffList, currTurn)
        charDMG = getMulDMG(char, currEnemy, buffList, debuffList, currTurn)
        charCR = getMulCR(char, currEnemy, buffList, debuffList, currTurn) if charCR == 0 else charCR
        charCD = getMulCD(char, currEnemy, buffList, debuffList, currTurn) if charCD == 0 else charCD
        enemyMul = getMulENEMY(char, currEnemy, buffList, debuffList, currTurn)

        enemyBroken = False
        newDebuffs, newDelays = [], []
        # if turn.moveName == "H7UltEnhancedBSC":
        #     print(f"ATK: {baseValue:.3f} | DMG%: {charDMG:.3f} | CR: {charCR:.3f} | CD: {charCD:.3f} | EnemyMul: {enemyMul:.3f}")
        turnDmg += expectedDMG(baseValue * charDMG * percentMultiplier * enemyMul, charCR, charCD)

        gauge = 0
        if checkValidList(currTurn.element, currEnemy.weakness):
            gauge = breakUnits * charWBE
            enemyBroken = currEnemy.redToughness(gauge)
        elif currTurn.omniBreak:
            gauge = breakUnits * charWBE * currTurn.omniBreakMod
            enemyBroken = currEnemy.redToughness(gauge)
        msg = f"    GAUGE  - Enemy {currEnemy.enemyID} toughness reduced by {gauge:.3f}"
        logger.info(msg)
        if manualMode and gauge > 0:
            print(msg)

        if enemyBroken:
            charBE = getMulBE(char, currEnemy, buffList, debuffList, currTurn)
            anyBroken.append(currEnemy)
            ele = currTurn.element[0]
            enemyBreakMul = getMulENEMY(char, currEnemy, buffList, debuffList, Turn(char.name, char.role, currEnemy.enemyID, Targeting.NA, [AtkType.BRK], [char.element], [0, 0], [0, 0], 0, char.scaling, 0, "PlaceholderTurn"))
            brkMul = getMulBrkDMG(char, currEnemy, buffList, debuffList, currTurn)
            wbDmg += eleDct[ele.value] * wbMultiplier * currEnemy.maxToughnessMul * charBE * enemyBreakMul * brkMul
            newDelays.extend(wbDelay(ele, charBE, currEnemy))
            newDebuff.append(wbDebuff(ele, char.role, charBE, currEnemy))
        return newDebuffs, newDelays

    def processBreak(currTurn: Turn, currEnemy: Enemy, breakUnits: float, percentMultiplier: float, breakType: str):
        nonlocal turnDmg, wbDmg, anyBroken

        charBE = getMulBE(char, currEnemy, buffList, debuffList, currTurn)
        brkMul = getMulBrkDMG(char, currEnemy, buffList, debuffList, currTurn)
        eleMul = eleDct[char.element.value]
        enemyMul = getMulENEMY(char, currEnemy, buffList, debuffList, currTurn)
        if breakType == "BREAK": # should only appear when enemies are broken
            breakDMG = eleMul * wbMultiplier * currEnemy.maxToughnessMul * charBE * brkMul * percentMultiplier * enemyMul
            turnDmg += breakDMG
        elif breakType == "SUPER": # superbreak logic
            sbrkMul = getMulSuperBrkDMG(char, currEnemy, buffList, debuffList, currTurn) # should only be affected by HMC A2 trace for now
            charWBE = getMulWBE(char, currEnemy, buffList, debuffList, currTurn)
            tempDmg = wbMultiplier * percentMultiplier * (breakUnits / 10 * charWBE) * brkMul * sbrkMul * charBE * enemyMul
            turnDmg += tempDmg
            # print(f"{turn.moveName} | WBMUL: {wbMultiplier:.3f} | SBScg: {percentMultiplier} | ToughnessRed: {breakUnits / 10 * charWBE:.3f} | BrkMul: {brkMul:.3f} | SBrkMul: {sbrkMul:.3f} | CharBE: {charBE:.3f} | EnemyMul: {enemyMul:.3f} | DMG: {tempDmg:.3f}" )
        return

    enemiesHit = []
    preHitStatus = [True if e.broken else False for e in enemyTeam]
    if "BREAK" in turn.targeting.value:
        if "SBREAK" in turn.targeting.value: # superbreak logic
            if turn.targeting == Targeting.AOESB:
                for enemy in enemyTeam:
                    if enemy.broken: # only can apply when enemy is weakness broken
                        enemiesHit.append(enemy)
                        processBreak(turn, enemy, turn.brkSplit[0], turn.dmgSplit[0], "SUPER")
            else:
                enemy = findBestEnemy(char, enemyTeam, buffList, debuffList, turn) if turn.targetID == -1 else enemyTeam[turn.targetID]
                if enemy.broken:
                    enemiesHit.append(enemy)
                    processBreak(turn, enemy, turn.brkSplit[0], turn.dmgSplit[0], "SUPER")
                if enemy.hasAdj and (turn.brkSplit[1] > 0 or turn.dmgSplit[1] > 0):
                    for enemyID in enemy.adjacent:
                        adj_enemy = enemyTeam[enemyID]
                        if adj_enemy.broken:
                            enemiesHit.append(adj_enemy)
                            processBreak(turn, adj_enemy, turn.brkSplit[1], turn.dmgSplit[1], "SUPER")
        else:
            if turn.targeting == Targeting.AOEBREAK: # normal break
                for enemy in enemyTeam:
                    enemiesHit.append(enemy)
                    processBreak(turn, enemy, turn.brkSplit[0], turn.dmgSplit[0], "BREAK")
            else:
                enemy = findBestEnemy(char, enemyTeam, buffList, debuffList, turn) if turn.targetID == -1 else enemyTeam[turn.targetID]
                enemiesHit.append(enemy)
                processBreak(turn, enemy, turn.brkSplit[0], turn.dmgSplit[0], "BREAK")
                if enemy.hasAdj and (turn.brkSplit[1] > 0 or (turn.dmgSplit[1] > 0)):
                    for enemyID in enemy.adjacent:
                        adj_enemy = enemyTeam[enemyID]
                        enemiesHit.append(adj_enemy)
                        processBreak(turn, adj_enemy, turn.brkSplit[1], turn.dmgSplit[1], "BREAK")
    elif turn.targeting == Targeting.AOE:
        # AOE Attack
        for enemy in enemyTeam:
            enemiesHit.append(enemy)
            a, b = processEnemy(turn, enemy, turn.brkSplit[0], turn.dmgSplit[0])
            newDebuff.extend(a)
            newDelay.extend(b)
    elif turn.targeting == Targeting.SPECIAL:
        enemy = findBestEnemy(char, enemyTeam, buffList, debuffList, turn) if turn.targetID == -1 else  enemyTeam[turn.targetID]
        enemiesHit.append(enemy)
        if turn.moveName == "RobinConcertoDMG":
            _, _ = processEnemy(turn, enemy, turn.brkSplit[0], turn.dmgSplit[0], 1.0, 2.5)
        elif turn.moveName == "RobinMoonlessMidnight":
            _, _ = processEnemy(turn, enemy, turn.brkSplit[0], turn.dmgSplit[0], 1.0, 2.5 + 4.5)
        else:
            _, _ = processEnemy(turn, enemy, turn.brkSplit[0], turn.dmgSplit[0])
    else :
        enemy = findBestEnemy(char, enemyTeam, buffList, debuffList, turn) if turn.targetID == -1 else enemyTeam[turn.targetID]
        enemiesHit.append(enemy)
        a, b = processEnemy(turn, enemy, turn.brkSplit[0], turn.dmgSplit[0])
        newDebuff.extend(a)
        newDelay.extend(b)
        if enemy.hasAdj and (turn.brkSplit[1] > 0 or (turn.dmgSplit[1] > 0)):
            for enemyID in enemy.adjacent:
                adj_enemy = enemyTeam[enemyID]
                enemiesHit.append(adj_enemy)
                a, b = processEnemy(turn, adj_enemy, turn.brkSplit[1], turn.dmgSplit[1])
                newDebuff.extend(a)
                newDelay.extend(b)

    if healingList != []:
        for i in range(len(playerTeam)):
            Heal = healingList[i]
            character = playerTeam[i]
            if Heal.target == character.role:
                if Heal.scaling != Scaling.Other:
                    enemy = findBestEnemy(char, enemyTeam, buffList, debuffList, turn) if turn.targetID == -1 else enemyTeam[turn.targetID]
                    character.ChangeHpValue(Heal.val[0] * getBaseValue(character, buffList, turn) * getMulOGH(character,enemy,buffList,debuffList,turn))
                    Total_HP_Change = Total_HP_Change + abs(Heal.val[0]) * getBaseValue(character, buffList, turn) * getMulOGH(character,enemy,buffList,debuffList,turn)
                elif Heal.scaling == Scaling.Other:
                    enemy = findBestEnemy(char, enemyTeam, buffList, debuffList, turn) if turn.targetID == -1 else enemyTeam[turn.targetID]
                    character.ChangeHpValue(Heal.val[0] * getMulOGH(character, enemy,buffList, debuffList,turn))
                    Total_HP_Change = Total_HP_Change + abs(Heal.val[0]) * getMulOGH(character, enemy,buffList, debuffList,turn)
            elif Heal.target == Role.ALL:
                if Heal.scaling != Scaling.Other:
                    enemy = findBestEnemy(char, enemyTeam, buffList, debuffList, turn) if turn.targetID == -1 else enemyTeam[turn.targetID]
                    character.ChangeHpValue(Heal.val[0] * getBaseValue(character, buffList, turn) * getMulOGH(character,enemy,buffList,debuffList,turn))
                    Total_HP_Change = Total_HP_Change + abs(Heal.val[0]) * getBaseValue(character, buffList, turn) * getMulOGH(character,enemy,buffList,debuffList,turn)
                elif Heal.scaling == Scaling.Other:
                    enemy = findBestEnemy(char, enemyTeam, buffList, debuffList, turn) if turn.targetID == -1 else enemyTeam[turn.targetID]
                    character.ChangeHpValue(Heal.val[0] * getMulOGH(character,enemy,buffList,debuffList,turn))
                    Total_HP_Change = Total_HP_Change + abs(Heal.val[0]) * getMulOGH(character,enemy,buffList,debuffList,turn)

    return Result(turn.charName, turn.charRole, turn.atkType, turn.element, anyBroken, turnDmg, wbDmg, Total_HP_Change,turn.errGain * charERR, turn.moveName, enemiesHit, preHitStatus), newDebuff, newDelay

def handleEnergyFromBuffs(buffList: list[Buff], debuffList: list[Debuff], playerTeam: list[Character], enemyTeam: list[Enemy]) -> list[Buff]:
    errBuffs, newList = [], []
    for buff in buffList:
        if buff.buffType == StatTypes.ERR_T or buff.buffType == StatTypes.ERR_F:
            errBuffs.append(buff)
        else:
            newList.append(buff)
    for eb in errBuffs:
        char = findCharRole(playerTeam, eb.target)
        placeholderTurn = Turn(char.name, char.role, 0, Targeting.NA, [AtkType.SPECIAL], [char.element], [0, 0], [0, 0], 0, char.scaling, 0, "PlaceHolderTurn: ERR")
        charERR = getMulERR(char, enemyTeam[0], buffList, debuffList, placeholderTurn) if ((eb.buffType == StatTypes.ERR_T) and not char.specialEnergy) else 1
        errToAdd = eb.getBuffVal() * charERR
        char.addEnergy(errToAdd)
        logger.info(f"ERR    > {errToAdd:.3f} energy added to {char.name} from {eb.name} | {char.name} Energy: {char.currEnergy:.3f}")
    return newList

def handleSPFromBuffs(buffList: list[Buff], spTracker: SpTracker) -> list[Buff]:
    newList = []
    for buff in buffList:
        if buff.buffType == StatTypes.SKLPT:
            spTracker.addSP(buff.getBuffVal() if buff.getBuffVal() > 0 else 0)
            spTracker.redSP(buff.getBuffVal() if buff.getBuffVal() < 0 else 0)
        else:
            newList.append(buff)
    return newList


# noinspection DuplicatedCode,PyUnusedLocal
def handleSpec(specStr: str, unit: Character, playerTeam: list[Character], summons: list[Summon], enemyTeam: list[Enemy], buffList: list[Buff], debuffList: list[Debuff], typ: str, manualMode = False) -> Special:
    gauge = enemyTeam
    specChar = findCharName(playerTeam, specStr)
    placeHolderTurn = Turn(specChar.name, specChar.role, -1, Targeting.NA, [AtkType.SPECIAL], [specChar.element], [0, 0], [0, 0], 0, specChar.scaling, 0, "PH Turn")
    if typ == "START":
        match specStr:
            case "Aventurine":
                avenDef = getBaseValue(specChar, buffList, placeHolderTurn)
                aggroList = addEnergy(playerTeam, enemyTeam, 0, atkRatio, buffList)
                bbList = [2 * aggroList[i] if i == specChar.pos else 1 * aggroList[i] for i in range(4)]
                return Special(name=specStr, attr1=avenDef, attr2=sum(bbList), enemies=gauge)

            case "Bronya":
                cd = getCharStat(StatTypes.CD_PERCENT, specChar, enemyTeam[0], buffList, [], placeHolderTurn)
                cd = cd - findBuffName(buffList, "BronyaUltCD").getBuffVal() if "BronyaUltATK" in getBuffNames(buffList) else cd
                return Special(name=specStr, attr1=cd, enemies=gauge)

            case "DrRatio":
                enemyDebuffs = [countDebuffs(e.enemyID, debuffList) for e in enemyTeam]
                canUlt = ("RobinFuaCD" in getBuffNames(buffList)) if inTeam(playerTeam, "Robin") else True
                return Special(name=specStr, attr1=enemyDebuffs, attr2=canUlt, enemies=gauge)

            case "Feixiao":
                enemyDebuffs = [countDebuffs(e.enemyID, debuffList) for e in enemyTeam]
                feixiaoTurn = True if specChar.name == "Feixiao" else False
                if inTeam(playerTeam, "Robin") and inTeam(playerTeam, "Bronya"):
                    canUlt = ("RobinFuaCD" in getBuffNames(buffList) and "BronyaUltATK" in getBuffNames(buffList))
                elif inTeam(playerTeam, "Robin"):
                    canUlt = "RobinFuaCD" in getBuffNames(buffList)
                elif inTeam(playerTeam, "Bronya"):
                    canUlt = "BronyaUltATK" in getBuffNames(buffList)
                else:
                    canUlt = True
                return Special(name=specStr, attr1=canUlt, attr2=feixiaoTurn, attr3=enemyDebuffs, enemies=gauge)

            case "Firefly":
                res1 = getScalingValues(specChar, buffList, [AtkType.ALL])
                res2 = getCharStat(StatTypes.BE_PERCENT, specChar, enemyTeam[specChar.defaultTarget], buffList, debuffList, placeHolderTurn)
                return Special(name=specStr, attr1=res1, attr2=res2, enemies=gauge)

            case "Fuxuan":
                lst = addEnergy(playerTeam, enemyTeam, 0, atkRatio, buffList)
                return Special(name=specStr, attr1=lst, enemies=gauge)

            case "Gallagher":
                beStat = getCharStat(StatTypes.BE_PERCENT, specChar, enemyTeam[0], buffList, debuffList, placeHolderTurn)
                canUlt = False if unit.name == "Gallagher" else True
                return Special(name=specStr, attr1=beStat, attr2=canUlt, enemies=gauge)

            case "HarmonyMC":
                hmcBE = getCharStat(StatTypes.BE_PERCENT, specChar, enemyTeam[specChar.defaultTarget], buffList, debuffList, placeHolderTurn)
                return Special(name=specStr, attr1=hmcBE, enemies=gauge)

            case "HuntM7":
                master = findCharRole(playerTeam, findCharName(playerTeam, "HuntM7").masterRole)
                return Special(name=specStr, attr1=master.element, enemies=gauge)

            case "HuoHuo":
                lst = []
                for char in [char for char in playerTeam if char.name != "HuoHuo"]:
                    lst.append([0 if char.specialEnergy else char.maxEnergy, char.role])
                return Special(name=specStr, attr1=lst[0], attr2=lst[1], attr3=lst[2], enemies=gauge)

            case "Jiaoqiu":
                ashenList = [db.stacks for db in debuffList if db.name == "AshenRoasted"]
                maxStacks = max(ashenList) if len(ashenList) > 0 else 0
                tickField = True if unit.name == "Jiaoqiu" else False
                targetStatus = []
                for enemy in enemyTeam:
                    targetStatus.append("SpringVULN" in getBuffNames([debuff for debuff in debuffList if debuff.target == enemy.enemyID]))
                ehr = getCharStat(StatTypes.EHR_PERCENT, specChar, enemyTeam[0], buffList, debuffList, placeHolderTurn)
                return Special(name=specStr, attr1=ehr, attr2=maxStacks, attr3=tickField, attr4=targetStatus, enemies=gauge)

            case "Lingsha":
                fuyuan = findCharName(summons, "Fuyuan")
                canUlt = True if fuyuan.currAV > max([char.currAV for char in playerTeam]) else False
                charBE = getCharStat(StatTypes.BE_PERCENT, specChar, enemyTeam[0], buffList, debuffList, placeHolderTurn)
                return Special(name=specStr, attr1=canUlt, enemies=gauge, attr3=charBE)

            case "Moze":
                res = ("RobinFuaCD" in getBuffNames(buffList)) if inTeam(playerTeam, "Robin") else True
                return Special(name=specStr, attr1=res, enemies=gauge)

            case "Rappa":
                atkStat = getScalingValues(specChar, buffList, [AtkType.ALL])
                return Special(name=specStr, attr1=atkStat, enemies=gauge, attr2=inTeam(playerTeam, "RuanMei"))

            case "Robin":
                atk = getBaseValue(specChar, buffList, placeHolderTurn)
                if "RobinUltBuff" in getBuffNames(buffList):
                    atk -= findBuffName(buffList, "RobinUltBuff").getBuffVal()
                return Special(name=specStr, attr1=atk, enemies=gauge)

            case "RuanMei":
                be = getCharStat(StatTypes.BE_PERCENT, specChar, enemyTeam[0], buffList, debuffList, placeHolderTurn)
                return Special(name=specStr, attr1=be, enemies=gauge)

            case "Sparkle":
                cdStat = getCharStat(StatTypes.CD_PERCENT, specChar, enemyTeam[0], buffList, [], placeHolderTurn)
                if "EarthlyTeamCD" in getBuffNames(buffList):
                    cdStat -= findBuffName(buffList, "EarthlyTeamCD").getBuffVal()
                return Special(name=specStr, attr1=cdStat, enemies=gauge)

            case "Sunday":
                if inTeam(playerTeam, "JingYuan"):
                    summonRole = Role.LIGHTNINGLORD
                elif inTeam(playerTeam, "Topaz"):
                    summonRole = Role.NUMBY
                else:
                    summonRole = None
                energyCap = findCharRole(playerTeam, specChar.targetRole).maxEnergy
                cdStat = getCharStat(StatTypes.CD_PERCENT, specChar, enemyTeam[0], buffList, [], placeHolderTurn)
                sundayTurn = unit.name == "Sunday"
                return Special(name=specStr, attr1=summonRole, attr2=energyCap, attr3=cdStat, attr4=sundayTurn, enemies=gauge)

            case "Topaz":
                fireWeak = hasWeakness(Element.FIRE, enemyTeam)
                canUlt = ("RobinFuaCD" in getBuffNames(buffList)) if inTeam(playerTeam, "Robin") else True
                return Special(name=specStr, attr1=fireWeak, attr2=canUlt, enemies=gauge)

            case "Yunli":
                yunliSlot = specChar.pos
                lst = addEnergy(playerTeam, enemyTeam, 0, atkRatio, buffList)
                return Special(name=specStr, attr1=lst[yunliSlot], enemies=gauge)

            case "Sushang":
                HasExtraSwordStance = True if "SushangUltimateAttack" in getBuffNames(buffList) else False
                return Special(name=specStr, attr1=HasExtraSwordStance,attr2=enemyTeam, enemies=gauge)

            case "Mem":
                RmcBuffs = []
                Temporary = []
                HasMemosprite = False
                SpecialEnergyCharacter = []
                DpsEnergy = 0
                for buffs in buffList:
                    Temporary.append(buffs)
                for ActualBuffs in Temporary:
                    if ActualBuffs.target == Role.SUP1:
                        RmcBuffs.append(ActualBuffs)
                energyList = addEnergy(playerTeam, enemyTeam, 0, atkRatio, buffList)
                cdStat = getCharStat(StatTypes.CD_PERCENT, specChar, enemyTeam[0], buffList, [], placeHolderTurn)
                for char in playerTeam:
                    if char.specialEnergy == True:
                        SpecialEnergyCharacter.append(char.name)
                    if char.role == Role.DPS:
                        DpsEnergy = char.maxEnergy
                        if char.hasMemosprite == True:
                            HasMemosprite = True
                return Special(name=specStr, attr1=RmcBuffs, attr2=sum(energyList)/len(playerTeam), attr3= cdStat, attr4=DpsEnergy,attr5=HasMemosprite,attr6=SpecialEnergyCharacter ,enemies=gauge)

            case "Tribbie":
                CharacterList = []
                TeamHP = 0
                for character in playerTeam:
                    CharacterList.append(character.name)
                    if character.name != "Tribbie" and character.role != Role.MEMO1 and character.role != Role.MEMO2 and character.role != Role.MEMO3:
                        TeamHP = TeamHP + getCharMaxHP(character, character.lightcone, buffList)
                UltIsActive = True if "TribbieUltVuln" in getBuffNames(buffList) else False
                return Special(name=specStr, attr1=CharacterList, attr2=TeamHP, attr3= UltIsActive, enemies=gauge)

            case _:
                return Special(specStr, enemies=gauge)

    elif typ == "END":
        match specStr:
            case "Robin":
                slowestChar = sorted([char for char in playerTeam if char.name != "Robin"], key=lambda x: x.currSPD)[0]
                res = True if slowestChar.name == "Yunli" else unit.role == slowestChar.role
                return Special(name=specStr, attr1=res)

            case "Sunday":
                targetChar = findCharRole(playerTeam, specChar.targetRole)
                targetCRStat = getCharStat(StatTypes.CR_PERCENT, targetChar, enemyTeam[0], buffList, [], placeHolderTurn)
                return Special(name=specStr, attr1=targetCRStat)

            case _:
                return Special(name=specStr)

def wbDelay(ele: Element, charBE: float, enemy: Enemy) -> list[Delay]:
    res = [Delay("STDBreakDelay", 0.25, enemy.enemyID, True, False)]
    breakName = f"{ele.value}-break"
    if ele in [Element.PHYSICAL, Element.WIND, Element.FIRE, Element.LIGHTNING]: # standard break delay
        pass # no additional effects (for now)
    elif ele == Element.ICE:
        res.append(Delay(breakName, 0.50, enemy.enemyID, True, False))
    elif ele == Element.QUANTUM:
        res.append(Delay(breakName, 0.2 * charBE, enemy.enemyID, True, False))
    elif ele == Element.IMAGINARY:
        res.append(Delay(breakName, 0.3 * charBE, enemy.enemyID, True, False))
    return res

def wbDebuff(ele: Element, charRole: Role, charBE: float, enemy: Enemy) -> Debuff:
    debuffName = f"{enemy.name} {ele.value}-break"
    if ele == Element.PHYSICAL:
        return Debuff(debuffName, charRole, StatTypes.BLEED, 2 * wbMultiplier * enemy.maxToughnessMul * charBE, enemy.enemyID, [AtkType.ALL], 2, 1, True, [0, 0], False)
    elif ele == Element.FIRE:
        return Debuff(debuffName, charRole, StatTypes.BURN, 1 * wbMultiplier * charBE, enemy.enemyID, [AtkType.ALL], 2, 1, True, [0, 0], False)
    elif ele == Element.ICE:
        return Debuff(debuffName, charRole, StatTypes.FREEZE, 1 * wbMultiplier * charBE, enemy.enemyID, [AtkType.ALL], 1, 1, False, [0, 0], False)
    elif ele == Element.WIND:
        return Debuff(debuffName, charRole, StatTypes.WINDSHEAR, 3 * wbMultiplier * charBE, enemy.enemyID, [AtkType.ALL], 2, 1, True, [0, 0], False)
    elif ele == Element.LIGHTNING:
        return Debuff(debuffName, charRole, StatTypes.SHOCK, 2 * wbMultiplier * charBE, enemy.enemyID, [AtkType.ALL], 2, 1, True, [0, 0], False)
    elif ele == Element.QUANTUM:
        return Debuff(debuffName, charRole, StatTypes.ENTANGLE, 1.8 * wbMultiplier * enemy.maxToughnessMul * charBE, enemy.enemyID, [AtkType.ALL], 1, 1, False, [0, 0], False)
    elif ele == Element.IMAGINARY:
        return Debuff(debuffName, charRole, StatTypes.SPD_PERCENT, -0.1, enemy.enemyID, [AtkType.ALL], 1, 1, False, [0, 0], False)

def findBestEnemy(char: Character, enemyTeam: list[Enemy], buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> Enemy:
    bestEnemy = None
    bestMul = 0
    for enemy in enemyTeam:
        currMul = getMulENEMY(char, enemy, buffList, debuffList, turn)
        if currMul > bestMul:
            bestMul = currMul
            bestEnemy = enemy
    return bestEnemy

def expectedDMG(baseDMG: float, cr: float, cd: float) -> float:
    return (baseDMG * (1 - cr)) + (baseDMG * cr * cd)

# Functions to get various multipliers
def checkValidList(list1: list, list2: list) -> bool:
    if (AtkType.ALL in list2) or (AtkType.ALL in list1) or (Role.ALL in list1) or (Role.ALL in list2):
        return True
    set2 = set(list2)
    return any(l1 in set2 for l1 in list1)

def getBaseValue(char, buffList: list[Buff], turn: Turn) -> float:
    if turn.scaling == Scaling.ATK or turn.scaling == Scaling.DEF or turn.scaling == Scaling.HP: # normal scaling attacks
        return getScalingValues(char, buffList, turn.atkType)
    else:
        return 0

def getScalingValues(char: Character, buffList: list[Buff], atkType: list[AtkType]) -> float:
    base, mul, flat = char.getBaseStat()
    mulChecker = StatTypes.ATK_PERCENT if char.scaling == Scaling.ATK else (StatTypes.HP_PERCENT if char.scaling == Scaling.HP else StatTypes.DEF_PERCENT)
    flatChecker = StatTypes.ATK if char.scaling == Scaling.ATK else (StatTypes.HP if char.scaling == Scaling.HP else StatTypes.DEF)
    for buff in buffList:
        if buff.target != char.role:
            continue
        if not checkValidList(atkType, buff.atkType):
            continue
        if buff.buffType == mulChecker:
            mul += buff.getBuffVal()
        elif buff.buffType == flatChecker:
            flat += buff.getBuffVal()
    return base * (1 + mul) + flat

def processTurnList(turnList: list[Turn], playerTeam, summons, eTeam, teamBuffs, enemyDebuffs, advList, delayList, healList, spTracker, dmgTracker: DmgTracker, manualMode=False):

    while turnList:
        turn = turnList[0]

        spTracker.addSP(turn.spChange if turn.spChange > 0 else 0)
        spTracker.redSP(turn.spChange if turn.spChange < 0 else 0)

        logging.warning(f"    TURN   - {turn}")
        logging.debug("\n        ----------Char Buffs----------")
        [logging.debug(f"        {buff}") for buff in teamBuffs if (buff.target == turn.charRole and checkValidList(turn.atkType, buff.atkType))]
        logging.debug("        ----------End of Buff List----------")
        logging.debug("\n        ----------Enemy Debuffs----------")
        [logging.debug(f"        {debuff}") for debuff in enemyDebuffs if debuff.target == turn.targetID]
        logging.debug("        ----------End of Debuff List----------")
        [logging.debug(f"        {heal}") for heal in healList]
        logging.debug("        ----------End of Healing List----------")

        res, newDebuffs, newDelays = handleTurn(turn, playerTeam, eTeam, teamBuffs, enemyDebuffs, healList,manualMode=manualMode)
        for character in playerTeam:
            oldMaxHp = character.maxHP
            character.maxHP = getCharMaxHP(character, character.lightcone, teamBuffs)
            character.currHP = character.currHP*(character.maxHP/oldMaxHp)
        healList = []
        dmgTracker.addActionDMG(res.turnDmg)
        dmgTracker.addWeaknessBreakDMG(res.wbDmg)
        dmgTracker.addHealing(res.Healing)
        char = findCharRole(playerTeam, res.charRole)
        result = f"RESULT - {res} | {char.name} Energy: {min(char.maxEnergy, char.currEnergy + res.errGain):.0f}/{char.maxEnergy}"
        logging.warning(f"    {result}")
        if manualMode:
            print(result)
        teamBuffs, enemyDebuffs, advList, delayList, healList = handleAdditions(playerTeam, eTeam, teamBuffs, enemyDebuffs, advList, delayList, healList, [], newDebuffs, [], newDelays, [])
        for char in playerTeam + summons:
            if char.role == turn.charRole:
                tempB, tempDB, tempA, tempD, newTurns, tempH = char.ownTurn(turn, res)
            else:
                tempB, tempDB, tempA, tempD , newTurns, tempH = char.allyTurn(turn, res)
            teamBuffs, enemyDebuffs, advList, delayList, healList = handleAdditions(playerTeam, eTeam, teamBuffs, enemyDebuffs, advList, delayList, healList,tempB, tempDB, tempA, tempD, tempH)
            turnList.extend(newTurns)

        turnList = turnList[1:]

    return teamBuffs, enemyDebuffs, advList, delayList, turnList, healList

def handleUlts(playerTeam, summons, eTeam, teamBuffs, enemyDebuffs, advList, delayList, healingList,spTracker, dmgTracker, manualMode = False, simAV = 0):

    turnList = []
    # Check if any unit can ult
    for char in playerTeam:
        if char.canUseUlt():
            action, target = "Y", -1
            if manualMode:
                action, target = manualModule(spTracker, playerTeam, summons, eTeam, simAV, char, "ULT")
            if action == "Y":
                ult = f"ULT    > {char.name} used their ultimate"
                logging.critical(ult)
                if manualMode:
                    print(ult)
                bl, dbl, al, dl, tl, hl = char.useUlt(target)
                teamBuffs, enemyDebuffs, advList, delayList, healingList = handleAdditions(playerTeam, eTeam, teamBuffs, enemyDebuffs, advList, delayList, healingList,bl, dbl, al, dl, hl)
                turnList.extend(tl)

        # Handle any new attacks from unit ults
        teamBuffs, enemyDebuffs, advList, delayList, turnList, healingList = processTurnList(turnList, playerTeam, summons, eTeam, teamBuffs, enemyDebuffs, advList, delayList, healingList,spTracker, dmgTracker, manualMode=manualMode)

        # Handle any errGain from unit ults
        teamBuffs = handleEnergyFromBuffs(teamBuffs, enemyDebuffs, playerTeam, eTeam)

        # Add/Minus any SP changes from special effects
        teamBuffs = handleSPFromBuffs(teamBuffs, spTracker)

    return teamBuffs, enemyDebuffs, advList, delayList, healingList

def handleSpecialEffects(unit, playerTeam, summons, eTeam, teamBuffs, enemyDebuffs, advList, delayList, healList, checkType, spTracker, dmgTracker, manualMode = False):

    turnList = []
    # Apply any special effects
    for char in playerTeam:
        spec = char.special()
        specRes = handleSpec(spec, unit, playerTeam, summons, eTeam, teamBuffs, enemyDebuffs, checkType, manualMode=manualMode)
        if checkType == "START":
            bl, dbl, al, dl, tl, hl = char.handleSpecialStart(specRes)
        else:
            bl, dbl, al, dl, tl, hl = char.handleSpecialEnd(specRes)
        teamBuffs, enemyDebuffs, advList, delayList, healList = handleAdditions(playerTeam, eTeam, teamBuffs, enemyDebuffs, advList, delayList, healList, bl, dbl, al, dl, hl)
        turnList.extend(tl)

    # Handle any attacks from special attacks
    teamBuffs, enemyDebuffs, advList, delayList, turnList, healList = processTurnList(turnList, playerTeam, summons, eTeam, teamBuffs, enemyDebuffs, advList, delayList, healList, spTracker, dmgTracker, manualMode)

    # Add Energy if any was provided from special effects
    teamBuffs = handleEnergyFromBuffs(teamBuffs, enemyDebuffs, playerTeam, eTeam)

    # Add/Minus any SP changes from special effects
    teamBuffs = handleSPFromBuffs(teamBuffs, spTracker)

    return teamBuffs, enemyDebuffs, advList, delayList, healList

def manualModule(spTracker: SpTracker, playerTeam: list[Character], summons: list[Summon], enemyTeam: list[Enemy], simAV: float, unit, actionType) -> tuple[str, int]:
    unit.takeTurn()
    print("===============================================================================================================================================================")
    print(f"INFO   > CURRENT AV: {simAV:.3f} | SP: {spTracker.getDisp()}\n")
    res1 = "TEAMAV > "
    res2 = "ENERGY > "
    for char in [p for p in (playerTeam + summons)]:
        res1 += f"{char.name}: {char.currAV:.3f} | "
        res2 += f"{char.name}: {char.currEnergy:.0f}/{char.maxEnergy} | "
    print(res1)
    print(res2 + "\n")
    res = "ENEMY  > "
    for enemy in enemyTeam:
        res += f"Enemy {enemy.enemyID} AV: {enemy.currAV:.3f} Toughness: {enemy.gauge:.2f}/{enemy.toughness:.2f} | "
    print(res + "\n")
    output = ""
    userAction = ""
    if actionType == "TURN":
        while userAction.upper() not in {"E", "A", "MEMO"}:
            userAction = input(f"INPUT  > {unit.name} | Energy: {unit.currEnergy:.0f}/{unit.maxEnergy} | Move (E/A/MEMO): ")
            if userAction.upper() not in {"E", "A", "MEMO"}:
                print("Invalid Input!")
                continue
            if userAction.upper() == "E":
                string = "SKILL"
            elif userAction.upper() == "MEMO":
                string = "MEMOATTACK"
            else:
                string = "BASIC"
            output = f"    {unit.name} used {string} against Enemy "
    elif actionType == "ULT":
        while userAction.upper() not in {"Y", "N"}:
            userAction = input(f"INPUT  > {unit.name} Energy: {unit.currEnergy:.0f}/{unit.maxEnergy} | Use Ultimate? (Y/N): ")
            if userAction.upper() not in {"Y", "N"}:
                print("Invalid Input!")
                continue
            if userAction.upper() == "Y":
                output = f"    {unit.name} used their ultimate against Enemy "
            else:
                output = f"    {unit.name} holds their ultimate"
    target = -1
    while target not in range(len(enemyTeam)) and userAction.upper() != "N":
        target = int(input(f"TARGET > Select Enemy Target {[enemy.enemyID for enemy in enemyTeam]}: "))
        if target not in range(len(enemyTeam)):
            print("Invalid Input!")
    if actionType == "ULT" and userAction == "N":
        pass
    else:
        output += str(target)
    print(f"<<< {output}     >>>")
    print("===============================================================================================================================================================")
    return userAction.upper(), target

# Use this function to get the stat of the character, without any associated base multipliers:
# e.g. 1 + dmg%, 1 + err% etc.
def getCharStat(query: StatTypes, char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> float:
    res = 0
    pwrList = [query, penDct[char.element]] if query == StatTypes.PEN else [query]

    res += sum([buff.getBuffVal() for buff in buffList if ((buff.target == char.role) and checkValidList(turn.atkType, buff.atkType) and buff.buffType in pwrList and (not buff.reqBroken or enemy.broken))])
    res += sum([debuff.getDebuffVal() for debuff in debuffList if ((debuff.target == enemy.enemyID) and checkValidList(turn.atkType, debuff.atkType) and debuff.debuffType in pwrList) and checkValidList([char.role], debuff.validFor)])

    match query:
        case StatTypes.BE_PERCENT:
            return res + char.relicStats.getBE() # base multiplier of 1 not added
        case StatTypes.WB_EFF:
            return res # base multiplier of 1 not added
        case StatTypes.EHR_PERCENT:
            return res + char.relicStats.getEHR()
        case StatTypes.ERS_PERCENT:
            return res + char.relicStats.getERS()
        case StatTypes.CR_PERCENT:
            return res + char.relicStats.getCR() # base value of 0.05 added
        case StatTypes.CD_PERCENT:
            return res + char.relicStats.getCD() # base value of 0.5 added, base multi of 1 not added
        case StatTypes.DMG_PERCENT:
            return res + char.relicStats.getDMG() # base value of 1 not added
        case StatTypes.ERR_PERCENT:
            return res + char.relicStats.getERR() # base value of 1 not added
        case StatTypes.OGH_PERCENT:
            return res + char.relicStats.getOGH() # base multiplier of 1 not added
        case StatTypes.BRK_DMG:
            return res
        case StatTypes.SBRK_DMG:
            return res
        case StatTypes.SHRED:
            return res
        case StatTypes.PEN:
            return res
        case StatTypes.VULN:
            return res
        case StatTypes.TRUEDAMAGE:
            return res

# Use these functions to directly get the multiplier against the specified enemy for the specified char
def getMulBE(char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> float:
    return getCharStat(StatTypes.BE_PERCENT, char, enemy, buffList, debuffList, turn) + 1

def getMulWBE(char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> float:
    return getCharStat(StatTypes.WB_EFF, char, enemy, buffList, debuffList, turn) + 1

def getMulEHR(char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> float:
    return getCharStat(StatTypes.EHR_PERCENT, char, enemy, buffList, debuffList, turn)

def getMulERS(char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> float:
    return getCharStat(StatTypes.ERS_PERCENT, char, enemy, buffList, debuffList, turn)

def getMulCR(char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> float:
    return min(1.0, getCharStat(StatTypes.CR_PERCENT, char, enemy, buffList, debuffList, turn))

def getMulCD(char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> float:
    return getCharStat(StatTypes.CD_PERCENT, char, enemy, buffList, debuffList, turn) + 1

def getMulDMG(char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> float:
    return getCharStat(StatTypes.DMG_PERCENT, char, enemy, buffList, debuffList, turn) + 1

def getMulERR(char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> float:
    return getCharStat(StatTypes.ERR_PERCENT, char, enemy, buffList, debuffList, turn) + 1

def getMulOGH(char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> float:
    return getCharStat(StatTypes.OGH_PERCENT, char, enemy, buffList, debuffList, turn) + 1

def getMulBrkDMG(char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> float:
    return getCharStat(StatTypes.BRK_DMG, char, enemy, buffList, debuffList, turn) + 1

def getMulSuperBrkDMG(char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> float:
    return getCharStat(StatTypes.SBRK_DMG, char, enemy, buffList, debuffList, turn) + 1

def getMulSHRED(char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> float:
    shred = getCharStat(StatTypes.SHRED, char, enemy, buffList, debuffList, turn)
    return min(1.0, 100 / ((enemy.level + 20) * (1 - shred) + 100))

def getMulVULN(char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> float:
    vuln = getCharStat(StatTypes.VULN, char, enemy, buffList, debuffList, turn)
    return min(10.0, 1 + vuln)

def getMulPEN(char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> float:
    pen = getCharStat(StatTypes.PEN, char, enemy, buffList, debuffList, turn)
    pen = pen - enemy.getRes(turn.element[0])
    return min(10.0, 1 + pen)

def getTRUEDAMAGE(char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff],turn: Turn) -> float:
    return getCharStat(StatTypes.TRUEDAMAGE, char, enemy, buffList, debuffList, turn) + 1

def getMulUNI(enemy: Enemy) -> float:
    return enemy.getUniMul()

def getMulENEMY(char: Character, enemy: Enemy, buffList: list[Buff], debuffList: list[Debuff], turn: Turn) -> float:
    shredMul = getMulSHRED(char, enemy, buffList, debuffList, turn)
    vulnMul = getMulVULN(char, enemy, buffList, debuffList, turn)
    penMul = getMulPEN(char, enemy, buffList, debuffList, turn)
    TrueDamageMul = getTRUEDAMAGE(char, enemy, buffList, debuffList, turn)
    uniMul = getMulUNI(enemy)
    return shredMul * vulnMul * penMul * TrueDamageMul * uniMul