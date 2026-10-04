import asyncio
import logging
from csv import DictReader
from datetime import date, datetime
from io import BytesIO, StringIO
from operator import attrgetter

import httpx
from reddevil.core import RdNotFound, get_secret, get_setting
from reddevil.filestore.filestore import (
    list_bucket_files,
    read_bucket_content,
    write_bucket_content,
)

from .helpers import load_icdata
from .md_elo import DbICTrfRecord, EloGame, EloPlayer, TrfRound
from .md_interclubs import DbICSeries

logger = logging.getLogger(__name__)
icdata = None


# data model
elodata = {}  # elo data indexed by idbel
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
    Reads csv file from from zerotwo cloud server and write it in google cloud
    """
    secret = get_secret("eloserver")
    tz_brussels = get_setting("TZ_BRUSSELS")
    url_eloserver_csv = get_setting("ELO_SERVER_CSV")
    logger.info(f"Fetching ELO data from server {url_eloserver_csv}")
    async with httpx.AsyncClient() as client:
        response = await client.get(url_eloserver_csv, headers={"x-api-key": secret})
        if response.status_code != 200:
            raise RuntimeError(
                f"Failed to fetch ELO data, status code: {response.status_code}"
            )
        response_csv = await client.get(
            url_eloserver_csv, headers={"x-api-key": secret}
        )
        if response_csv.status_code != 200:
            raise RuntimeError(
                f"Failed to fetch ELO CSV data, status code: {response_csv.status_code}"
            )
    csvBytes = BytesIO(initial_bytes=response.text.encode("utf-8"))
    rd = datetime.now(tz=tz_brussels).date().strftime("%Y%m%d")
    try:
        write_bucket_content(f"eloprocessing/{rd}.csv", csvBytes)
    except Exception as e:
        logger.info("failed to write eloprocessing file")
        logger.exception(e)
    finally:
        csvBytes.close()


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
            idbel = int(fd["national_id"])
            elodata[idbel] = fd


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
                if g.result not in switch_result:
                    continue
                fideh = elodata.get(idnh, None)
                fidev = elodata.get(idnv, None)
                if not fideh or not fidev:
                    logger.info(
                        "failed fidev or fideh, updateing eloprocessing.csv might help"
                    )
                assert fideh and fidev
                if ix % 2:
                    idbel_white, idbel_black = idnv, idnh
                    idfide_white, idfide_black = (
                        fidev["fide_id"] or "",
                        fideh["fide_id"] or "",
                    )
                    fullname_white = f"{fidev['first_name']}, {fidev['last_name']}"
                    fullname_black = f"{fideh['first_name']}, {fideh['last_name']}"
                    fiderating_white, fiderating_black = (
                        fidev["fiderating"] or 0,
                        fideh["fiderating"] or 0,
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
                    fullname_white = f"{fideh['last_name']}, {fideh['first_name']}"
                    fullname_black = f"{fidev['last_name']}, {fidev['first_name']}"
                    fiderating_white, fiderating_black = (
                        fideh["fiderating"] or 0,
                        fidev["fiderating"] or 0,
                    )
                    natfide_white, natfide_black = (
                        fideh.get("natfide", "BEL"),
                        fidev.get("natfide", "BEL"),
                    )
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
        tlines.setdefault((g.team_white), [])
        tlines.setdefault((g.team_black), [])
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
            bsc1 = 0.0
            bsc2 = "-"
        if g.result == "0-1 FF":
            wsc1 = 0.0
            wsc2 = "-"
            bsc1 = 1.0
            bsc2 = "+"
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
            team=(g.team_white),
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
            team=(g.team_black),
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
        "012 Belgian Interclubs 2026 - 2027 - Round {round}",
        "022 Various locations in Belgian Clubs",
        "032 BEL",
        "042 {icdate}",
        "052 {icdate}",
        "062 {npart}",
        "072 {nrated}",
        "082 {nteams}",
        "092 Standard Team Round Robin",
        "102 225185 Cornet, Luc",
        """122 90'/40 + 30'/end + 30"/move from move 1""",
    ]
    icdate = icdata["rounds"][round]  # type: ignore
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
    for ln in hlines:
        fl = ln.format(**cnt)
        f.write(fl)
        f.write(linefeed)
    for key in sortedplayers:
        pl = elopl[key]
        ls = " " * 100
        ls = replaceAt(ls, 0, "001")
        ls = replaceAt(ls, 4, f"{pl.myix:4d}")
        ls = replaceAt(ls, 9, f"{pl.gender.lower():1s}")
        ls = replaceAt(ls, 10, f"{pl.title:>3s}")
        ls = replaceAt(ls, 14, f"{pl.fullname:33s}")
        ls = replaceAt(ls, 48, f"{pl.fiderating:4d}")
        ls = replaceAt(ls, 53, pl.natfide)
        ls = replaceAt(ls, 57, f"{pl.idfide:11d}")
        ls = replaceAt(ls, 69, f"{pl.birthday:10s}")
        ls = replaceAt(ls, 80, f"{pl.sc1:4.1f}")
        ls = replaceAt(ls, 91, f"{pl.oppix:4d}")
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
            ls = replaceAt(ls, 36 + 6 * ix, f"{pl:4d}")
        f.write(ls)
        f.write(linefeed)
    f.seek(0)
    repBytes = BytesIO(initial_bytes=f.read().encode("utf-8"))
    try:
        write_bucket_content(f"icn/ICN_fide_R{round}.txt", repBytes)
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

