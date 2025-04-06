import logging

import asyncio
from csv import DictReader, DictWriter
from typing import List
from unidecode import unidecode
from operator import attrgetter
from datetime import date
from io import StringIO, BytesIO
from reddevil.filestore.filestore import (
    write_bucket_content,
    read_bucket_content,
    list_bucket_files,
)
from reddevil.core import RdNotFound, RdInternalServerError
from kbsb import ROOT_DIR
from kbsb.core.db import get_mysql
from .md_elo import EloGame, EloPlayer, DbICTrfRecord, TrfRound
from .md_interclubs import DbICSeries
from .helpers import load_icdata

logger = logging.getLogger(__name__)
icdata = None

# TODO eloprocessing.csv needs to be automated !!!

# data model
elodata = {}  # elo data indexed by idbel
belgames1 = []  # divison 1 to 4
belgames2 = []  # division 5
fidegames = []
tlines = {}  # team lines index by team name, list gnr
elopl = {}  # all players index by idbel
cnt = {
    "won": 0,
    "drawn": 0,
    "lost": 0,
    "npart": 0,
    "ngames": 0,
    "nrated": 0,
    "mteams": 0.0,
}
sortedplayers = []  # sorted idbel by elo and name
switch_result = {
    "1-0": "0-1",
    "½-½": "½-½",
    "0-1": "1-0",
    "1-0 FF": "0-1 FF",
    "0-1 FF": "1-0 FF",
    "0-0 FF": "0-0 FF",
}
linefeed = "\x0d\x0a"
b_linefeed = b"\x0d\x0a"


def replaceAt(source, index, replace):
    """
    creates a copy of source str where replace str is filled in at index
    """
    replace = replace or ""
    return source[:index] + replace + source[index + len(replace) :]


result4home = {"1-0": 1.0, "½-½": 0.5, "0-1": 0.0, "1-0 FF": 1.0, "0-1 FF": 0.0}

result4visit = {"1-0": 0.0, "½-½": 0.5, "0-1": 1.0, "1-0 FF": 0.0, "0-1 FF": 1.0}

score4home = {
    "1-0": "1",
    "½-½": "=",
    "0-1": "0",
    "1-0 FF": "+",
    "0-1 FF": "-",
}

score4visit = {
    "1-0": "0",
    "½-½": "=",
    "0-1": "1",
    "1-0 FF": "-",
    "0-1 FF": "+",
}


# eloprocessing views


async def write_eloprocessing():
    """
    Reads elo data from infomaniak server and write it down in a csv file
    in the cloud
    """
    logger.info("writing eloprocessing")
    cnx = get_mysql()
    query = """
        select `esyy_frbekbsbbe`.`signaletique`.`Matricule` AS `idnumber`,
               `esyy_frbekbsbbe`.`signaletique`.`Nom`       AS `last_name`,
               `esyy_frbekbsbbe`.`signaletique`.`Prenom`    AS `first_name`,
               `esyy_frbekbsbbe`.`signaletique`.`MatFIDE`   AS `idfide`,
               `esyy_frbekbsbbe`.`signaletique`.`NatFIDE`   AS `natfide`,
               `esyy_frbekbsbbe`.`signaletique`.`Dnaiss`    AS `birthday`,
               `esyy_frbekbsbbe`.`fide`.`NAME`              AS `fullname`,
               `esyy_frbekbsbbe`.`fide`.`TITLE`             AS `title`,
               `esyy_frbekbsbbe`.`fide`.`ELO`               AS `fiderating`,
               `esyy_frbekbsbbe`.`fide`.`SEX`               AS `gender`,
               `esyy_frbekbsbbe`.`signaletique`.`Sexe`      AS `gender2`,
               `esyy_frbekbsbbe`.`signaletique`.`Club`      AS `idclub`,
               `esyy_frbekbsbbe`.`{elotable}`.`Elo`     AS `belrating`
        from ((`esyy_frbekbsbbe`.`signaletique` left join `esyy_frbekbsbbe`.`fide`
               on ((`esyy_frbekbsbbe`.`signaletique`.`MatFIDE` =
                    `esyy_frbekbsbbe`.`fide`.`ID_NUMBER`))) left join `esyy_frbekbsbbe`.`{elotable}`
              on ((`esyy_frbekbsbbe`.`signaletique`.`Matricule` = `esyy_frbekbsbbe`.`{elotable}`.`Matricule`)))
        where (`esyy_frbekbsbbe`.`signaletique`.`AnneeAffilie` >= 2025);

    """
    try:
        cursor = cnx.cursor(dictionary=True)
        qf = query.format(elotable=get_elotable())
        cursor.execute(qf)
        players = cursor.fetchall()
    except Exception as e:
        logger.exception("Cannot get players from Infomaniak")
        raise RdInternalServerError(description="MySQLError")
    finally:
        cnx.close()
    csvelo = StringIO()
    fields = [
        "idnumber",
        "last_name",
        "first_name",
        "idfide",
        "natfide",
        "birthday",
        "fullname",
        "title",
        "fiderating",
        "gender",
        "gender2",
        "idclub",
        "belrating",
    ]
    writer = DictWriter(csvelo, fields, restval="NULL")
    writer.writeheader()
    for p in players:
        p["first_name"] = unidecode(p["first_name"])
        p["last_name"] = unidecode(p["last_name"])
    writer.writerows(players)
    csvelo.seek(0)
    rd = date.today().strftime("%Y%m%d")
    try:
        write_bucket_content(f"eloprocessing/{rd}.csv", csvelo)
    except Exception as e:
        logger.info("failed to write test file")
        logger.exception(e)
    await asyncio.sleep(0)
    # fname = ROOT_DIR / "kbsb" / "eloprocessing.csv"
    # logger.info(f"writing {fname}")
    # with open(fname, "w") as f:
    #     f.write(csvelo.read())
    logger.info(f"eloprocessing/{rd}.csv written")


