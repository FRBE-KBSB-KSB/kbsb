import asyncio
import logging
from csv import DictReader
from datetime import date, datetime
from io import BytesIO, StringIO
from typing import Any

import httpx
from reddevil.core import get_secret, get_setting
from reddevil.filestore.filestore import (
    list_bucket_files,
    read_bucket_content,
    write_bucket_content,
)

from .helpers import load_icdata
from .md_elo import EloGame, EloPlayer

#  from .md_elo import DbICTrfRecord, TrfRound
from .md_interclubs import DbICSeries, ICSeriesDB

logger = logging.getLogger(__name__)
icdata = None


# data model
fidegames = []
tlines: dict[str, Any] = {}  # team lines index by team name, list gnr
eloall = {}  # all players index by idbel
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


def _replaceAt(source, index, replace):
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
        raise RuntimeError(f"failed to read eloprocessing/{path} from cloud") from e
    with StringIO(elocsv.decode("utf-8")) as ff:
        csvfide = DictReader(ff)
        for fd in csvfide:
            idbel = int(fd["national_id"])
            idfide = int(fd.get("fide_id") or 0)
            fiderating = int(fd.get("standard") or 0)
            last_name = fd["last_name"]
            try:
                first_name = fd["first_name"]
            except KeyError:
                logger.info(f"fd: {fd}")
                raise RuntimeError(f"failed to read first_name for idbel {idbel}")
            eloall[idbel] = EloPlayer(
                birthyear=fd.get("birth_year", "0"),
                fiderating=fiderating,
                fullname=f"{last_name}, {first_name}",
                gender=fd.get("gender", "m"),
                idbel=idbel,
                idfide=idfide,
                nationality=fd.get("fidefederation", "BEL"),
                title=fd.get("title", ""),
            )


async def list_eloprocessing() -> list[str]:
    """
    list the eloprocessing files in the cloud
    """
    try:
        files = list_bucket_files("eloprocessing")
    except Exception as e:
        logger.info("failed to list eloprocessing files")
        logger.exception(e)
        raise RuntimeError("failed to list eloprocessing files") from e
    await asyncio.sleep(0)
    return files


# fide elo


async def games_fiderating(round):
    # assemble all games of the round in a list of EloGame records
    global fidegames, elopl
    fidegames = []
    elopl = {}
    for series in await DbICSeries.find_multiple({"_model": ICSeriesDB}):
        assert isinstance(series, ICSeriesDB)
        for r in series.rounds:
            if r.round == round:
                encounters = r.encounters
                break
        else:
            raise RuntimeError(
                f"round {round} not found in series {series.division}{series.index}"
            )
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
                playerhome = elopl[idnh] = eloall[idnh]
                playervisit = elopl[idnv] = eloall[idnv]
                if not playerhome or not playervisit:
                    logger.info(
                        "failed playervisit or playerhome, updateing eloprocessing.csv might help"
                    )
                    raise RuntimeError(
                        f"failed playervisit or playerhome for {idnh} or {idnv}"
                    )
                playerhome.team = teams[enc.pairingnr_home].name
                playervisit.team = teams[enc.pairingnr_visit].name
                playerhome.idopp = playervisit.idbel
                playervisit.idopp = playerhome.idbel
                if ix % 2:  # counting from 0, so odd index means home player is black
                    playerhome.color = "b"
                    playervisit.color = "w"
                    eg = EloGame(
                        player_white=playervisit,
                        player_black=playerhome,
                        result=switch_result[g.result],
                    )
                else:
                    playerhome.color = "w"
                    playervisit.color = "b"
                    eg = EloGame(
                        player_white=playerhome,
                        player_black=playervisit,
                        result=g.result,
                    )
                fidegames.append(eg)


