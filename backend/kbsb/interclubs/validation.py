import logging
from datetime import datetime, timedelta, timezone, time
from .md_interclubs import (
    ICSeries,
    ICTeam,
    ICRound,
    ICEncounter,
    ICValidationError,
    DbICSeries,
)
from .helpers import load_icdata, load_playerratings

logger = logging.getLogger(__name__)


class LineUpValidation:
    """
    This class validates the line-up of players for interclub matches.
    It covers both planning and results.
    """

    def __init__(self) -> None:
        self.validationerrors = []

    async def a_init(self) -> None:
        self.series = await self.read_interclubseries()
        self.playerratings = await load_playerratings()
        self.icdata = await load_icdata()

    def _getround(self, s: ICSeries, round: int) -> ICRound:
        for rnd in s.rounds:
            if rnd.round == round:
                return rnd
        raise RuntimeError(f"Round {round} not found in series {s.division}{s.index}")

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
        rnd = self._getround(s, round)
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
        self.validationerrors.append(
            ICValidationError(
                errormessage=reason,
                division=s.division,
                index=s.index,
                pnr_offender=pnr_offender,
                round=round,
                icclub_offender=idclub,
                icclub_opponent=icclub_opponent,
                name=nameteams.get(pnr_offender, "###"),
                name_opponent=nameteams.get(pnr_opponent, "###"),
            )
        )

    def check_forfaits(self):
        for s in self.series.values():
            rnd = self._getround(s, round)
            for encix, enc in enumerate(rnd.encounters):
                if enc.icclub_home == 0 or enc.icclub_visit == 0:
                    continue
                for gix, g in enumerate(enc.games):
                    if g.result in ["1-0 FF", "0-0 FF"]:
                        self.create_issue(
                            "forfait away",
                            enc.icclub_visit,
                            s,
                            round,
                            encix,
                            enc.pairingnr_visit,
                            gix,
                        )
                    if g.result in ["0-1 FF", "0-0 FF"]:
                        self.create_issue(
                            "forfait home",
                            enc.icclub_home,
                            s,
                            round,
                            encix,
                            enc.pairingnr_home,
                            gix,
                        )

    def check_signatures(self):
        for s in self.series.values():
            rnd = self._getround(s, round)
            nextday = self.icdata["rounds"][rnd] + timedelta(days=1)
            homesigndate = datetime.combine(nextday, time(0)).astimezone(timezone.utc)
            visitsigndate = datetime.combine(nextday, time(12)).astimezone(timezone.utc)
            for encix, enc in enumerate(rnd.encounters):
                if enc.icclub_home == 0 or enc.icclub_visit == 0:
                    continue
                if not enc.signhome_ts:
                    self.create_issue(
                        reason="signature home missing",
                        idclub=enc.icclub_home,
                        s=s,
                        round=round,
                        encix=encix,
                    )
                elif enc.signhome_ts.astimezone(timezone.utc) > homesigndate:
                    self.create_issue(
                        reason="signature home too late",
                        idclub=enc.icclub_home,
                        s=s,
                        round=round,
                        encix=encix,
                    )
                if not enc.signvisit_ts:
                    self.create_issue(
                        reason="signature away missing",
                        idclub=enc.icclub_visit,
                        s=s,
                        round=round,
                        encix=encix,
                    )
                elif enc.signvisit_ts.astimezone(timezone.utc) > visitsigndate:
                    self.create_issue(
                        reason="signature away too late",
                        idclub=enc.icclub_visit,
                        s=s,
                        round=round,
                        encix=encix,
                    )

    def check_order_players(self, round, idclub):
        for s in self.series.values():
            rnd = self._getround(s, round)
            for encix, enc in enumerate(rnd.encounters):
                if idclub not in (enc.icclub_home, enc.icclub_visit):
                    continue
                if enc.icclub_home == 0 or enc.icclub_visit == 0:
                    continue
                if idclub == enc.icclub_home:
                    homeratings = []
                    for gix, g in enumerate(enc.games):
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
                            {"ix": gix, "rating": homerating, "plr": g.idnumber_home}
                        )
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
                            {"ix": gix, "rating": visitrating, "plr": g.idnumber_visit}
                        )
                    diff = len(visitratings) / 2
                    visitratings.sort(key=lambda x: x["rating"])
                    for i, vr in enumerate(visitratings):
                        if vr["ix"] < i - diff or vr["ix"] > i + diff:
                            self.create_issue(
                                reason="visit player order is not correct",
                                s=s,
                                encix=encix,
                                idclub=idclub,
                                gameix=vr["ix"],
                                pairingnr=enc.pairingnr_visit,
                            )

    def check_average_elo(self):
        for clb in allclubs:
            avgdivs = {}
            for t in clb.teams:
                serie = self.series[(t.division, t.index)]
                round = getround(serie, rnd)
                encounters = [
                    e
                    for e in round.encounters
                    if t.pairingnumber in (e.pairingnr_home, e.pairingnr_visit)
                ]
                if len(encounters) != 1:
                    logger.info(
                        f"We're fucked to get encounter of {t.name} in {serie.division}{serie.index}"
                    )
                    for ct in clb.teams:
                        logger.info(f"debugging club team {ct}")
                    raise RdInternalServerError("No encounters found")
                enc = encounters[0]
                if not enc.icclub_home or not enc.icclub_visit:  # bye
                    continue
                if not enc.boardpoint2_home or not enc.boardpoint2_visit:  # not played]
                    continue
                if t.pairingnumber == enc.pairingnr_home:
                    ratings = [
                        playerratings[g.idnumber_home]
                        for g in enc.games
                        if g.idnumber_home and playerratings.get(g.idnumber_home)
                    ]
                if t.pairingnumber == enc.pairingnr_visit:
                    ratings = [
                        playerratings[g.idnumber_visit]
                        for g in enc.games
                        if g.idnumber_visit and playerratings.get(g.idnumber_visit)
                    ]
                avgdiv = avgdivs.setdefault(serie.division, [])
                if ratings:
                    avgdiv.append(sum(ratings) / len(ratings))
            maxdiv2 = max(avgdivs.get(2, [0]))
            maxdiv3 = max(avgdivs.get(3, [0]))
            maxdiv4 = max(avgdivs.get(4, [0]))
            maxdiv5 = max(avgdivs.get(5, [0]))
            mindiv1 = avgdivs.get(1, [3000])[0]
            mindiv2 = min(avgdivs.get(2, [3000]))
            mindiv3 = min(avgdivs.get(3, [3000]))
            if maxdiv2 > mindiv1:
                logger.info(f"{t.idclub} Avg elo too high in division 2")
            if maxdiv3 > min(mindiv1, mindiv2):
                logger.info(f"{t.idclub} Avg elo too high in division 3")
            if maxdiv4 > min(mindiv1, mindiv2, mindiv3):
                logger.info(f"{t.idclub} Avg elo too high in division 4")
            if maxdiv5 > min(mindiv1, mindiv2, mindiv3):
                logger.info(f"{t.idclub} Avg elo too high in division 4")

    def check_titular_ok(self):
        for s in self.series.values():
            round = getround(s, rnd)
            for enc in round.encounters:
                if enc.icclub_home == 0 or enc.icclub_visit == 0:
                    continue
                for ix, g in enumerate(enc.games):
                    if g.idnumber_home in playertitular:
                        if s.division > playertitular[g.idnumber_home]["division"]:
                            report_issue(
                                s,
                                ix,
                                enc.pairingnr_home,
                                0,
                                "Titular played in a division too low",
                            )
                        if (
                            s.division == playertitular[g.idnumber_home]["division"]
                            and s.index != playertitular[g.idnumber_home]["index"]
                        ):
                            report_issue(
                                s,
                                ix,
                                enc.pairingnr_home,
                                0,
                                "Titular played in wrong series",
                            )
                        if (
                            s.division == playertitular[g.idnumber_home]["division"]
                            and s.index == playertitular[g.idnumber_home]["index"]
                            and enc.pairingnr_home
                            != playertitular[g.idnumber_home]["pairingnumber"]
                        ):
                            report_issue(
                                s,
                                ix,
                                enc.pairingnr_home,
                                0,
                                "Titular played in wrong team in the series",
                            )
                    if g.idnumber_visit in playertitular:
                        if s.division > playertitular[g.idnumber_visit]["division"]:
                            report_issue(
                                s,
                                ix,
                                enc.pairingnr_visit,
                                0,
                                "Titular played in a division too low",
                            )
                        if (
                            s.division == playertitular[g.idnumber_visit]["division"]
                            and s.index != playertitular[g.idnumber_visit]["index"]
                        ):
                            report_issue(
                                s,
                                ix,
                                enc.pairingnr_visit,
                                0,
                                "Titular played in wrong series",
                            )
                        if (
                            s.division == playertitular[g.idnumber_visit]["division"]
                            and s.index == playertitular[g.idnumber_visit]["index"]
                            and enc.pairingnr_visit
                            != playertitular[g.idnumber_visit]["pairingnumber"]
                        ):
                            report_issue(
                                s,
                                ix,
                                enc.pairingnr_visit,
                                0,
                                "Titular played in wrong team in the series",
                            )

    def check_reserves_in_single_series(self):
        for idclub, division, index, pnr1, pnr2 in doublepairings:
            series = self.series[(division, index)]
            # build up sets of previous players
            players1 = set()
            players2 = set()
            for rr in range(1, r):
                round = getround(series, rr)
                for enc in round.encounters:
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
            round = getround(series, r)
            for enc in round.encounters:
                if enc.icclub_home == 0 or enc.icclub_visit == 0:
                    continue
                club601 = enc.icclub_home == 601 or enc.icclub_visit == 601
                if pnr1 in (enc.pairingnr_home, enc.pairingnr_visit):
                    for ix, g in enumerate(enc.games):
                        if club601:
                            logger.info(
                                f"game pn1 {g.idnumber_home} - {g.idnumber_visit}"
                            )
                        if pnr1 == enc.pairingnr_home and g.idnumber_home in players2:
                            report_issue(
                                series,
                                ix,
                                pnr1,
                                0,
                                f"player {g.idnumber_home} already played in other team of series",
                            )
                        elif (
                            pnr1 == enc.pairingnr_visit and g.idnumber_visit in players2
                        ):
                            report_issue(
                                series,
                                ix,
                                pnr1,
                                0,
                                f"player {g.idnumber_visit} already played in other team of series",
                            )
                if pnr2 in (enc.pairingnr_home, enc.pairingnr_visit):
                    for ix, g in enumerate(enc.games):
                        if club601:
                            logger.info(
                                f"game pnr2 {g.idnumber_home} - {g.idnumber_visit}"
                            )
                        if pnr2 == enc.pairingnr_home and g.idnumber_home in players1:
                            report_issue(
                                series,
                                ix,
                                pnr2,
                                0,
                                f"player {g.idnumber_home} already played in other team of series",
                            )
                        elif (
                            pnr2 == enc.pairingnr_visit and g.idnumber_visit in players1
                        ):
                            report_issue(
                                series,
                                ix,
                                pnr2,
                                0,
                                f"player {g.idnumber_visit} already played in other team of series",
                            )

    def check_reserves_elotoohigh(self):
        for s in self.series.values():
            maxelo = icdata["max_elo"][s.division]
            round = getround(s, r)
            for enc in round.encounters:
                if enc.icclub_home == 0 or enc.icclub_visit == 0:
                    continue
                for ix, g in enumerate(enc.games):
                    # skip if player is titular for the team
                    t_home = playertitular.get(g.idnumber_home, {})
                    if (
                        t_home
                        and t_home["division"] == s.division
                        and t_home["index"] == s.index
                        and t_home["pairingnumber"] == enc.pairingnr_home
                    ):
                        continue
                    t_visit = playertitular.get(g.idnumber_visit, {})
                    if (
                        t_visit
                        and t_visit["division"] == s.division
                        and t_visit["index"] == s.index
                        and t_visit["pairingnumber"] == enc.pairingnr_visit
                    ):
                        continue
                    # now check the elo
                    fide_home = fideratings.get(g.idnumber_home, 0)
                    if fide_home > maxelo:
                        report_issue(
                            s, ix, enc.pairingnr_home, 0, "fide rating reserve too high"
                        )
                    fide_visit = fideratings.get(g.idnumber_visit, 0)
                    if fide_home > maxelo:
                        report_issue(
                            s, ix, enc.pairingnr_home, 0, "fide rating reserve too high"
                        )
                    if fide_visit > maxelo:
                        report_issue(
                            s,
                            ix,
                            enc.pairingnr_visit,
                            0,
                            "fide rating reserve too high",
                        )

    async def read_interclubseries(self) -> dict[tuple[int, int], ICSeries]:
        a = {}
        for s in await DbICSeries.find_multiple({"_model": ICSeries}):
            a[(s.division, s.index)] = s
        return a

    async def validate_planning(
        self, idclub: int, round: int
    ) -> list[ICValidationError]:
        """
        Validate the planning of interclub matches for a specific club and round.
        This method checks various aspects such as forfaits, signatures, player order,
        average elo, titular players, reserves in single series, and reserves elo too high.
        """
        self.validationerrors: list[ICValidationError] = []
        self.idclub = idclub
        self.round = round
        await self.a_init()
        self.check_order_players(round, idclub)
        # self.check_average_elo(round)
        # self.check_titular_ok(round)
        # self.check_reserves_in_single_series(round)
        # self.check_reserves_elotoohigh(round)
        return self.validationerrors

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
        self.check_order_players(round, idclub)
        # self.check_average_elo(round)
        # self.check_titular_ok(round)
        # self.check_reserves_in_single_series(round)
        # self.check_reserves_elotoohigh(round)
        return self.validationerrors