def read_eloprocessing(path: str):
    logger.info(f"reading eloprocessing/{path}")
    try:
        elocsv = read_bucket_content(f"eloprocessing/{path}")
    except Exception as e:
        logger.info(f"failed to read eloprocessing/{path} from cloud")
        logger.exception(e)
    with StringIO(elocsv.decode("utf-8")) as ff:
        csvfide = DictReader(ff)
        for fd in csvfide:
            elodata[int(fd["idnumber"])] = fd


async def list_eloprocessing() -> list[str]:
    """
    list the eloprocessing files in the cloud
    """
    try:
        files = list_bucket_files("eloprocessing")
    except Exception as e:
        logger.info("failed to list eloprocessing files")
        logger.exception(e)
    await asyncio.sleep(0)
    return files


# belgian elo


async def get_games_bel(round):
    games1 = []
    games2 = []
    for series in await DbICSeries.find_multiple({"_model": DbICSeries.DOCUMENTTYPE}):
        print(f"processing {series.division} {series.index}")
        for r in series.rounds:
            if r.round == round:
                encounters = r.encounters
                break
        for enc in encounters:
            icclub_home = enc.icclub_home
            icclub_visit = enc.icclub_visit
            if icclub_home == 0 or icclub_visit == 0:
                continue  # skip bye
            for ix, g in enumerate(enc.games):
                idnh = g.idnumber_home
                idnv = g.idnumber_visit
                if not idnh or not idnv:
                    continue
                elodatah = elodata[idnh]
                elodatav = elodata[idnv]
                if ix % 2:
                    idbel_white, idbel_black = idnv, idnh
                    belrating_white, belrating_black = (
                        elodatav["belrating"],
                        elodatah["belrating"],
                    )
                    fullname_white = (
                        f"{elodatav['last_name']}, {elodatav['first_name']}"
                    )
                    fullname_black = (
                        f"{elodatah['last_name']}, {elodatah['first_name']}"
                    )
                    natfide_white, natfide_black = (
                        elodatav["natfide"] or "BEL",
                        elodatah["natfide"] or "BEL",
                    )
                    gender_white, gender_black = (
                        elodatav["gender2"],
                        elodatah["gender2"],
                    )
                    result = switch_result[g.result]
                else:
                    idbel_white, idbel_black = idnh, idnv
                    belrating_white, belrating_black = (
                        elodatah["belrating"],
                        elodatav["belrating"],
                    )
                    fullname_white = (
                        f"{elodatah['last_name']}, {elodatah['first_name']}"
                    )
                    fullname_black = (
                        f"{elodatav['last_name']}, {elodatav['first_name']}"
                    )
                    natfide_white, natfide_black = (
                        elodatah["natfide"],
                        elodatav["natfide"],
                    )
                    gender_white, gender_black = (
                        elodatah["gender"] or elodatah["gender2"],
                        elodatav["gender"] or elodatav["gender2"],
                    )
                    result = g.result
                game = EloGame(
                    belrating_white=belrating_white,
                    fullname_white=fullname_white,
                    gender_white=gender_white,
                    idbel_white=idbel_white,
                    natfide_white=natfide_white,
                    belrating_black=belrating_black,
                    fullname_black=fullname_black,
                    gender_black=gender_black,
                    idbel_black=idbel_black,
                    natfide_black=natfide_black,
                    result=result,
                )
                if series.division == 5:
                    games2.append(game)
                else:
                    games1.append(game)
    return games1, games2


