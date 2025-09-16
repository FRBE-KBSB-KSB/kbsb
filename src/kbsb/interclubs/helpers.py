import logging
import yaml
from reddevil.filestore.filestore import get_file
from reddevil.core import RdInternalServerError, get_settings
from .md_interclubs import (
    ICClubDB,
    DbICClub,
)
from kbsb import ROOT_DIR

logger = logging.getLogger(__name__)


async def load_icdata():
    icdata = getattr(load_icdata, "icdata", None)
    if not icdata:
        settings = get_settings()
        if settings.ICDATA == "cloud":
            icdr = await get_file("data", "ic2526.yml")
            icdata = yaml.load(icdr.body, Loader=yaml.SafeLoader)
            logger.info("loaded icdata from cloud")
        if settings.ICDATA == "local":
            icdata_path = ROOT_DIR / "shared" / "cloud" / "data" / "ic2526.yml"
            icdata = yaml.load(icdata_path.read_text(), Loader=yaml.SafeLoader)
            logger.info("loaded icdata from local")
        setattr(load_icdata, "icdata", icdata)
    return icdata


async def load_clubinfo():
    playerratings = getattr(load_clubinfo, "playerratings", None)
    clubs = getattr(load_clubinfo, "clubs", None)
    titulars = getattr(load_clubinfo, "titulars", None)
    fideratings = getattr(load_clubinfo, "fideratings", None)
    if not playerratings:
        logger.info("reading interclub ratings")
        playerratings = {}
        clubs = []
        titulars = {}
        fideratings = {}
        for clb in await DbICClub.find_multiple(
            {"_model": ICClubDB, "registered": True}
        ):
            clubs.append(clb)
            for p in clb.players:
                if p.nature in ["assigned", "imported"]:
                    playerratings[p.idnumber] = p.rating
                    fideratings[p.idnumber] = p.fiderating
                    if p.titular:
                        teamix = int(p.titular.split(" ")[-1])
                        for t in clb.teams:
                            if t.name == p.titular:
                                break
                        else:
                            logger.error(
                                f"Team {p.titular} not found in club {clb.name}"
                            )
                            raise RdInternalServerError("Fucked")
                        titulars[p.idnumber] = {
                            "team": teamix,
                            "division": t.division,
                            "index": t.index,
                            "pairingnumber": t.pairingnumber,
                        }
            setattr(load_clubinfo, "playerratings", playerratings)
            setattr(load_clubinfo, "fideratings", fideratings)
            setattr(load_clubinfo, "clubs", clubs)
            setattr(load_clubinfo, "titulars", titulars)
    return (playerratings, clubs, titulars, fideratings)


ptable = (
    [(1, 12), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7)],
    [(12, 7), (8, 6), (9, 5), (10, 4), (11, 3), (1, 2)],
    [(2, 12), (3, 1), (4, 11), (5, 10), (6, 9), (7, 8)],
    [(12, 8), (9, 7), (10, 6), (11, 5), (1, 4), (2, 3)],
    [(3, 12), (4, 2), (5, 1), (6, 11), (7, 10), (8, 9)],
    [(12, 9), (10, 8), (11, 7), (1, 6), (2, 5), (3, 4)],
    [(4, 12), (5, 3), (6, 2), (7, 1), (8, 11), (9, 10)],
    [(12, 10), (11, 9), (1, 8), (2, 7), (3, 6), (4, 5)],
    [(5, 12), (6, 4), (7, 3), (8, 2), (9, 1), (10, 11)],
    [(12, 11), (1, 10), (2, 9), (3, 8), (4, 7), (5, 6)],
    [(6, 12), (7, 5), (8, 4), (9, 3), (10, 2), (11, 1)],
)