def sort_fidegames():
    global sortedplayers
    for g in fidegames:
        tlines.setdefault((g.player_white.team), [])
        tlines.setdefault((g.player_black.team), [])
        if g.result == "1-0":
            elopl[g.player_white.idbel].sc1 = 1.0
            elopl[g.player_black.idbel].sc1 = 0.0
            elopl[g.player_white.idbel].sc2 = "1"
            elopl[g.player_black.idbel].sc2 = "0"
        if g.result == "½-½":
            elopl[g.player_white.idbel].sc1 = 0.5
            elopl[g.player_black.idbel].sc1 = 0.5
            elopl[g.player_white.idbel].sc2 = "="
            elopl[g.player_black.idbel].sc2 = "="
        if g.result == "0-1":
            elopl[g.player_white.idbel].sc1 = 0.0
            elopl[g.player_black.idbel].sc1 = 1.0
            elopl[g.player_white.idbel].sc2 = "0"
            elopl[g.player_black.idbel].sc2 = "1"
        if g.result == "1-0 FF":
            elopl[g.player_white.idbel].sc1 = 1.0
            elopl[g.player_white.idbel].sc2 = "+"
            elopl[g.player_black.idbel].sc1 = 0.0
            elopl[g.player_black.idbel].sc2 = "-"
        if g.result == "0-1 FF":
            elopl[g.player_white.idbel].sc1 = 0.0
            elopl[g.player_white.idbel].sc2 = "-"
            elopl[g.player_black.idbel].sc1 = 1.0
            elopl[g.player_black.idbel].sc2 = "+"
    sortedplayers = sorted(
        elopl.keys(), key=lambda x: (-elopl[x].fiderating, elopl[x].fullname)
    )
    logger.info(f"sortedplayers {len(sortedplayers)}")
    for ix, key in enumerate(sortedplayers):
        pl = elopl[key]
        pl.myix = ix + 1
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
    icdate = icdata["rounds11"][round]  # type: ignore
    print("round date:", icdate, type(icdate))
    ls = " " * 100
    # make line 132
    ls = _replaceAt(ls, 0, "132")
    ls = _replaceAt(ls, 91, icdate.strftime("%y/%m/%d"))
    hlines.append(ls)
    for g in fidegames:
        if g.player_white.fiderating > 0:
            cnt["nrated"] += 1
        if g.player_black.fiderating > 0:
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
        ls = _replaceAt(ls, 0, "001")
        ls = _replaceAt(ls, 4, f"{pl.myix:4d}")
        ls = _replaceAt(ls, 9, f"{pl.gender.lower():1s}")
        ls = _replaceAt(ls, 10, f"{pl.title:>3s}")
        ls = _replaceAt(ls, 14, f"{pl.fullname:33s}")
        ls = _replaceAt(ls, 48, f"{pl.fiderating:4d}")
        ls = _replaceAt(ls, 53, pl.nationality)
        ls = _replaceAt(ls, 57, f"{pl.idfide:11d}")
        ls = _replaceAt(ls, 69, f"{pl.birthyear:4s}/01/01")
        ls = _replaceAt(ls, 80, f"{pl.sc1:4.1f}")
        ls = _replaceAt(ls, 91, f"{pl.oppix:4d}")
        ls = _replaceAt(ls, 96, pl.color)
        ls = _replaceAt(ls, 98, pl.sc2)
        if "`" in ls:
            ls = ls.replace("`", "'")
        f.write(ls)
        f.write(linefeed)
    sortedkeys = sorted(tlines.keys())
    for tk in sortedkeys:
        ls = " " * 100
        ls = _replaceAt(ls, 0, "013")
        ls = _replaceAt(ls, 5, tk)
        for ix, pl in enumerate(tlines[tk]):
            ls = _replaceAt(ls, 36 + 6 * ix, f"{pl:4d}")
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
    await games_fiderating(round)
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

# trfdata_2425 = {"startround": "20240930.csv", "endround": "20250525.csv"}
# trfdata_2526 = {"startround": "20250929.csv", "endround": "20260428.csv"}
# trfdata_2627 = {"startround": "20260930.csv", "endround": "20270524.csv"}