def generate_belgian_report(records: List[EloGame], label: str, round: int):
    """
    writing a list EloGame records in a Belgian ELO file
    """
    hlines = [
        "00A ### Interclubs",
        "00B 1 rondes",
        "00C Envoi des rondes {round} à {round}",
        "00D Envoi par : interclubs@frbe-kbsb-ksb.be",
        "00E Envoi par le club : 998",
        "00F P={npart} R=1 S={icdate:%d/%m/%y} E={icdate:%d/%m/%y} +{won} ={drawn} -{lost}",
        "012 Belgian Interclubs 2024 - 2025 - Round {round}",
        "022 Various locations in Belgian Clubs",
        "032 BEL",
        "042 {icdate}",
        "052 {icdate}",
        "062 {npart}",
        "102 Cornet, Luc",
    ]
    icdate = icdata["rounds"][round]
    ls = " " * 100
    # make line 132
    ls = replaceAt(ls, 0, "132")
    ls = replaceAt(ls, 91, icdate.strftime("%y.%m.%d"))
    hlines.append(ls)
    won = 0
    drawn = 0
    lost = 0
    npart = 0
    ngames = 0
    glines = []
    for g in records:
        if g.result not in ["1-0", "0-1", "½-½"]:
            continue
        # fetch player from signaletique
        whiteline = {
            "n": npart + 1,
            "name": g.fullname_white,
            "idn": g.idbel_white,
            "nat": g.natfide_white or "BEL",
            "elo": g.belrating_white,
            "opponent": npart + 2,
            "color": "w",
        }
        blackline = {
            "n": npart + 2,
            "name": g.fullname_black,
            "idn": g.idbel_black,
            "nat": g.natfide_black or "BEL",
            "elo": g.belrating_black,
            "opponent": npart + 1,
            "color": "b",
        }
        if g.result == "1-0":
            whiteline["rs"] = "1"
            blackline["rs"] = "0"
            whiteline["score"] = 1.0
            blackline["score"] = 0.0
            won += 1
            lost += 1
        if g.result == "½-½":
            drawn += 2
            whiteline["rs"] = "="
            blackline["rs"] = "="
            whiteline["score"] = 0.5
            blackline["score"] = 0.5
        if g.result == "0-1":
            won += 1
            lost += 1
            whiteline["rs"] = "0"
            blackline["rs"] = "1"
            whiteline["score"] = 0.0
            blackline["score"] = 1.0
        glines.append(whiteline)
        glines.append(blackline)
        ngames += 1
        npart += 2
    ff = BytesIO()
    headerdict = {
        "ngames": ngames,
        "npart": npart,
        "won": won,
        "drawn": drawn,
        "lost": lost,
        "round": round,
        "icdate": icdate,
    }
    for l in hlines:
        fl = l.format(**headerdict)
        ff.write(fl.encode("latin-1"))
        ff.write(b_linefeed)
    for l in glines:
        ls = " " * 100
        ls = replaceAt(ls, 0, "001")
        ls = replaceAt(ls, 4, "{:4d}".format(l["n"]))
        ls = replaceAt(ls, 14, "{:32s}".format(l["name"]))
        ls = replaceAt(ls, 48, "{:4d}".format(l["elo"]))
        ls = replaceAt(ls, 63, "{:5d}".format(l["idn"]))
        ls = replaceAt(ls, 81, "{:3.1f}".format(l["score"]))
        ls = replaceAt(ls, 91, "{:4d}".format(l["opponent"]))
        ls = replaceAt(ls, 96, "{:1s}".format(l["color"]))
        ls = replaceAt(ls, 98, "{:1s}".format(l["rs"]))
        ff.write(ls.encode("latin-1"))
        ff.write(b_linefeed)
    ff.seek(0)
    try:
        write_bucket_content(f"icn/ICN_bel_R{round}_{label}.txt", ff)
    except Exception:
        logger.info(f"failed to write belg file icn/ICN_R{round}_{label}.txt")
        logger.exception(e)


