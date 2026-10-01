"""
The report deadline on the FIDE registration form. The KBSB expects a report
within 4 days after its end date (for a New long tournament, the end of the
report's last round; a report is one file for all rounds of one FIDE rating
period). Day x-1 at 12:00 (x the last day of the month) is the last chance for
that month's list, shown for every report; an end date in the last two days
of a month counts for the next month's list. An end date from x-6 to x-2 is
the critical window: the form warns, the organiser ticks it, and the server
asks for the tick for the same reports
(kbsb.fide.api_fide.get_report_deadline, report_groups, fide_registration.vue).
"""

import csv
import json
import re
from datetime import date
from pathlib import Path

import pytest

from kbsb.fide.api_fide import (
    get_report_deadline,
    report_deadline_mail,
    report_groups,
    validate_form,
)

FIDE_DIR = Path(__file__).parents[1] / "src/kbsb/fide"
TRANSLATIONS = json.loads((FIDE_DIR / "translations.json").read_text(encoding="utf-8"))


def d(text):
    return date.fromisoformat(text)


@pytest.mark.parametrize(
    "end,critical,cutoff",
    [
        # September, 30 days: 24 to 28, cutoff 29 Sep
        ("2026-09-23", False, None),
        ("2026-09-24", True, "2026-09-29"),
        ("2026-09-28", True, "2026-09-29"),
        ("2026-09-29", False, None),  # FIDE transition period
        ("2026-09-30", False, None),
        # February 2027, 28 days: 22 to 26, cutoff 27 Feb
        ("2027-02-21", False, None),
        ("2027-02-22", True, "2027-02-27"),
        ("2027-02-26", True, "2027-02-27"),
        ("2027-02-27", False, None),
        # October, 31 days: 25 to 29, cutoff 30 Oct
        ("2026-10-24", False, None),
        ("2026-10-25", True, "2026-10-30"),
        ("2026-10-29", True, "2026-10-30"),
        ("2026-10-30", False, None),
        # February 2028, leap year: 23 to 27, cutoff 28 Feb
        ("2028-02-22", False, None),
        ("2028-02-23", True, "2028-02-28"),
        ("2028-02-27", True, "2028-02-28"),
        ("2028-02-28", False, None),
        ("2028-02-29", False, None),
    ],
)
def test_critical_window(end, critical, cutoff):
    deadline = get_report_deadline(end)
    assert deadline["critical"] is critical
    assert deadline["cutoff"] == (d(cutoff) if cutoff else None)


@pytest.mark.parametrize(
    "end,last_chance",
    [
        ("2026-12-01", "2026-12-30"),  # December has 31 days: x-1 is the 30th
        ("2026-12-18", "2026-12-30"),
        ("2026-12-29", "2026-12-30"),
        ("2026-12-30", "2027-01-30"),  # transition period: January's list
        ("2026-12-31", "2027-01-30"),
        ("2026-09-18", "2026-09-29"),
        ("2026-09-29", "2026-10-30"),
        ("2026-09-30", "2026-10-30"),
        ("2027-01-31", "2027-02-27"),
        ("2027-06-25", "2027-06-29"),
        ("2028-01-30", "2028-02-28"),  # leap year
    ],
)
def test_last_chance(end, last_chance):
    assert get_report_deadline(end)["last_chance"] == d(last_chance)


@pytest.mark.parametrize(
    "end,expected",
    [
        ("2026-09-20", "2026-09-24"),
        ("2026-09-28", "2026-10-02"),
        ("2026-12-18", "2026-12-22"),
        ("2026-12-30", "2027-01-03"),
        ("2027-02-26", "2027-03-02"),
        ("2028-02-27", "2028-03-02"),
        ("2028-02-29", "2028-03-04"),
    ],
)
def test_expected_by_is_end_plus_four_days(end, expected):
    assert get_report_deadline(end)["expected"] == d(expected)


@pytest.mark.parametrize("end", ["", None, "2026-02-30", "2026-13-01", "26-09-2026"])
def test_invalid_dates_have_no_deadline(end):
    assert get_report_deadline(end) is None


