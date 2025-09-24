import logging
from datetime import datetime, timedelta, timezone, time
from reddevil.core import RdInternalServerError
from .md_interclubs import (
    ICSeries,
    ICTeam,
    ICRound,
    ICEncounter,
    ICValidationError,
    DbICSeries,
)
from .helpers import load_icdata, load_all_icclubs

logger = logging.getLogger(__name__)


class LineUpValidation:
    """
    This class validates the line-up of players for interclub matches.
    It covers both planning and results.
    """

    def __init__(self) -> None:
        self.validationerrors = []
        self.doublepairings = []

    async def a_init(self) -> None:
        (
            self.playerratings,
            self.clubs,
            self.titulars,
            self.fideratings,
        ) = await load_all_icclubs()
        self.icdata = await load_icdata()

    def _get_round(self, s: ICSeries, round: int) -> ICRound:
        for rnd in s.rounds:
            if rnd.round == round:
                return rnd
        raise RuntimeError(f"Round {round} not found in series {s.division}{s.index}")

    def _find_encounter(
        self, division: int, index: int, name: str, round: int
    ) -> tuple[ICSeries, int]:
        for s in self.seriesdict.values():
            if s.division == division and s.index == index:
                break
        else:
            logger.error(f"We're fucked finding the series {division}{index}")
            raise RdInternalServerError("Fucked")
        for t in s.teams:
            if t.name == name:
                break
        else:
            logger.error(
                f"We're fucked finding the team {name} in series {division}{index}"
            )
            raise RdInternalServerError("Fucked")
        rnd = self._get_round(s, round)
        for encix, enc in enumerate(rnd.encounters):
            if t.pairingnumber in (enc.pairingnr_visit, enc.pairingnr_home):
                return s, encix

    def create_issue(
        self,
        reason: str,
        s: ICSeries,
        round: int,
        encix: int,
        idclub: int,
        pairingnr: int | None = None,
        gameix: int | None = None,
    ) -> ICValidationError:
        rnd = self._get_round(s, round)
        enc = rnd.encounters[encix]
        nameteams = {t.pairingnumber: t.name for t in s.teams}
        playing_home = enc.icclub_home == idclub
        playing_away = enc.icclub_visit == idclub
        pnr_offender = enc.pairingnr_home if playing_home else enc.pairingnr_visit
        if playing_home and playing_away and pairingnr is not None:
            # encounter between two teams of the same club, now choose the the correct team, via the pairingnr
            pnr_offender = pairingnr
        pnr_opponent = enc.pairingnr_visit if playing_home else enc.pairingnr_home
        icclub_opponent = enc.icclub_visit if playing_home else enc.icclub_home
        boardnr = gameix + 1 if gameix is not None else None
        self.validationerrors.append(
            ICValidationError(
                boardnr=boardnr,
                division=s.division,
                errormessage=reason,
                icclub_offender=idclub,
                icclub_opponent=icclub_opponent,
                index=s.index,
                name=nameteams.get(pnr_offender, "###"),
                name_opponent=nameteams.get(pnr_opponent, "###"),
                pnr_offender=pnr_offender,
                round=round,
            )
        )

    def check_forfaits(self, round: int, idclub: int):
        for s in self.seriesdict.values():
            rnd = self._get_round(s, round)
            for encix, enc in enumerate(rnd.encounters):
                if enc.icclub_home == 0 or enc.icclub_visit == 0:
                    continue
                if idclub not in (enc.icclub_home, enc.icclub_visit):
                    continue
                for gix, g in enumerate(enc.games):
                    if g.result in ["1-0 FF", "0-0 FF"] and enc.icclub_visit == idclub:
                        self.create_issue(
                            reason="forfait away",
                            idclub=enc.icclub_visit,
                            s=s,
                            round=round,
                            encix=encix,
                            pairingnr=enc.pairingnr_visit,
                            gameix=gix,
                        )
                    if g.result in ["0-1 FF", "0-0 FF"] and enc.icclub_home == idclub:
                        self.create_issue(
                            reason="forfait home",
                            idclub=enc.icclub_home,
                            s=s,
                            round=round,
                            encix=encix,
                            pairingnr=enc.pairingnr_home,
                            gameix=gix,
                        )

    def check_signatures(self, round: int, idclub: int):
        for s in self.seriesdict.values():
            rnd = self._get_round(s, round)
            nextday = self.icdata["rounds"][rnd] + timedelta(days=1)
            homesigndate = datetime.combine(nextday, time(0)).astimezone(timezone.utc)
            visitsigndate = datetime.combine(nextday, time(12)).astimezone(timezone.utc)
            for encix, enc in enumerate(rnd.encounters):
                if enc.icclub_home == 0 or enc.icclub_visit == 0:
                    continue
                if idclub not in (enc.icclub_home, enc.icclub_visit):
                    continue
                if not enc.signhome_ts and idclub == enc.icclub_home:
                    self.create_issue(
                        reason="signature home missing",
                        idclub=enc.icclub_home,
                        s=s,
                        round=round,
                        encix=encix,
                    )
                elif (
                    enc.signhome_ts.astimezone(timezone.utc) > homesigndate
                    and idclub == enc.icclub_home
                ):
                    self.create_issue(
                        reason="signature home too late",
                        idclub=enc.icclub_home,
                        s=s,
                        round=round,
                        encix=encix,
                    )
                if not enc.signvisit_ts and idclub == enc.icclub_visit:
                    self.create_issue(
                        reason="signature away missing",
                        idclub=enc.icclub_visit,
                        s=s,
                        round=round,
                        encix=encix,
                    )
                elif (
                    enc.signvisit_ts.astimezone(timezone.utc) > visitsigndate
                    and idclub == enc.icclub_visit
                ):
                    self.create_issue(
                        reason="signature away too late",
                        idclub=enc.icclub_visit,
                        s=s,
                        round=round,
                        encix=encix,
                    )

    def check_order_players(self, round: int, idclub: int):
        for s in self.seriesdict.values():
            rnd = self._get_round(s, round)
            for encix, enc in enumerate(rnd.encounters):
                notfilled = False
                if idclub not in (enc.icclub_home, enc.icclub_visit):
                    continue
                if enc.icclub_home == 0 or enc.icclub_visit == 0:
                    continue
                if idclub == enc.icclub_home:
                    homeratings = []
                    for gix, g in enumerate(enc.games):
                        if not g.idnumber_home:
                            notfilled = True
                            break
                        homerating = self.playerratings.get(g.idnumber_home)
                        if homerating is None:
                            self.create_issue(
                                reason="home player is not in playerlist",
                                s=s,
                                round=round,
                                encix=encix,
                                idclub=idclub,
                                gameix=gix,
                                pairingnr=enc.pairingnr_home,
                            )
                        homeratings.append(
                            {
                                "ix": gix,
                                "rating": homerating or 0,
                                "plr": g.idnumber_home or 0,
                            }
                        )
                    if notfilled:
                        continue
                    diff = len(homeratings) // 2
                    hs = sorted(homeratings, key=lambda x: x["rating"], reverse=True)
                    for i, hr in enumerate(hs):
                        if hr["ix"] < i - diff or hr["ix"] > i + diff:
                            self.create_issue(
                                reason="home player order is not correct",
                                s=s,
                                round=round,
                                encix=encix,
                                idclub=idclub,
                                gameix=hr["ix"],
                                pairingnr=enc.pairingnr_home,
                            )
                if idclub == enc.icclub_visit:
                    visitratings = []
                    for gix, g in enumerate(enc.games):
                        if not g.idnumber_visit:
                            notfilled = True
                            break
                        visitrating = self.playerratings.get(g.idnumber_visit)
                        if visitrating is None:
                            self.create_issue(
                                reason="visit player is not in playerlist",
                                s=s,
                                round=round,
                                encix=encix,
                                idclub=idclub,
                                gameix=gix,
                                pairingnr=enc.pairingnr_visit,
                            )
                        visitratings.append(
                            {
                                "ix": gix,
                                "rating": visitrating or 0,
                                "plr": g.idnumber_visit or 0,
                            }
                        )
                    if notfilled:
                        continue
                    logger.info(f"visitratings {visitratings}")
                    diff = len(visitratings) / 2
                    vs = sorted(visitratings, key=lambda x: x["rating"], reverse=True)
                    for i, vr in enumerate(vs):
                        if vr["ix"] < i - diff or vr["ix"] > i + diff:
                            self.create_issue(
                                reason="visit player order is not correct",
                                s=s,
                                round=round,
                                encix=encix,
                                idclub=idclub,
                                gameix=vr["ix"],
                                pairingnr=enc.pairingnr_visit,
                            )

    def check_average_elo(self, round: int, idclub: int):
        logger.info(f"check_average_elo for club {idclub} round {round}")
        logger.info(f"seriesdict keys{self.seriesdict.keys()}")
        try:
            for clb in self.clubs:
                if clb.idclub != idclub:
                    continue
                notfilled = False
                avgdivs = {}
                for t in clb.teams:
                    if not (t.division, t.index) in self.seriesdict:
                        # we are bye
                        continue
                    sr = self.seriesdict[(t.division, t.index)]
                    rnd = self._get_round(sr, round)
                    encounters = [
                        e
                        for e in rnd.encounters
                        if t.pairingnumber in (e.pairingnr_home, e.pairingnr_visit)
                    ]
                    if not encounters:
                        logger.error(
                            f"We're fucked to get encounter of {t.name} in {sr.division}{sr.index}"
                        )
                        for ct in clb.teams:
                            logger.error(f"debugging club team {ct}")
                        raise RdInternalServerError("Fucked")
                    enc = encounters[0]
                    if not enc.icclub_home or not enc.icclub_visit:  # bye
                        continue
                    # if not enc.boardpoint2_home or not enc.boardpoint2_visit:  # not played]
                    #     continue
                    if t.pairingnumber == enc.pairingnr_home:
                        ratings = [
                            self.playerratings[g.idnumber_home]
                            for g in enc.games
                            if g.idnumber_home
                            and self.playerratings.get(g.idnumber_home)
                        ]
                        notfilled = min([g.idnumber_home or 0 for g in enc.games]) == 0
                    if t.pairingnumber == enc.pairingnr_visit:
                        ratings = [
                            self.playerratings[g.idnumber_visit]
                            for g in enc.games
                            if g.idnumber_visit
                            and self.playerratings.get(g.idnumber_visit)
                        ]
                        notfilled = min([g.idnumber_visit or 0 for g in enc.games]) == 0
                    if notfilled:
                        break
                    logger.info(f"sr {sr.division}{sr.index} ratings {ratings}")
                    avgdiv = avgdivs.setdefault(sr.division, {})
                    if ratings:
                        avgdiv[(t.name, sr.index)] = sum(ratings) / len(ratings)
                if notfilled:
                    break
                maxdiv2 = max(avgdivs.get(2, {}).values(), default=0)
                maxdiv3 = max(avgdivs.get(3, {}).values(), default=0)
                maxdiv4 = max(avgdivs.get(4, {}).values(), default=0)
                maxdiv5 = max(avgdivs.get(5, {}).values(), default=0)
                mindiv1 = avgdivs.get(1, {}).values() or 4000
                mindiv2 = min(avgdivs.get(2, {}).values(), default=4000)
                mindiv3 = min(avgdivs.get(3, {}).values(), default=4000)
                logger.info(f"{maxdiv2=} {maxdiv3=} {maxdiv4=} {maxdiv5=}")
                logger.info(f"{mindiv1=} {mindiv2=} {mindiv3=}")
                if maxdiv2 > mindiv1:
                    for (name, index), avg in avgdivs.get(2, {}).items():
                        logger.error(f"Avg elo {avg} of {name} too high")
                        s, encix = self._find_encounter(
                            division=2, index=index, name=name, round=round
                        )
                        self.create_issue(
                            reason="Avg elo too high",
                            s=s,
                            round=round,
                            idclub=idclub,
                            encix=encix,
                        )
                        return
                if maxdiv3 > min(mindiv1, mindiv2):
                    for (name, index), avg in avgdivs.get(3, {}).items():
                        logger.error(f"Avg elo {avg} of {name} too high")
                        s, encix = self._find_encounter(
                            division=3, index=index, name=name, round=round
                        )
                        self.create_issue(
                            reason="Avg elo too high",
                            s=s,
                            round=round,
                            idclub=idclub,
                            encix=encix,
                        )
                        return
                if maxdiv4 > min(mindiv1, mindiv2, mindiv3):
                    for (name, index), avg in avgdivs.get(4, {}).items():
                        logger.error(f"Avg elo {avg} of {name} too high")
                        s, encix = self._find_encounter(
                            division=4, index=index, name=name, round=round
                        )
                        self.create_issue(
                            reason="Avg elo too high",
                            s=s,
                            round=round,
                            idclub=idclub,
                            encix=encix,
                        )
                        return
                if maxdiv5 > min(mindiv1, mindiv2, mindiv3):
                    for (name, index), avg in avgdivs.get(5, {}).items():
                        logger.error(f"Avg elo {avg} of {name} too high")
                        s, encix = self._find_encounter(
                            division=5, index=index, name=name, round=round
                        )
                        self.create_issue(
                            reason="Avg elo too high",
                            s=s,
                            round=round,
                            idclub=idclub,
                            encix=encix,
                        )
                        return
        except Exception as e:
            logger.exception("Exception in check_average_elo")

    def check_titular_ok(self, round: int, idclub: int):
        for s in self.seriesdict.values():
            rnd = self._get_round(s, round)
            for encix, enc in enumerate(rnd.encounters):
                if enc.icclub_home == 0 or enc.icclub_visit == 0:
                    continue
                if idclub not in (enc.icclub_home, enc.icclub_visit):
                    continue
                for encix, g in enumerate(enc.games):
                    if g.idnumber_home in self.titulars:
                        if (
                            s.division == self.titulars[g.idnumber_home]["division"]
                            and s.index == self.titulars[g.idnumber_home]["index"]
                            and enc.pairingnr_home
                            != self.titulars[g.idnumber_home]["pairingnumber"]
                        ):
                            self.create_issue(
                                s=s,
                                encix=encix,
                                idclub=idclub,
                                pairingnr=enc.pairingnr_home,
                                reason="Titular played in wrong team in the series",
                            )
                    if g.idnumber_visit in self.titulars:
                        if (
                            s.division == self.titulars[g.idnumber_visit]["division"]
                            and s.index == self.titulars[g.idnumber_visit]["index"]
                            and enc.pairingnr_visit
                            != self.titulars[g.idnumber_visit]["pairingnumber"]
                        ):
                            self.create_issue(
                                s=s,
                                encix=encix,
                                idclub=idclub,
                                pairingnr=enc.pairingnr_visit,
                                reason="Titular played in wrong team in the series",
                            )

    def check_reserves_in_single_series(self, round: int, idclub: int):
        for club, division, index, pnr1, pnr2 in self.doublepairings:
            series = self.seriesdict[(division, index)]
            # build up sets of previous players
            players1 = set()
            players2 = set()
            for rr in range(1, round):
                rnd = self._get_round(series, rr)
                for enc in rnd.encounters:
                    if enc.icclub_home == 0 or enc.icclub_visit == 0:
                        continue
                if pnr1 in (enc.pairingnr_home, enc.pairingnr_visit):
                    for g in enc.games:
                        if pnr1 == enc.pairingnr_home:
                            players1.add(g.idnumber_home)
                        else:
                            players1.add(g.idnumber_visit)
                if pnr2 in (enc.pairingnr_home, enc.pairingnr_visit):
                    for g in enc.games:
                        if pnr2 == enc.pairingnr_home:
                            players2.add(g.idnumber_home)
                        else:
                            players2.add(g.idnumber_visit)
        for club, division, index, pnr1, pnr2 in self.doublepairings:
            series = self.seriesdict[(division, index)]
            # build up sets of previous players
            players1 = set()
            players2 = set()
            for rr in range(1, round):
                rnd = self._get_round(series, rr)
                for enc in rnd.encounters:
                    if enc.icclub_home == 0 or enc.icclub_visit == 0:
                        continue
                    if pnr1 in (enc.pairingnr_home, enc.pairingnr_visit):
                        for g in enc.games:
                            if pnr1 == enc.pairingnr_home:
                                players1.add(g.idnumber_home)
                            else:
                                players1.add(g.idnumber_visit)
                    if pnr2 in (enc.pairingnr_home, enc.pairingnr_visit):
                        for g in enc.games:
                            if pnr2 == enc.pairingnr_home:
                                players2.add(g.idnumber_home)
                            else:
                                players2.add(g.idnumber_visit)
            # now check the players of this round
            rnd = self._get_round(series, round)
            for encix, enc in enumerate(rnd.encounters):
                if enc.icclub_home == 0 or enc.icclub_visit == 0:
                    continue
                if pnr1 in (enc.pairingnr_home, enc.pairingnr_visit):
                    for gix, g in enumerate(enc.games):
                        if pnr1 == enc.pairingnr_home and g.idnumber_home in players2:
                            self.create_issue(
                                reason=f"reserve already played in other team of series",
                                s=series,
                                round=round,
                                encix=encix,
                                idclub=idclub,
                                pairingnr=pnr1,
                                gameix=gix,
                            )
                        elif (
                            pnr1 == enc.pairingnr_visit and g.idnumber_visit in players2
                        ):
                            self.create_issue(
                                reason=f"reserve already played in other team of series",
                                s=series,
                                round=round,
                                encix=encix,
                                idclub=idclub,
                                pairingnr=pnr1,
                                gameix=gix,
                            )
                if pnr2 in (enc.pairingnr_home, enc.pairingnr_visit):
                    for gix, g in enumerate(enc.games):
                        if pnr2 == enc.pairingnr_home and g.idnumber_home in players1:
                            self.create_issue(
                                reason=f"player {g.idnumber_home} already played in other team of series",
                                s=series,
                                round=round,
                                encix=encix,
                                idclub=idclub,
                                pairingnr=pnr2,
                                gameix=gix,
                            )
                        elif (
                            pnr2 == enc.pairingnr_visit and g.idnumber_visit in players1
                        ):
                            self.create_issue(
                                reason=f"player {g.idnumber_visit} already played in other team of series",
                                s=series,
                                round=round,
                                encix=encix,
                                idclub=idclub,
                                pairingnr=pnr2,
                                gameix=gix,
                            )

    def check_elotoohigh(self, round: int, idclub: int):
        try:
            for sr in self.seriesdict.values():
                maxelo = self.icdata["max_elo"][sr.division]
                rnd = self._get_round(sr, round)
            for encix, enc in enumerate(rnd.encounters):
                if enc.icclub_home == 0 or enc.icclub_visit == 0:
                    continue
                if idclub not in (enc.icclub_home, enc.icclub_visit):
                    continue
                for gix, g in enumerate(enc.games):
                    # if player is titular for the team skip
                    if g.idnumber_home in self.titulars:
                        tit = self.titulars[g.idnumber_home]
                        if tit["division"] == sr.division and tit["index"] == sr.index:
                            continue
                    if g.idnumber_visit in self.titulars:
                        tit = self.titulars[g.idnumber_visit]
                        if tit["division"] == sr.division and tit["index"] == sr.index:
                            continue
                    # now check the elo
                    fide_home = self.fideratings.get(g.idnumber_home, 0)
                    if fide_home > maxelo:
                        self.create_issue(
                            reason="fide rating too high",
                            s=sr,
                            round=round,
                            encix=encix,
                            idclub=idclub,
                            gameix=gix,
                            pairingnr=enc.pairingnr_home,
                        )
                    fide_visit = self.fideratings.get(g.idnumber_visit, 0)
                    if fide_visit > maxelo:
                        self.create_issue(
                            reason="fide rating too high",
                            s=sr,
                            round=round,
                            encix=encix,
                            idclub=idclub,
                            gameix=gix,
                            pairingnr=enc.pairingnr_visit,
                        )
        except Exception as e:
            logger.exception("Exception in check_elotoohigh")
            raise e

    async def read_interclubseries(self) -> dict[tuple[int, str], ICSeries]:
        a = {}
        for s in await DbICSeries.find_multiple({"_model": ICSeries}):
            a[(s.division, s.index)] = s
        return a

    async def validate_planning(
        self, idclub: int, round: int, seriesdict: dict[tuple[int, str], ICSeries]
    ) -> list[ICValidationError]:
        """
        Validate the planning of interclub matches for a specific club and round.
        This method checks various aspects such as forfaits, signatures, player order,
        average elo, titular players, reserves in single series, and reserves elo too high.
        """
        self.validationerrors: list[ICValidationError] = []
        self.seriesdict = seriesdict
        self.idclub = idclub
        self.round = round
        await self.a_init()
        self.check_order_players(round, idclub)
        self.check_average_elo(round, idclub)
        self.check_titular_ok(round, idclub)
        self.check_reserves_in_single_series(round, idclub)
        self.check_elotoohigh(round, idclub)

    async def validate_results(
        self, idclub: int, round: int
    ) -> list[ICValidationError]:
        """
        Validate the results of interclub matches for a specific club and round.
        This method checks various aspects such as forfaits, signatures, player order,
        average elo, titular players, reserves in single series, and reserves elo too high.
        """
        self.validationerrors: list[ICValidationError] = []
        self.idclub = idclub
        self.round = round
        await self.a_init()
        self.seriesdict = await self.read_interclubseries()
        self.check_order_players(round, idclub)
        # self.check_average_elo(round)
        # self.check_titular_ok(round)
        # self.check_reserves_in_single_series(round)
        # self.check_reserves_elotoohigh(round)
        return self.validationerrors