async def write_bel_report(round: int, path_elo: str):
    """
    end point to generate a belgian elo report to the cloud storage
    """
    global icdata
    icdata = await load_icdata()
    read_eloprocessing(path_elo)
    games1, games2 = await get_games_bel(round)
    logger.info(f"games {len(games1)} {len(games2)}")
    generate_belgian_report(games1, "part1", round)
    generate_belgian_report(games2, "part2", round)


async def list_bel_reports() -> list[str]:
    """
    list the belgian elo files in the cloud
    """
    try:
        files = list_bucket_files("icn")
    except Exception as e:
        logger.info("failed to list bel reports")
        logger.exception(e)
    await asyncio.sleep(0)
    return [f.split("/")[1] for f in files if f.startswith("icn/ICN_bel")]


async def get_bel_report(path: str) -> str:
    """
    get the content of a belgian elo report
    """
    try:
        report = read_bucket_content(f"icn/{path}")
    except Exception as e:
        logger.info("failed to list bel reports")
        logger.exception(e)
    await asyncio.sleep(0)
    return report


# fide elo


async def get_games_fide(round):
    global fidegames
    fidegames = []
    for series in await DbICSeries.find_multiple({"_model": DbICSeries.DOCUMENTTYPE}):
        for r in series.rounds:
            if r.round == round:
                encounters = r.encounters
                break
        teams = {t.pairingnumber: t for t in series.teams}
        for enc in encounters:
            icclub_home = enc.icclub_home
            icclub_visit = enc.icclub_visit
            if icclub_home == 0 or icclub_visit == 0:
                continue  # skip bye
            for ix, g in enumerate(enc.games):
                idnh = g.idnumber_home
                idnv = g.idnumber_visit
                if not idnh or not idnv:
                    continue
                fideh = elodata.get(idnh, None)
                fidev = elodata.get(idnv, None)
                if not fideh or not fidev:
                    logger.info(
                        "failed fidev or fideh, updateing eloprocessing.csv might help"
                    )
                if ix % 2:
                    idbel_white, idbel_black = idnv, idnh
                    idfide_white, idfide_black = (
                        fidev["idfide"] or "",
                        fideh["idfide"] or "",
                    )
                    fullname_white = fidev["fullname"]
                    if not fullname_white:
                        ln = unidecode(fidev["last_name"])
                        fn = unidecode(fidev["first_name"])
                        fullname_white = f"{ln}, {fn}"
                    fullname_black = fideh["fullname"]
                    if not fullname_black:
                        ln = unidecode(fideh["last_name"])
                        fn = unidecode(fideh["first_name"])
                        fullname_black = f"{ln}, {fn}"
                    fiderating_white, fiderating_black = (
                        fidev["fiderating"] or 0,
                        fideh["fiderating"] or 0,
                    )
                    natfide_white, natfide_black = (
                        fidev["natfide"] or "BEL",
                        fideh["natfide"] or "BEL",
                    )
                    birthday_white, birthday_black = (
                        fidev["birthday"],
                        fideh["birthday"],
                    )
                    title_white, title_black = fidev["title"], fideh["title"]
                    gender_white, gender_black = (
                        fidev["gender"] or fidev["gender2"],
                        fideh["gender"] or fideh["gender2"],
                    )
                    team_white = teams[enc.pairingnr_visit].name
                    team_black = teams[enc.pairingnr_home].name
                    result = switch_result[g.result]
                else:
                    idbel_white, idbel_black = idnh, idnv
                    idfide_white, idfide_black = (
                        fideh.get("idfide", "") or "",
                        fidev.get("idfide", "") or "",
                    )
                    fullname_white = fideh["fullname"]
                    if not fullname_white:
                        ln = unidecode(fideh["last_name"])
                        fn = unidecode(fideh["first_name"])
                        fullname_white = f"{ln}, {fn}"
                    fullname_black = fidev["fullname"]
                    if not fullname_black:
                        ln = unidecode(fidev["last_name"])
                        fn = unidecode(fidev["first_name"])
                        fullname_black = f"{ln}, {fn}"
                    fiderating_white, fiderating_black = (
                        fideh["fiderating"] or 0,
                        fidev["fiderating"] or 0,
                    )
                    natfide_white, natfide_black = fideh["natfide"], fidev["natfide"]
                    birthday_white, birthday_black = (
                        fideh["birthday"],
                        fidev["birthday"],
                    )
                    title_white, title_black = fideh["title"], fidev["title"]
                    gender_white, gender_black = (
                        fideh["gender"] or fideh["gender2"],
                        fidev["gender"] or fidev["gender2"],
                    )
                    team_white = teams[enc.pairingnr_home].name
                    team_black = teams[enc.pairingnr_visit].name
                    result = g.result
                fidegames.append(
                    EloGame(
                        idbel_white=idbel_white,
                        idfide_white=idfide_white,
                        fullname_white=fullname_white,
                        fiderating_white=fiderating_white or 0,
                        natfide_white=natfide_white,
                        birthday_white=birthday_white,
                        title_white=title_white,
                        gender_white=gender_white,
                        team_white=team_white,
                        idbel_black=idbel_black,
                        idfide_black=idfide_black,
                        fullname_black=fullname_black,
                        fiderating_black=fiderating_black,
                        natfide_black=natfide_black,
                        birthday_black=birthday_black,
                        title_black=title_black,
                        gender_black=gender_black,
                        team_black=team_black,
                        result=result,
                    )
                )