def ack_errors(form, lang="en"):
    marker = TRANSLATIONS[lang]["messages"]["report_deadline_ack_required"].split("{reports}")[0]
    return [e for e in validate_form(dict(form), lang) if e.startswith(marker)]


def single(end, **extra):
    return {"tournament_report": "All rounds in 1 report", "start_date": end, "end_date": end, **extra}


def long_tournament(rounds, **extra):
    form = {
        "tournament_report": "New long tournament",
        "rounds_reported": str(len(rounds)),
        **extra,
    }
    for i, (start, end, report) in enumerate(rounds, start=1):
        form[f"round{i}_date"] = start
        form[f"round{i}_end_date"] = end
        form[f"round{i}_report"] = report
    return form


# The club's season: three reports of three rounds; report 1 ends on 18
# December 2026, report 3 on 25 June 2027 (in June's window, 24 to 28).
SEASON = long_tournament(
    [
        ("2026-12-04", "", "1"),
        ("2026-12-11", "", "1"),
        ("2026-12-18", "", "1"),
        ("2027-03-05", "", "2"),
        ("2027-03-12", "", "2"),
        ("2027-03-19", "", "2"),
        ("2027-06-04", "", "3"),
        ("2027-06-11", "", "3"),
        ("2027-06-25", "", "3"),
    ]
)


def mail_items(html):
    return re.findall(r"<li>(.*?)</li>", html)


def test_reports_group_the_rounds_like_the_form():
    groups = report_groups(SEASON)
    assert [(g["num"], g["rounds"], g["end"]) for g in groups] == [
        (1, [1, 2, 3], "2026-12-18"),
        (2, [4, 5, 6], "2027-03-19"),
        (3, [7, 8, 9], "2027-06-25"),
    ]
    # A round on the last two days of a month is a report of its own.
    late = long_tournament([("2026-09-05", "", "1"), ("2026-09-30", "", "2"), ("2026-10-03", "", "3")])
    assert [g["rounds"] for g in report_groups(late)] == [[1], [2], [3]]
    # Report per round: one report per round, whatever the periods.
    per_round = {**SEASON, "report_per_round": True}
    assert [g["rounds"] for g in report_groups(per_round)] == [[i] for i in range(1, 10)]


def test_season_mail_per_report_nl():
    items = mail_items(report_deadline_mail(SEASON, "nl"))
    assert len(items) == 3
    first, second, third = items
    # report 1: 18 December, outside the window: expected 22 December, last
    # chance 30 December (December has 31 days), no warning
    assert first.startswith("Rapport 1 (rondes 1, 2 en 3), laatste ronde op 18 december 2026")
    assert "verwacht uiterlijk op 22 december 2026" in first
    assert "Laatste kans voor de ratinglijst van december: 30 december om 12u." in first
    assert "Opgepast" not in first
    assert "Laatste kans voor de ratinglijst van maart: 30 maart om 12u." in second
    assert "Opgepast" not in second
    # report 3: 25 June, in the window
    assert third.startswith("Rapport 3 (rondes 7, 8 en 9), laatste ronde op 25 juni 2027")
    assert "Laatste kans voor de ratinglijst van juni: 29 juni om 12u." in third
    assert (
        "Opgepast: dien het rapport voor de rondes 7, 8 en 9 in uiterlijk op 29 juni om 12u, "
        "anders wordt het niet meer in de ratinglijst van juni verwerkt en kan u een boete krijgen."
    ) in third


def test_season_mail_per_report_en_fr():
    en = mail_items(report_deadline_mail(SEASON, "en"))
    assert en[0].startswith("Report 1 (rounds 1, 2 and 3)")
    assert "Last chance for the December rating list: 30 December at 12:00." in en[0]
    assert "Please note: send in the report for rounds 7, 8 and 9 by 29 June at 12:00" in en[2]
    fr = mail_items(report_deadline_mail(SEASON, "fr"))
    assert fr[0].startswith("Rapport 1 (rondes 1, 2 et 3)")
    assert "Dernière chance pour la liste de classement de décembre : le 30 décembre à 12h." in fr[0]
    assert "Attention : envoyez le rapport 3 (rondes 7, 8 et 9) au plus tard le 29 juin à 12h" in fr[2]