trfdata_2425 = {"startround": "20240930.csv", "endround": "20250525.csv"}
trfdata_2526 = {"startround": "20250929.csv", "endround": "20260428.csv"}
trfdata_2627 = {"startround": "20260930.csv", "endround": "20270524.csv"}


async def trf_process_round(round):
    """
    read the results of a round and store them in the trf_report
    """
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
                if not g.result:
                    continue
                # home player
                try:
                    ph = await DbICTrfRecord.find_single(
                        {"idbel": idnh, "_model": DbICTrfRecord.DOCUMENTTYPE}
                    )
                except RdNotFound:
                    await DbICTrfRecord.add(
                        {"idbel": idnh, "rounds": [], "event": "ic2526"}
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
                        {"idbel": idnv, "rounds": [], "event": "ic2526"}
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


async def trf_process_playerdetails1():
    """
    read the trf_report and fill in all fields but the fiderating
    """
    for trf in await DbICTrfRecord.find_multiple(
        {"_model": DbICTrfRecord.DOCUMENTTYPE}
    ):
        details = elodata.get(trf.idbel)
        if not details:
            logger.info(f"no elodata for {trf.idbel}")
            continue
        upd = {
            "birthdate": details["birthday"],
            "gender": details["gender"],
            "chesstitle": details["title"],
            "fullname": details["fullname"],
            "federation": details["natfide"],
            "idfide": details["idfide"],
            "fiderating": 0,
            "idclub": details["idclub"],
        }
        await DbICTrfRecord.update({"idbel": trf.idbel}, upd)


async def trf_process_playerdetails2():
    """
    read the trf_report
    if the record is filled in, update the record with the fiderating
    else fill in the record with the elodata
    """
    for trf in await DbICTrfRecord.find_multiple(
        {"_model": DbICTrfRecord.DOCUMENTTYPE}
    ):
        details = elodata.get(trf.idbel)
        if not details:
            logger.error(f"no elodata for {trf.idbel}")
            break
        upd = {"fiderating": details["fiderating"]}
        if not trf.fullname or trf.fullname == "":
            upd = upd | {
                "birthdate": details["birthday"],
                "gender": details["gender"],
                "chesstitle": details["title"],
                "fullname": details["fullname"],
                "federation": details["natfide"],
                "idfide": details["idfide"],
                "idclub": details["idclub"],
            }
        await DbICTrfRecord.update({"idbel": trf.idbel}, upd)


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


async def trf_generate() -> None:
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
        ls = replaceAt(ls, 4, f"{pl.player_ix:4d}")
        ls = replaceAt(ls, 9, "{:1s}".format(pl.gender or "X"))
        ls = replaceAt(ls, 10, "{:>3s}".format(pl.chesstitle or ""))
        ls = replaceAt(ls, 14, f"{pl.fullname:33s}")
        ls = replaceAt(ls, 48, f"{pl.fiderating or 0:4d}")
        ls = replaceAt(ls, 53, pl.federation)
        ls = replaceAt(ls, 57, f"{pl.idfide or 0:11d}")
        ls = replaceAt(ls, 69, "{:10s}".format(pl.birthdate or ""))
        ls = replaceAt(ls, 80, f"{pl.points or 0.0:4.1f}")
        for r in pl.rounds:
            ls = replaceAt(ls, 81 + r.round * 10, f"{r.opponent_ix:4d}")
            ls = replaceAt(ls, 86 + r.round * 10, r.color)
            ls = replaceAt(ls, 88 + r.round * 10, r.scorestr)
        if "`" in ls:
            ls = ls.replace("`", "'")
        f.write(ls)
        f.write(linefeed)
    with open("icn_trf.txt", "w") as trff:
        trff.write(f.getvalue())


async def trf_fide_ratings():
    """
    update the fide ratings in the trf report
    """
    for trf in await DbICTrfRecord.find_multiple(
        {"_model": DbICTrfRecord.DOCUMENTTYPE}
    ):
        if not trf.idfide:
            continue
        try:
            fide = elodata[trf.idbel]
            trf.fiderating = fide["fiderating"]
        except KeyError:
            logger.error(f"no elodata for {trf.idbel}")
            continue
        await DbICTrfRecord.update({"idbel": trf.idbel}, {"fiderating": trf.fiderating})


async def trf_report_phase1():
    """
    generate the trf report
    """
    logger.info("trf report phase 1")
    read_eloprocessing(trfdata_2526["startround"])
    for round in range(1, 12):
        logger.info(f"processing round {round}")
        await trf_process_round(round)
    await trf_process_playerdetails1()


async def trf_report_phase2():
    """
    sort the players and write the report
    """
    logger.info("trf report phase 2")
    read_eloprocessing(trfdata_2526["endround"])
    await trf_process_playerdetails2()
    await trf_process_sort()
    await trf_generate()


# helpers


def get_elotable() -> str:
    today = date.today()
    elomonth = (today.month - 1) // 3 * 3 + 1
    return f"p_player{today.year}{elomonth:02d}"