# async def trf_process_round(round):
#     """
#     read the results of a round and store them in the trf_report
#     """
#     global fidegames
#     fidegames = []
#     for series in await DbICSeries.find_multiple({"_model": DbICSeries.DOCUMENTTYPE}):
#         for r in series.rounds:
#             if r.round == round:
#                 encounters = r.encounters
#                 break
#         else:
#             continue
#         for enc in encounters:
#             icclub_home = enc.icclub_home
#             icclub_visit = enc.icclub_visit
#             if icclub_home == 0 or icclub_visit == 0:
#                 continue  # skip bye
#             for ix, g in enumerate(enc.games):
#                 idnh = g.idnumber_home
#                 idnv = g.idnumber_visit
#                 if not idnh or not idnv:
#                     continue
#                 if not g.result:
#                     continue
#                 # home player
#                 try:
#                     ph = await DbICTrfRecord.find_single(
#                         {"idbel": idnh, "_model": DbICTrfRecord.DOCUMENTTYPE}
#                     )
#                 except RdNotFound:
#                     await DbICTrfRecord.add(
#                         {"idbel": idnh, "rounds": [], "event": "ic2526"}
#                     )
#                     ph = await DbICTrfRecord.find_single(
#                         {"idbel": idnh, "_model": DbICTrfRecord.DOCUMENTTYPE}
#                     )
#                 for r in ph.rounds:
#                     if r.round == round:
#                         r.color = "w" if not ix % 2 else "b"
#                         r.opponent_idbel = idnv
#                         r.result = g.result
#                         r.score = result4home[g.result]
#                         r.scorestr = score4home[g.result]
#                         break
#                 else:
#                     ph.rounds.append(
#                         TrfRound(
#                             round=round,
#                             color="w" if not ix % 2 else "b",
#                             opponent_idbel=idnv,
#                             result=g.result,
#                             score=result4home[g.result],
#                             scorestr=score4home[g.result],
#                         )
#                     )
#                 await DbICTrfRecord.update(
#                     {"idbel": idnh}, ph.model_dump(exclude_none=True)
#                 )

#                 # visit player
#                 try:
#                     pv = await DbICTrfRecord.find_single(
#                         {"idbel": idnv, "_model": DbICTrfRecord.DOCUMENTTYPE}
#                     )
#                 except RdNotFound:
#                     await DbICTrfRecord.add(
#                         {"idbel": idnv, "rounds": [], "event": "ic2526"}
#                     )
#                     pv = await DbICTrfRecord.find_single(
#                         {"idbel": idnv, "_model": DbICTrfRecord.DOCUMENTTYPE}
#                     )
#                 for r in pv.rounds:
#                     if r.round == round:
#                         r.color = "w" if ix % 2 else "b"
#                         r.opponent_idbel = idnh
#                         r.result = g.result
#                         r.score = result4visit[g.result]
#                         r.scorestr = score4visit[g.result]
#                         break
#                 else:
#                     pv.rounds.append(
#                         TrfRound(
#                             round=round,
#                             color="w" if ix % 2 else "b",
#                             opponent_idbel=idnh,
#                             result=g.result,
#                             score=result4visit[g.result],
#                             scorestr=score4visit[g.result],
#                         )
#                     )
#                 await DbICTrfRecord.update(
#                     {"idbel": idnv}, pv.model_dump(exclude_none=True)
#                 )


# async def trf_process_playerdetails1():
#     """
#     read the trf_report and fill in all fields but the fiderating
#     """
#     for trf in await DbICTrfRecord.find_multiple(
#         {"_model": DbICTrfRecord.DOCUMENTTYPE}
#     ):
#         details = elodata.get(trf.idbel)
#         if not details:
#             logger.info(f"no elodata for {trf.idbel}")
#             continue
#         upd = {
#             "birthdate": details["birthday"],
#             "gender": details["gender"],
#             "chesstitle": details["title"],
#             "fullname": details["fullname"],
#             "federation": details["natfide"],
#             "idfide": details["idfide"],
#             "fiderating": 0,
#             "idclub": details["idclub"],
#         }
#         await DbICTrfRecord.update({"idbel": trf.idbel}, upd)


# async def trf_process_playerdetails2():
#     """
#     read the trf_report
#     if the record is filled in, update the record with the fiderating
#     else fill in the record with the elodata
#     """
#     for trf in await DbICTrfRecord.find_multiple(
#         {"_model": DbICTrfRecord.DOCUMENTTYPE}
#     ):
#         details = elodata.get(trf.idbel)
#         if not details:
#             logger.error(f"no elodata for {trf.idbel}")
#             break
#         upd = {"fiderating": details["fiderating"]}
#         if not trf.fullname or trf.fullname == "":
#             upd = upd | {
#                 "birthdate": details["birthday"],
#                 "gender": details["gender"],
#                 "chesstitle": details["title"],
#                 "fullname": details["fullname"],
#                 "federation": details["natfide"],
#                 "idfide": details["idfide"],
#                 "idclub": details["idclub"],
#             }
#         await DbICTrfRecord.update({"idbel": trf.idbel}, upd)


# async def trf_process_sort():
#     """
#     Perform the following steps
#     - order players by rating, fullname
#     - assign player_ix and opponent_ix
#     """