def sort_fidegames():
    global sortedplayers
    for g in fidegames:
        wt = tlines.setdefault(unidecode(g.team_white), [])
        bt = tlines.setdefault(unidecode(g.team_black), [])
        wopp = ""
        bopp = ""
        if g.result == "1-0":
            wsc1 = 1.0
            bsc1 = 0.0
            wsc2 = "1"
            bsc2 = "0"
        if g.result == "½-½":
            wsc1 = 0.5
            bsc1 = 0.5
            wsc2 = "="
            bsc2 = "="
        if g.result == "0-1":
            wsc1 = 0.0
            bsc1 = 1.0
            wsc2 = "0"
            bsc2 = "1"
        if g.result == "1-0 FF":
            wsc1 = 1.0
            wsc2 = "+"
            wopp = "0000"
            bsc1 = 0.0
            bsc2 = "-"
            bopp = "0000"
        if g.result == "0-1 FF":
            wsc1 = 0.0
            wsc2 = "-"
            wopp = "0000"
            bsc1 = 1.0
            bsc2 = "+"
            bopp = "0000"
        white = EloPlayer(
            idbel=g.idbel_white,
            idfide=g.idfide_white,
            fullname=g.fullname_white,
            fiderating=g.fiderating_white,
            natfide=g.natfide_white,
            birthday=g.birthday_white,
            title=g.title_white,
            gender=g.gender_white,
            sc1=wsc1,
            sc2=wsc2,
            idopp=g.idbel_black,
            team=unidecode(g.team_white),
            color="w",
        )
        black = EloPlayer(
            idbel=g.idbel_black,
            idfide=g.idfide_black,
            fullname=g.fullname_black,
            fiderating=g.fiderating_black,
            natfide=g.natfide_black,
            birthday=g.birthday_black,
            title=g.title_black,
            gender=g.gender_black,
            sc1=bsc1,
            sc2=bsc2,
            idopp=g.idbel_white,
            team=unidecode(g.team_black),
            color="b",
        )
        elopl[white.idbel] = white
        elopl[black.idbel] = black
    sortedplayers = sorted(
        elopl.keys(), key=lambda x: (-elopl[x].fiderating, elopl[x].fullname)
    )
    logger.info(f"sortedplayers {len(sortedplayers)}")
    for ix, key in enumerate(sortedplayers):
        elopl[key].myix = ix + 1
        elopl[elopl[key].idopp].oppix = ix + 1
        tlines[elopl[key].team].append(ix + 1)


