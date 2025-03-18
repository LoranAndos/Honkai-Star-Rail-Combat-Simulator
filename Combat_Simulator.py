import logging

from Characters.Luocha import Luocha
from Characters.Sparkle import Sparkle
from Characters.Sushang import Sushang
from Characters.Tingyun import Tingyun
from Characters.Rmc import Rmc
from Characters.Tribbie import Tribbie
from Memosprites.Mem import Mem
from MainFunctions import *
from Enemy import *

cycles = 5  # comment out this line if running the simulator from an external script
log = True
manual = False


# noinspection PyUnboundLocalVariable,PyUnusedLocal
def startSimulator(cycleLimit=5, s1: Character = None, s2: Character = None, s3: Character = None, s4: Character = None,
                   outputLog: bool = False, enemyModule=None, manualMode=False) -> str:
    # =============== SETTINGS ===============
    # Enemy Settings
    numEnemies = 3
    enemyLevel = [95, 95, 95]  # make sure that the number of entries in this list is the same as "numEnemies"
    enemyTypes = [EnemyType.ELITE, EnemyType.BOSS, EnemyType.ELITE]  # make sure that the number of entries in this list is the same as "numEnemies"
    enemySPD = [145.2, 158.4, 145.2]  # make sure that the number of entries in this list is the same as "numEnemies"
    toughness = [100, 160, 100]  # make sure that the number of entries in this list is the same as "numEnemies"
    attackRatio = atkRatio  # from Misc.py
    weaknesses = [Element.PHYSICAL]
    actionOrder = [1, 1, 2]  # determines how many attacks enemies will have per turn
    enemyModule = EnemyModule(numEnemies, enemyLevel, enemyTypes, enemySPD, toughness,
                                                              attackRatio, weaknesses, actionOrder)
    # Character Settings
    # Small note: Make sure Rmc is always SUP1 and Dps Memo always Memo1
    if all([a is None for a in [s1, s2, s3, s4]]):
        slot1 = Sushang(0,Role.DPS,1,eidolon=6,targetPrio=Priority.DEFAULT)
        slot2 = Rmc(1,Role.SUP1,1,eidolon=6,targetPrio=Priority.DEFAULT)
        slot3 = Mem.Mem(2,Role.MEMO2,1,eidolon=6,targetPrio=Priority.DEFAULT)
        slot4 = Luocha(3,Role.SUS,1,eidolon=0,targetPrio=Priority.DEFAULT)
        slot5 = Tribbie(4,Role.SUP2,1,eidolon=0,targetPrio=Priority.DEFAULT)


    # Simulation Settings
    totalEnemyAttacks = 0
    logLevel = logging.DEBUG
    # CRITICAL: Only prints the main action taken during each turn + ultimates
    # WARNING: Prints the above plus details on all actions recorded during the turn (FuA/Bonus attacks etc.), and all AV adjustments
    # INFO: Prints the above plus buff and debuff expiry, speed adjustments, av of all chars at the start of each turn
    # DEBUG: Prints the above plus all associated buffs and debuffs present during each turn
    # =============== END OF SETTINGS ===============

    # Logging Config
    if not s1:
        playerTeam = [slot1, slot2, slot3, slot4, slot5]
    else:
        playerTeam = [s1, s2, s3, s4]

    if outputLog:
        log_folder = "Output"
        teamInfo = "".join([char.name for char in playerTeam])
        enemyInfo = f"_{enemyModule.numEnemies}Enemies_{cycleLimit}Cycles"
        logging.basicConfig(
            filename=f"{log_folder}/{teamInfo}{enemyInfo}.log",
            level=logLevel,
            format="%(message)s",
            filemode="w"
        )
    else:
        logging.disable(logging.CRITICAL)  # Disable all logging messages

    avLimit = cycleLimit * 100 + 50
    simAV = 0

    # Damage Module
    dmg = DmgTracker()

    # Skill Point Module
    startingSP = 3 + [p.relic1.name for p in playerTeam if p.relic1.setType == 4].count("Passerby of Wandering Cloud")
    maxSP = (8 if findCharName(playerTeam, "Sparkle").eidolon >= 4 else 7) if inTeam(playerTeam, "Sparkle") else 5
    spTracker = SpTracker(startingSP, maxSP)

    # Summons
    summons = addSummons([p for p in playerTeam if p.hasSummon])

    # Print Enemy Info
    eTeam = []
    for i in range(enemyModule.numEnemies):
        adjList = []
        if (i - 1) >= 0:
            adjList.append(i - 1)
        if (i + 1) < enemyModule.numEnemies:
            adjList.append(i + 1)
        eLevel = enemyModule.enemyLevel[i]
        eType = enemyModule.enemyTypes[i]
        eSPD = enemyModule.enemySPD[i]
        eToughness = enemyModule.toughness[i]
        eAction = enemyModule.actionOrder
        eWeaknesses = enemyModule.weaknesses

        eTeam.append(Enemy(i, eLevel, eType, eSPD, eToughness, eAction, eWeaknesses, adjList,CanDoDamage=False))

    manualPrint(manualMode,
                "===============================================================================================================================================================")
    logging.critical("Enemy Team:")
    manualPrint(manualMode, "Enemy Team:")
    for enemy in eTeam:
        logging.critical(enemy)
        manualPrint(manualMode, enemy)

    # Print Char Info
    logging.critical("\nPlayer Team:")
    manualPrint(manualMode, "\nPlayer Team:")
    for char in playerTeam:
        logging.critical(f"{char}\n")
        manualPrint(manualMode, f"{char}\n")

    # Setup equipment and char traces
    teamBuffs, enemyDebuffs, advList, delayList, healingList = [], [], [], [], []
    for char in playerTeam:
        initBuffs, initDebuffs, initAdv, initDelay, initHealing = char.equip()
        teamBuffs, enemyDebuffs, advList, delayList, healingList = handleAdditions(playerTeam, eTeam, teamBuffs, enemyDebuffs,
                                                                      advList, delayList, healingList,initBuffs, initDebuffs,
                                                                      initAdv, initDelay, initHealing)

    # Setup initial AV
    for char in playerTeam:
        initCharAV(char, teamBuffs)  # apply any pre-existing speed buffs

    # Setup initial currHp and Maxhp
    initCharCurrentHP_MaxHp(playerTeam, teamBuffs) # apply any pre-existing Hp buffs

    logging.warning("\nInitial AV Adjustments")
    avAdjustment(playerTeam, advList)  # apply any "on battle start" advances
    advList = []  # clear advList after applying

    logging.warning("\nInitial Enemy Delays")
    delayList = delayAdjustment(eTeam, delayList, enemyDebuffs)  # apply any "on battle start" delays

    allUnits = sortUnits(playerTeam + eTeam + summons)
    setPriority(allUnits)

    # Simulator Loop
    logging.critical("\n==========COMBAT SIMULATION STARTED==========")

    while simAV < avLimit:

        unit = allUnits[0]  # Find next turn
        av = unit.currAV
        simAV += av
        turnList = []
        if simAV > avLimit:  # don't parse turn once over avLimit
            break
        logging.critical("\n<<< NEW TURN >>>")
        # Reduce AV of all chars
        for u in allUnits:
            u.standardAVred(av)
            logging.info(
                f"-   {u.name} AV: {u.currAV:.3f} ENERGY: {u.currEnergy if u.isChar() and not u.isSummon() else 0:.3f} MaxHP: {u.maxHP:.3f} CurrHp {u.currHP:.3f}" )
        logging.info("")

        # Apply any special effects
        teamBuffs, enemyDebuffs, advList, delayList, healingList = handleSpecialEffects(unit, playerTeam, summons, eTeam, teamBuffs,
                                                                           enemyDebuffs, advList, delayList, healingList, "START",
                                                                           spTracker, dmg, manualMode=manualMode)

        if unit.isChar() and not unit.isSummon():
            # Check if any unit can ult
            teamBuffs, enemyDebuffs, advList, delayList, healingList = handleUlts(playerTeam, summons, eTeam, teamBuffs,
                                                                     enemyDebuffs, advList, delayList, healingList, spTracker, dmg,
                                                                     manualMode=manualMode, simAV=simAV)

        # Handle unit Turns
        if not unit.isChar():  # Enemy turn
            numAttacks = unit.takeTurn()
            totalEnemyAttacks += numAttacks
            action = f"ACTION > [ENEMY] TotalAV: {simAV:.3f} | TurnAV: {av:.3f} | {unit.name} | {numAttacks} attacks"
            logging.critical(action)
            manualPrint(manualMode, action)
            for i in range(numAttacks):
                for char in playerTeam:
                    bl, dbl, al, dl, tl, hl = char.useHit(unit.enemyID)
                    teamBuffs, enemyDebuffs, advList, delayList, healingList = handleAdditions(playerTeam, eTeam, teamBuffs,
                                                                                  enemyDebuffs, advList, delayList, healingList, bl,
                                                                                  dbl, al, dl, hl)
                    turnList.extend(tl)
            energyList = addEnergy(playerTeam, eTeam, numAttacks, enemyModule.attackRatios,teamBuffs)
            energyMsg = "    CharEnergy -"
            for i in range(len(playerTeam)):
                energyMsg += f" {playerTeam[i].name}: Hit {energyList[i]:.3f} Total: {playerTeam[i].currEnergy:.3f} |"
            logging.warning(energyMsg)
            dmg.addDebuffDMG(takeDebuffDMG(unit, playerTeam, teamBuffs, enemyDebuffs))
        elif unit.isChar() and not unit.isSummon():  # Character Turn
            if manualMode:
                moveType, target = manualModule(spTracker, playerTeam, summons, eTeam, simAV, unit, "TURN")
            else:
                moveType, target = unit.takeTurn(), unit.defaultTarget
            action = f"ACTION > [CHAR] TotalAV: {simAV:.3f} | TurnAV: {av:.3f} | {unit.name} | {moveType}-move"
            logging.critical(action)
            manualPrint(manualMode, action)
            teamBuffs = tickBuffs(unit, teamBuffs, "START")
            if moveType == "E":
                bl, dbl, al, dl, tl, hl = unit.useSkl(target)
            elif moveType == "A":
                bl, dbl, al, dl, tl, hl = unit.useBsc(target)
            elif moveType == "MEMO":
                bl, dbl, al, dl, tl, hl = unit.useMemo(target)
            else:
                manualPrint(manualMode, "Invalid move type!")
                bl, dbl, al, dl, tl, hl = [], [], [], [], [], []
            teamBuffs, enemyDebuffs, advList, delayList, healingList = handleAdditions(playerTeam, eTeam, teamBuffs, enemyDebuffs,
                                                                          advList, delayList, healingList, bl, dbl, al, dl, hl)
            turnList.extend(tl)
        elif unit.isChar() and unit.isSummon():
            action = f"ACTION > [SUMMON] TotalAV: {simAV:.3f} | TurnAV: {av:.3f} | {unit.name}"
            logging.critical(action)  # Summon logic
            manualPrint(manualMode, action)
            bl, dbl, al, dl, tl, hl = unit.takeTurn()
            teamBuffs, enemyDebuffs, advList, delayList, healingList = handleAdditions(playerTeam, eTeam, teamBuffs, enemyDebuffs,
                                                                          advList, delayList, healingList, bl, dbl, al, dl, hl)
            turnList.extend(tl)

        # Handle any pending attacks:
        teamBuffs, enemyDebuffs, advList, delayList, turnList, healingList  = processTurnList(turnList, playerTeam, summons, eTeam,
                                                                                teamBuffs, enemyDebuffs, advList,
                                                                                delayList, healingList, spTracker, dmg,
                                                                                manualMode=manualMode)

        # Handle any errGain from unit turns
        teamBuffs = handleEnergyFromBuffs(teamBuffs, enemyDebuffs, playerTeam, eTeam)

        # Check if any unit can ult
        teamBuffs, enemyDebuffs, advList, delayList, healingList = handleUlts(playerTeam, summons, eTeam, teamBuffs, enemyDebuffs,
                                                                 advList, delayList, healingList, spTracker, dmg,
                                                                 manualMode=manualMode, simAV=simAV)

        if unit.isChar() and not unit.isSummon():
            teamBuffs = tickBuffs(unit, teamBuffs, "END")  # THIS MARKS THE END OF THE PLAYER TURN
        elif not unit.isChar():
            enemyDebuffs = tickDebuffs(unit, enemyDebuffs)  # THIS MARKS THE END OF THE ENEMY TURN

        # Apply any special effects
        teamBuffs, enemyDebuffs, advList, delayList, healingList = handleSpecialEffects(unit, playerTeam, summons, eTeam, teamBuffs,
                                                                           enemyDebuffs, advList, delayList, healingList, "END",
                                                                           spTracker, dmg, manualMode=manualMode)

        # Check if any unit can ult
        teamBuffs, enemyDebuffs, advList, delayList, healingList = handleUlts(playerTeam, summons, eTeam, teamBuffs, enemyDebuffs,
                                                                 advList, delayList, healingList, spTracker, dmg,
                                                                 manualMode=manualMode, simAV=simAV)

        # Apply any speed adjustments
        spdAdjustment(playerTeam, teamBuffs)
        enemySPDAdjustment(eTeam, enemyDebuffs)

        # Reset the AV of the current unit by checking its current speed
        if not unit.isChar() or not unit.isSummon():
            resetUnitAV(unit, teamBuffs, enemyDebuffs)
            avLog = f"AV     > {unit.name} AV reset to {unit.currAV:.3f} | {unit.currSPD:.3f} SPD"
            logging.warning(avLog)
            manualPrint(manualMode, avLog)

        allUnits = sortUnits(allUnits)
        # Reset priorities
        setPriority(allUnits)

        # Apply any enemy delays
        delayList = delayAdjustment(eTeam, delayList, enemyDebuffs)

        # Apply any character/summon AV adjustments
        avAdjustment(playerTeam + summons, advList)
        advList = []

        # Reset Healing List
        healingList = []

        if unit.isChar() and unit.isSummon():
            resetUnitAV(unit, [], [])  # summons cannot be advanced during their own turn
            avLog = f"AV     > {unit.name} AV reset to {unit.currAV:.3f} | {unit.currSPD:.3f} SPD"
            logging.warning(avLog)
            manualPrint(manualMode, avLog)

        allUnits = sortUnits(allUnits)

    logging.critical("\n==========COMBAT SIMULATION ENDED==========")

    # Extra calculations
    for char in playerTeam:
        if char.name == "Yunli":
            char.hitMultiplier = char.ults / totalEnemyAttacks

    logging.critical("\n==========SIMULATION RESULTS==========")

    # Print damage info
    debuffDMG, charDMG = 0, 0
    dmgList = []
    for enemy in eTeam:
        debuffDMG += enemy.debuffDMG
    for char in playerTeam:
        res, currCharDMG = char.getTotalDMG()
        dmgList.append(currCharDMG)
        charDMG += currCharDMG
    dpavList = [i / avLimit for i in dmgList]
    percentList = [i / dmg.getTotalDMG() * 100 for i in dmgList]

    logging.critical(f"TOTAL TEAM DMG: {dmg.getTotalDMG():.3f} | AV: {avLimit}")
    logging.critical(f"TEAM DPAV: {dmg.getTotalDMG() / avLimit:.3f}")
    logging.critical(f"TOTAL TEAM HPGAIN: {dmg.getTotalHPGain():.3f} | TOTAL TEAM HPLOSS {dmg.getTotalHPLoss():.3f}")
    logging.critical(
        f"DEBUFF DMG: {dmg.getDebuffDMG():.3f} | CHAR DMG: {dmg.getActionDMG():.3f} | WB DMG: {dmg.getWeaknessBreakDMG():.3f}")
    logging.critical(
        f"SP GAINED: {spTracker.getSPGain()} | SP USED: {spTracker.getSPUsed()} | Enemy Attacks: {totalEnemyAttacks}")
    res = ""
    i = 0
    for char in playerTeam:
        res += f"\n{char.name} DPAV: {dpavList[i]:.3f}, {percentList[i]:.3f}%"
        i += 1

    logging.critical(f"{res}\n")

    for char in playerTeam:
        res, charDMG = char.getTotalDMG()
        logging.critical(
            f"{char.name} > Total DMG: {charDMG:.3f} | Basics: {char.basics} | Skills: {char.skills} | Ults: {char.ults} | FuAs: {char.fuas} | MemoAttacks: {char.MemoAttack} | Leftover AV: {char.currAV:.3f} | Excess Energy: {char.currEnergy:.3f}")
        logging.critical(res)

    return f"DPAV: {dmg.getTotalDMG() / avLimit:.3f} | SP Used: {spTracker.getSPUsed()}, SP Gain: {spTracker.getSPGain()}"


if __name__ == "__main__":
    # Start the simulator with logging output to a file
    fiveEnemies = EnemyModule(5, [85, 85, 85, 85, 85],
                              [EnemyType.ADD, EnemyType.ELITE, EnemyType.BOSS, EnemyType.ADD, EnemyType.ADD],
                              [100, 120, 144, 100, 100], [20, 60, 70, 20, 20], atkRatio, [Element.LIGHTNING], [1])
    print(startSimulator(cycleLimit=cycles, outputLog=log, manualMode=manual, enemyModule=fiveEnemies))