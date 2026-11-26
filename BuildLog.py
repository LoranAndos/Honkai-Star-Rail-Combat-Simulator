import logging

from Attributes import *


def _fmt(v) -> str:
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


def _line(kind: str, **fields) -> str:
    return f"BUILD   > {kind} | " + " | ".join(f"{k}={_fmt(v)}" for k, v in fields.items())


def _buffSum(buffList, role, statType, flatOnly=None) -> float:
    """Sum of the buffs of `statType` that target `role` and apply to ALL attack types."""
    total = 0.0
    for b in buffList:
        if b.target == role and b.buffType == statType and AtkType.ALL in b.atkType:
            total += b.getBuffVal()
    return total


def _mainName(stat) -> str:
    return stat.value if hasattr(stat, "value") else str(stat)


def logBuildSnapshot(playerTeam, teamBuffs, cycleLimit, avLimit, startingSP, maxSP, numEnemies) -> None:
    """Write the BUILD section. Call once, after equipment and initial buffs have been applied."""
    logging.critical("")
    logging.critical("==========BUILD SNAPSHOT==========")
    logging.critical(_line("CONTEXT", cycles=cycleLimit, avLimit=avLimit, startSP=startingSP, maxSP=maxSP,
                           enemies=numEnemies))

    for idx, char in enumerate(playerTeam):
        lc = getattr(char, "lightcone", None)
        rs = getattr(char, "relicStats", None)
        relic2 = getattr(char, "relic2", None)
        logging.critical(_line(
            "CHAR", idx=idx, name=char.name, eidolon=char.eidolon, element=char.element.name, path=char.path.name,
            role=char.role.name, pos=getattr(char, "pos", idx), scaling=getattr(char.scaling, "name", char.scaling),
            rotation=",".join(getattr(char, "rotation", []) or []), maxEnergy=char.maxEnergy,
            startEnergy=char.currEnergy))
        logging.critical(_line(
            "GEAR", idx=idx, lightcone=lc if lc is not None else "", relic1=getattr(char, "relic1", "") or "",
            relic2=relic2 if relic2 is not None else "", planar=getattr(char, "planar", "") or ""))
        if rs is None or lc is None:
            continue  # memosprites / summons-as-characters have no relic build

        logging.critical(_line("MAINS", idx=idx, body=_mainName(rs.body), boots=_mainName(rs.boots),
                               sphere=_mainName(rs.sphere), rope=_mainName(rs.rope)))
        logging.critical(_line(
            "ROLLS", idx=idx, spd=rs.spd, hpFlat=rs.hpFlat, atkFlat=rs.atkFlat, defFlat=rs.defFlat,
            hpPct=rs.hpPercent, atkPct=rs.atkPercent, defPct=rs.defPercent, be=rs.be, ehr=rs.ehr, ers=rs.ers,
            cr=rs.cr, cd=rs.cd, total=rs.totalSubRolls()))

        role = char.role

        def stat(name, final, relic, buffs, base=""):
            logging.critical(_line("STAT", idx=idx, stat=name, final=final, relic=relic, buffs=buffs, base=base))

        # HP / ATK / DEF: (char base + lightcone base) * (1 + relic% + buff%) + relic flat + buff flat
        for name, charBase, lcBase, pctType, flatType, relicPct, relicFlat in (
            ("HP", char.baseHP, lc.baseHP, StatTypes.HP_PERCENT, StatTypes.HP, rs.getHPPercent(), rs.getHPFlat()),
            ("ATK", char.baseATK, lc.baseATK, StatTypes.ATK_PERCENT, StatTypes.ATK, rs.getATKPercent(), rs.getATKFlat()),
            ("DEF", char.baseDEF, lc.baseDEF, StatTypes.DEF_PERCENT, StatTypes.DEF, rs.getDEFPercent(), rs.getDEFFlat()),
        ):
            base = charBase + lcBase
            buffPct = _buffSum(teamBuffs, role, pctType)
            buffFlat = _buffSum(teamBuffs, role, flatType)
            relicOnly = base * (1 + relicPct) + relicFlat
            final = base * (1 + relicPct + buffPct) + relicFlat + buffFlat
            stat(name, final, relicOnly - base, final - relicOnly, base)

        # SPD: base * (1 + SPD%) + relic flat SPD + flat SPD buffs
        spdPct = _buffSum(teamBuffs, role, StatTypes.SPD_PERCENT)
        spdFlat = _buffSum(teamBuffs, role, StatTypes.SPD)
        spdRelic = rs.getSPD()
        stat("SPD", char.baseSPD * (1 + spdPct) + spdRelic + spdFlat, spdRelic,
             char.baseSPD * spdPct + spdFlat, char.baseSPD)

        # Percent-type stats: relic (incl. the game's base value) + buffs
        for name, relicVal, statType, baseVal in (
            ("CR", rs.getCR(), StatTypes.CR_PERCENT, 0.05),
            ("CD", rs.getCD(), StatTypes.CD_PERCENT, 0.5),
            ("DMG", rs.getDMG(), StatTypes.DMG_PERCENT, 0.0),
            ("ERR", rs.getERR(), StatTypes.ERR_PERCENT, 0.0),
            ("BE", rs.getBE(), StatTypes.BE_PERCENT, 0.0),
            ("EHR", rs.getEHR(), StatTypes.EHR_PERCENT, 0.0),
            ("ERS", rs.getERS(), StatTypes.ERS_PERCENT, 0.0),
            ("HEAL", rs.getOGH(), StatTypes.OGH_PERCENT, 0.0),
        ):
            buffVal = _buffSum(teamBuffs, role, statType)
            stat(name, relicVal + buffVal, relicVal - baseVal, buffVal, baseVal)

        elaBuff = _buffSum(teamBuffs, role, StatTypes.ELA)
        stat("ELA", elaBuff, 0.0, elaBuff, 0.0)
    logging.critical("==========END OF BUILD SNAPSHOT==========")