def generate_fide_report(round: int):
    """
    writing a list EloGame records in a Belgian ELO file
    """
    global sortedplayers
    cnt["won"] = 0
    cnt["drawn"] = 0
    cnt["lost"] = 0
    cnt["npart"] = 0
    cnt["ngames"] = 0
    cnt["nrated"] = 0
    cnt["mteams"] = 0.0
    hlines = [
        "012 Belgian Interclubs 2024 - 2025 - Round {round}",
        "022 Various locations in Belgian Clubs",
        "032 BEL",
        "042 {icdate}",
        "052 {icdate}",
        "062 {npart}",
        "072 {nrated}",
        "082 {nteams}",
        "092 Standard Team Round Robin",
        "102 225185 Bailleul, Geert",
        "112 220574 Scaillet, Timothe",
        """122 90'/40 + 30'/end + 30"/move from move 1""",
    ]
    icdate = icdata["rounds"][round]
    print("round date:", icdate, type(icdate))
    ls = " " * 100
    # make line 132
    ls = replaceAt(ls, 0, "132")
    ls = replaceAt(ls, 91, icdate.strftime("%y/%m/%d"))
    hlines.append(ls)
    for g in fidegames:
        if g.fiderating_white > 0:
            cnt["nrated"] += 1
        if g.fiderating_black > 0:
            cnt["nrated"] += 1
        cnt["ngames"] += 1
        cnt["npart"] += 2
    cnt["nteams"] = len(tlines)
    cnt["icdate"] = icdate.strftime("%Y/%m/%d")
    cnt["round"] = round
    f = StringIO()
    for l in hlines:
        fl = l.format(**cnt)
        f.write(fl)
        f.write(linefeed)
    for key in sortedplayers:
        pl = elopl[key]
        ls = " " * 100
        ls = replaceAt(ls, 0, "001")
        ls = replaceAt(ls, 4, "{:4d}".format(pl.myix))
        ls = replaceAt(ls, 9, "{:1s}".format(pl.gender.lower()))
        ls = replaceAt(ls, 10, "{:>3s}".format(pl.title))
        ls = replaceAt(ls, 14, "{:33s}".format(pl.fullname))
        ls = replaceAt(ls, 48, "{:4d}".format(pl.fiderating))
        ls = replaceAt(ls, 53, pl.natfide)
        ls = replaceAt(ls, 57, "{:11d}".format(pl.idfide))
        ls = replaceAt(ls, 69, "{:10s}".format(pl.birthday))
        ls = replaceAt(ls, 80, "{:4.1f}".format(pl.sc1))
        ls = replaceAt(ls, 91, "{:4d}".format(pl.oppix))
        ls = replaceAt(ls, 96, pl.color)
        ls = replaceAt(ls, 98, pl.sc2)
        if "`" in ls:
            ls = ls.replace("`", "'")
        f.write(ls)
        f.write(linefeed)
    sortedkeys = sorted(tlines.keys())
    for tk in sortedkeys:
        ls = " " * 100
        ls = replaceAt(ls, 0, "013")
        ls = replaceAt(ls, 5, tk)
        for ix, pl in enumerate(tlines[tk]):
            ls = replaceAt(ls, 36 + 6 * ix, "{:4d}".format(pl))
        f.write(ls)
        f.write(linefeed)
    f.seek(0)
    try:
        write_bucket_content(f"icn/ICN_fide_R{round}.txt", f)
    except Exception as e:
        logger.info(f"failed to FIDE file icn/ICN_fide_R{round}.txt")
        logger.exception(e)


async def write_fide_report(round: int, path_elo: str):
    """
    endpoint to write the fide elo report to the cloud storage
    """
    global icdata
    icdata = await load_icdata()
    read_eloprocessing(path_elo)
    await get_games_fide(round)
    logger.info(f"info cardoen {elodata[27438]}")
    sort_fidegames()
    generate_fide_report(round)


async def list_fide_reports() -> list[str]:
    """
    list the belgian elo files in the cloud
    """
    try:
        files = list_bucket_files("icn")
    except Exception as e:
        logger.info("failed to list bel reports")
        logger.exception(e)
    await asyncio.sleep(0)
    return [f.split("/")[1] for f in files if f.startswith("icn/ICN_fide")]


async def get_fide_report(path: str) -> str:
    """
    get the content of a fide elo report
    """
    try:
        report = read_bucket_content(f"icn/{path}")
    except Exception as e:
        logger.info("failed to list fide reports")
        logger.exception(e)
    await asyncio.sleep(0)
    return report