def test_season_tick_only_for_report_3():
    errors = ack_errors(SEASON, "nl")
    assert len(errors) == 1
    assert errors[0].endswith(
        "de KBSB moet rapport 3 (rondes 7, 8 en 9) uiterlijk op 29 juni 2027 om 12u ontvangen."
    )
    assert "rapport 1" not in errors[0]
    assert ack_errors({**SEASON, "report_deadline_ack": True}, "nl") == []
    # Report 3 ending on 18 June instead: no tick at all.
    assert ack_errors({**SEASON, "round9_date": "2027-06-18"}) == []


def test_single_tournament_in_window_needs_the_tick():
    errors = ack_errors(single("2026-09-26"))
    assert len(errors) == 1
    assert "the tournament report by 29 September 2026 at 12:00 at the latest" in errors[0]
    assert ack_errors(single("2026-09-26", report_deadline_ack=True)) == []


@pytest.mark.parametrize("end", ["2026-09-23", "2026-09-29", "2026-09-30", "2026-10-05"])
def test_single_tournament_outside_window_needs_no_tick(end):
    assert ack_errors(single(end)) == []


def test_long_tournament_last_round_of_the_report_counts():
    # Round 2 is played over two dates and ends in the window: as the last
    # round of report 1 its end counts.
    form = long_tournament(
        [
            ("2026-09-05", "", "1"),
            ("2026-09-19", "2026-09-26", "1"),
            ("2026-10-03", "", "2"),
        ]
    )
    errors = ack_errors(form)
    assert len(errors) == 1
    assert "report 1 (rounds 1 and 2) by 29 September 2026 at 12:00" in errors[0]
    assert ack_errors({**form, "report_deadline_ack": True}) == []
    # Without the end date round 2 ends on 19 September: no tick needed.
    assert ack_errors({**form, "round2_end_date": ""}) == []


def test_long_tournament_report_listed_once():
    # Two rounds of one report in the window: one report, one cutoff.
    form = long_tournament([("2026-09-24", "", "1"), ("2026-09-27", "", "1")])
    errors = ack_errors(form)
    assert len(errors) == 1
    assert errors[0].endswith(
        "the KBSB must receive report 1 (rounds 1 and 2) by 29 September 2026 at 12:00 at the latest."
    )
    # Reported per round they are two reports, each with its own deadline.
    errors = ack_errors({**form, "report_per_round": True})
    assert "report 1 (round 1) by 29 September 2026" in errors[0]
    assert "and report 2 (round 2) by 29 September 2026" in errors[0]


def test_long_tournament_lists_every_report():
    form = long_tournament(
        [
            ("2026-09-26", "", "1"),
            ("2026-10-10", "", "2"),
            ("2026-10-27", "", "2"),
            ("2026-10-31", "", "3"),  # transition period, not critical
        ]
    )
    errors = ack_errors(form, "nl")
    assert len(errors) == 1
    assert (
        "rapport 1 (ronde 1) uiterlijk op 29 september 2026 om 12u en "
        "rapport 2 (rondes 2 en 3) uiterlijk op 30 oktober 2026 om 12u"
    ) in errors[0]
    assert ack_errors({**form, "report_deadline_ack": "true"}, "nl") == []


def test_long_tournament_outside_window_needs_no_tick():
    form = long_tournament(
        [("2026-09-05", "", "1"), ("2026-09-29", "", "2"), ("2026-10-03", "", "3")]
    )
    assert ack_errors(form) == []


def test_mail_single_tournament():
    html = report_deadline_mail(single("2026-09-27"), "nl")
    assert "1 oktober 2026" in html
    assert "29 september om 12u" in html and "ratinglijst van september" in html
    assert "kan u een boete krijgen" in html
    calm = report_deadline_mail(single("2026-09-20"), "en")
    assert "24 September 2026" in calm
    assert "Last chance for the September rating list: 29 September at 12:00." in calm
    assert "Please note" not in calm