#     players_dict = {}
#     players_list = []
#     for trf in await DbICTrfRecord.find_multiple(
#         {"_model": DbICTrfRecord.DOCUMENTTYPE}
#     ):
#         if not trf.fullname:
#             trf.fullname = ""
#         if not trf.fiderating:
#             trf.fiderating = 0
#         try:
#             trf.fiderating = int(trf.fiderating)
#         except ValueError:
#             logger.error(f"cannot make fiderating {trf.fiderating} an int")
#             raise ValueError
#         players_dict[trf.idbel] = trf
#         players_list.append(trf)
#     players_list.sort(key=attrgetter("fullname"))
#     players_list.sort(key=attrgetter("fiderating"), reverse=True)
#     for ix, trf in enumerate(players_list):
#         trf.player_ix = ix + 1
#     for trf in players_list:
#         points = 0.0
#         for r in trf.rounds:
#             r.opponent_ix = players_dict[r.opponent_idbel].player_ix
#             points += r.score
#         trf.points = points
#         upd = trf.model_dump(exclude_none=True)
#         upd.pop("idbel", None)
#         upd.pop("id", None)
#         await DbICTrfRecord.update({"idbel": trf.idbel}, upd)


# async def trf_generate() -> None:
#     """
#     generate a TRF file, round is specified only for that round
#     """
#     players_dict = {}
#     f = StringIO()
#     for trf in await DbICTrfRecord.find_multiple(
#         {"_model": DbICTrfRecord.DOCUMENTTYPE}
#     ):
#         players_dict[trf.player_ix] = trf

#     for k in range(len(players_dict)):
#         pl = players_dict[k + 1]
#         if not pl:
#             logger.info(f"Cannot access player at index {k + 1}")
#         if not pl.fullname:
#             pl.fullname = f"*** {pl.idbel} ***"
#         ls = " " * (90 + 10 * 11)
#         ls = replaceAt(ls, 0, "001")
#         ls = replaceAt(ls, 4, f"{pl.player_ix:4d}")
#         ls = replaceAt(ls, 9, "{:1s}".format(pl.gender or "X"))
#         ls = replaceAt(ls, 10, "{:>3s}".format(pl.chesstitle or ""))
#         ls = replaceAt(ls, 14, f"{pl.fullname:33s}")
#         ls = replaceAt(ls, 48, f"{pl.fiderating or 0:4d}")
#         ls = replaceAt(ls, 53, pl.federation)
#         ls = replaceAt(ls, 57, f"{pl.idfide or 0:11d}")
#         ls = replaceAt(ls, 69, "{:10s}".format(pl.birthdate or ""))
#         ls = replaceAt(ls, 80, f"{pl.points or 0.0:4.1f}")
#         for r in pl.rounds:
#             ls = replaceAt(ls, 81 + r.round * 10, f"{r.opponent_ix:4d}")
#             ls = replaceAt(ls, 86 + r.round * 10, r.color)
#             ls = replaceAt(ls, 88 + r.round * 10, r.scorestr)
#         if "`" in ls:
#             ls = ls.replace("`", "'")
#         f.write(ls)
#         f.write(linefeed)
#     with open("icn_trf.txt", "w") as trff:
#         trff.write(f.getvalue())


# async def trf_fide_ratings():
#     """
#     update the fide ratings in the trf report
#     """
#     for trf in await DbICTrfRecord.find_multiple(
#         {"_model": DbICTrfRecord.DOCUMENTTYPE}
#     ):
#         if not trf.idfide:
#             continue
#         try:
#             fide = elodata[trf.idbel]
#             trf.fiderating = fide["fiderating"]
#         except KeyError:
#             logger.error(f"no elodata for {trf.idbel}")
#             continue
#         await DbICTrfRecord.update({"idbel": trf.idbel}, {"fiderating": trf.fiderating})


# async def trf_report_phase1():
#     """
#     generate the trf report
#     """
#     logger.info("trf report phase 1")
#     read_eloprocessing(trfdata_2526["startround"])
#     for round in range(1, 12):
#         logger.info(f"processing round {round}")
#         await trf_process_round(round)
#     await trf_process_playerdetails1()


# async def trf_report_phase2():
#     """
#     sort the players and write the report
#     """
#     logger.info("trf report phase 2")
#     read_eloprocessing(trfdata_2526["endround"])
#     await trf_process_playerdetails2()
#     await trf_process_sort()
#     await trf_generate()


# helpers


def get_elotable() -> str:
    today = date.today()
    elomonth = (today.month - 1) // 3 * 3 + 1
    return f"p_player{today.year}{elomonth:02d}"