# trf processing


async def trf_process_round(round):
    """
    read the results of a round and store them in the trf_report
    """
    read_elo_data(round)
    for series in await DbICSeries.find_multiple({"_model": DbICSeries.DOCUMENTTYPE}):
        for r in series.rounds:
            if r.round == round:
                encounters = r.encounters
                break
        else:
            continue
        for enc in encounters:
            icclub_home = enc.icclub_home
            icclub_visit = enc.icclub_visit
            if icclub_home == 0 or icclub_visit == 0:
                continue  # skip bye
            for ix, g in enumerate(enc.games):
                idnh = g.idnumber_home
                idnv = g.idnumber_visit
                if not idnh or not idnv:
                    continue

                # home player
                try:
                    ph = await DbICTrfRecord.find_single(
                        {"idbel": idnh, "_model": DbICTrfRecord.DOCUMENTTYPE}
                    )
                except RdNotFound:
                    await DbICTrfRecord.add(
                        {"idbel": idnh, "rounds": [], "event": "ic2324"}
                    )
                    ph = await DbICTrfRecord.find_single(
                        {"idbel": idnh, "_model": DbICTrfRecord.DOCUMENTTYPE}
                    )
                for r in ph.rounds:
                    if r.round == round:
                        r.color = "w" if not ix % 2 else "b"
                        r.opponent_idbel = idnv
                        r.result = g.result
                        r.score = result4home[g.result]
                        r.scorestr = score4home[g.result]
                        break
                else:
                    ph.rounds.append(
                        TrfRound(
                            round=round,
                            color="w" if not ix % 2 else "b",
                            opponent_idbel=idnv,
                            result=g.result,
                            score=result4home[g.result],
                            scorestr=score4home[g.result],
                        )
                    )
                await DbICTrfRecord.update(
                    {"idbel": idnh}, ph.model_dump(exclude_none=True)
                )

                # visit player
                try:
                    pv = await DbICTrfRecord.find_single(
                        {"idbel": idnv, "_model": DbICTrfRecord.DOCUMENTTYPE}
                    )
                except RdNotFound:
                    await DbICTrfRecord.add(
                        {"idbel": idnv, "rounds": [], "event": "ic2324"}
                    )
                    pv = await DbICTrfRecord.find_single(
                        {"idbel": idnv, "_model": DbICTrfRecord.DOCUMENTTYPE}
                    )
                for r in pv.rounds:
                    if r.round == round:
                        r.color = "w" if ix % 2 else "b"
                        r.opponent_idbel = idnh
                        r.result = g.result
                        r.score = result4visit[g.result]
                        r.scorestr = score4visit[g.result]
                        break
                else:
                    pv.rounds.append(
                        TrfRound(
                            round=round,
                            color="w" if ix % 2 else "b",
                            opponent_idbel=idnh,
                            result=g.result,
                            score=result4visit[g.result],
                            scorestr=score4visit[g.result],
                        )
                    )
                await DbICTrfRecord.update(
                    {"idbel": idnv}, pv.model_dump(exclude_none=True)
                )


async def trf_process_playerdetails(round: int):
    """
    read the trf_report and fill in all fields but the fiderating
    """
    read_elo_data(round)
    for trf in await DbICTrfRecord.find_multiple(
        {"_model": DbICTrfRecord.DOCUMENTTYPE}
    ):
        details = elodata.get(trf.idbel)
        if not details:
            logger.error(f"no elodata for {trf.idbel}")
            continue
        upd = {
            "birthdate": details["birthday"],
            "gender": details["gender"],
            "chesstitle": details["title"],
            "fullname": details["fullname"],
            "federation": details["natfide"],
            "idfide": details["idfide"],
            "fiderating": details["fiderating"],
            "idclub": details["idclub"],
        }
        await DbICTrfRecord.update({"idbel": trf.idbel}, upd)