def test_mail_single_tournament_ending_on_the_18th():
    html = report_deadline_mail(single("2026-12-18"), "nl")
    assert "dus uiterlijk op 22 december 2026" in html
    assert "Laatste kans voor de ratinglijst van december: 30 december om 12u." in html
    assert "Opgepast" not in html


@pytest.mark.parametrize(
    "end,lang,text",
    [
        ("2026-09-30", "nl", "Laatste kans voor de ratinglijst van oktober: 30 oktober om 12u."),
        ("2026-12-30", "en", "Last chance for the January rating list: 30 January at 12:00."),
        ("2027-01-31", "fr", "Dernière chance pour la liste de classement de février : le 27 février à 12h."),
    ],
)
def test_transition_days_count_for_the_next_list(end, lang, text):
    html = report_deadline_mail(single(end), lang)
    assert text in html
    assert "color: #b45309" not in html
    late = report_deadline_mail(long_tournament([("2026-09-05", "", "1"), (end, "", "2")]), lang)
    assert text in mail_items(late)[1]


def test_mail_long_tournament_per_report():
    form = long_tournament(
        [
            ("2026-09-05", "", "1"),
            ("2026-09-19", "2026-09-26", "1"),
            ("2026-10-03", "", "2"),
        ]
    )
    html = report_deadline_mail(form, "fr")
    # report 1 ends 26 September: expected 30 September, cutoff 29 September
    assert html.count("<li>") == 2
    assert "30 septembre 2026" in html and "29 septembre à 12h" in html
    assert "liste de classement de septembre et vous pouvez recevoir une amende" in html
    assert "7 octobre 2026" in html
    oct_html = report_deadline_mail(long_tournament([("2026-10-27", "", "1")]), "fr")
    assert "liste de classement d'octobre" in oct_html
    assert "rapport 1 (ronde 1)" in oct_html


def test_confirmation_mail_has_the_placeholder():
    for lang in ("en", "nl", "fr"):
        assert "{report_deadlines}" in TRANSLATIONS[lang]["messages"]["conf_body"]


NEW_KEYS = {
    "ui": ["report_deadline_ack"],
    "messages": [
        "report_rounds_one",
        "report_rounds_many",
        "report_expected_report",
        "report_expected_tournament",
        "report_last_chance",
        "report_ack_item_report",
        "report_ack_item_tournament",
        "report_deadline_critical_tournament",
        "report_deadline_critical_report",
        "report_deadline_ack_required",
        "mail_report_deadline_tournament",
        "mail_report_deadline_intro",
        "mail_report_deadline_report",
    ],
}


def test_translations_json_and_csv_agree():
    with (FIDE_DIR / "translations_fide.csv").open(newline="", encoding="utf-8") as f:
        rows = {(r["section"], r["key"]): r for r in csv.DictReader(f)}
    for section, keys in NEW_KEYS.items():
        for key in keys:
            for lang in ("en", "nl", "fr"):
                value = TRANSLATIONS[lang][section][key]
                assert value and value == rows[(section, key)][lang], (section, key, lang)
                assert "\u2014" not in value  # no em-dashes in the texts
    for lang in ("en", "nl", "fr"):
        assert TRANSLATIONS[lang]["messages"]["conf_body"] == rows[("messages", "conf_body")][lang]
    # Retired with the per round deadline lines.
    assert ("ui", "report_expected_by") not in rows
    assert ("messages", "report_deadline_critical_round") not in rows


@pytest.mark.parametrize(
    "lang,fine",
    [
        ("en", "you may be fined"),
        ("nl", "kan u een boete krijgen"),
        ("fr", "vous pouvez recevoir une amende"),
    ],
)
def test_critical_warnings_mention_the_fine(lang, fine):
    for kind in ("tournament", "report"):
        assert fine in TRANSLATIONS[lang]["messages"][f"report_deadline_critical_{kind}"]