async def trf_process_fideratings(round: int):
    """
    read the trf_report and fill in all fields but the fiderating
    """
    players = {}
    read_elo_data(round)
    for trf in await DbICTrfRecord.find_multiple(
        {"_model": DbICTrfRecord.DOCUMENTTYPE}
    ):
        players[str(trf.idfide)] = trf  # force str index
    logger.info(f"trf records read # {len(players)}")
    with open(ROOT_DIR / "shared" / "data" / "standard_sep23frl.txt") as ff:
        ff.readline()  # skip first line
        i = 1
        while line := ff.readline():
            id = line[0:11].strip()  # force str
            if id in players:
                try:
                    pl = players[id]
                    rating = int(line[113:118].strip())
                except Exception:
                    logger.error(f"failed to read rating {line[113:118]}")
                    continue
                logger.info(f"update rating for {id} to {rating}")
                try:
                    await DbICTrfRecord.update(
                        {"idbel": pl.idbel},
                        {
                            "fiderating": rating,
                            "idfide": str(id),
                        },
                    )
                except RdNotFound:
                    logger.error(f"Could not find fideid {id} in TrfRecord")
                    logger.info(f"pl {pl}")
            i += 1
    logger.info(f"processed {i} lines")


async def trf_process_sort():
    """
    Perform the following steps
    - order players by rating, fullname
    - assign player_ix and opponent_ix
    """

    players_dict = {}
    players_list = []
    for trf in await DbICTrfRecord.find_multiple(
        {"_model": DbICTrfRecord.DOCUMENTTYPE}
    ):
        if not trf.fullname:
            trf.fullname = ""
        if not trf.fiderating:
            trf.fiderating = 0
        try:
            trf.fiderating = int(trf.fiderating)
        except ValueError:
            logger.error(f"cannot make fiderating {trf.fiderating} an int")
            raise ValueError
        players_dict[trf.idbel] = trf
        players_list.append(trf)
    players_list.sort(key=attrgetter("fullname"))
    players_list.sort(key=attrgetter("fiderating"), reverse=True)
    for ix, trf in enumerate(players_list):
        trf.player_ix = ix + 1
    for trf in players_list:
        points = 0.0
        for r in trf.rounds:
            r.opponent_ix = players_dict[r.opponent_idbel].player_ix
            points += r.score
        trf.points = points
        upd = trf.model_dump(exclude_none=True)
        upd.pop("idbel", None)
        upd.pop("id", None)
        await DbICTrfRecord.update({"idbel": trf.idbel}, upd)


async def trf_generate(round: int = 0) -> None:
    """
    generate a TRF file, round is specified only for that round
    """
    players_dict = {}
    f = StringIO()
    for trf in await DbICTrfRecord.find_multiple(
        {"_model": DbICTrfRecord.DOCUMENTTYPE}
    ):
        players_dict[trf.player_ix] = trf

    for k in range(len(players_dict)):
        pl = players_dict[k + 1]
        if not pl:
            logger.info(f"Cannot access player at index {k + 1}")
        if not pl.fullname:
            pl.fullname = f"*** {pl.idbel} ***"
        ls = " " * (90 + 10 * 11)
        ls = replaceAt(ls, 0, "001")
        ls = replaceAt(ls, 4, "{:4d}".format(pl.player_ix))
        ls = replaceAt(ls, 9, "{:1s}".format(pl.gender or "X"))
        ls = replaceAt(ls, 10, "{:>3s}".format(pl.chesstitle or ""))
        ls = replaceAt(ls, 14, "{:33s}".format(pl.fullname))
        ls = replaceAt(ls, 48, "{:4d}".format(pl.fiderating or 0))
        ls = replaceAt(ls, 53, pl.federation)
        ls = replaceAt(ls, 57, "{:11d}".format(pl.idfide or 0))
        ls = replaceAt(ls, 69, "{:10s}".format(pl.birthdate or ""))
        ls = replaceAt(ls, 80, "{:4.1f}".format(pl.points or 0.0))
        for r in pl.rounds:
            ls = replaceAt(ls, 81 + r.round * 10, "{:4d}".format(r.opponent_ix))
            ls = replaceAt(ls, 86 + r.round * 10, r.color)
            ls = replaceAt(ls, 88 + r.round * 10, r.scorestr)
        if "`" in ls:
            ls = ls.replace("`", "'")
        f.write(ls)
        f.write(linefeed)
    with open("icn_trf.txt", "w") as trff:
        trff.write(f.getvalue())


# helper


def get_elotable() -> str:
    today = date.today()
    elomonth = (today.month - 1) // 3 * 3 + 1
    return f"p_player{today.year}{elomonth:02d}"
