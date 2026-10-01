"""
The report deadline on the FIDE registration form. The KBSB expects a report
within 4 days after its end date; an end date from x-6 to x-2 (x the last day
of the month) is the critical window, where the report has to be in by day x-1
at 12:00 to be rated in that month's list. The form shows it, the organiser
ticks it, and the server asks for the tick for the same dates
(kbsb.fide.api_fide.get_report_deadline, fide_registration.vue).
"""

import csv
import json
from datetime import date
from pathlib import Path

import pytest

from kbsb.fide.api_fide import (
    get_report_deadline,
    report_deadline_mail,
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
    "end,expected",
    [
        ("2026-09-20", "2026-09-24"),
        ("2026-09-28", "2026-10-02"),
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
    marker = TRANSLATIONS[lang]["messages"]["report_deadline_ack_required"].split("{dates}")[0]
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


def test_single_tournament_in_window_needs_the_tick():
    errors = ack_errors(single("2026-09-26"))
    assert len(errors) == 1 and "29 September 2026" in errors[0]
    assert ack_errors(single("2026-09-26", report_deadline_ack=True)) == []


@pytest.mark.parametrize("end", ["2026-09-23", "2026-09-29", "2026-09-30", "2026-10-05"])
def test_single_tournament_outside_window_needs_no_tick(end):
    assert ack_errors(single(end)) == []


def test_long_tournament_each_round_counts():
    # Round 2 is played over two dates and ends in the window: its end counts.
    form = long_tournament(
        [
            ("2026-09-05", "", "1"),
            ("2026-09-19", "2026-09-26", "1"),
            ("2026-10-03", "", "2"),
        ]
    )
    errors = ack_errors(form)
    assert len(errors) == 1 and "29 September 2026" in errors[0]
    assert ack_errors({**form, "report_deadline_ack": True}) == []
    # Without the end date round 2 ends on 19 September: no tick needed.
    assert ack_errors({**form, "round2_end_date": ""}) == []


def test_long_tournament_lists_every_cutoff():
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
    assert "29 september 2026 en 30 oktober 2026" in errors[0]
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
    assert "24 September 2026" in calm and "12:00" not in calm


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


def test_confirmation_mail_has_the_placeholder():
    for lang in ("en", "nl", "fr"):
        assert "{report_deadlines}" in TRANSLATIONS[lang]["messages"]["conf_body"]


NEW_KEYS = {
    "ui": ["report_expected_by", "report_deadline_ack"],
    "messages": [
        "report_deadline_critical_round",
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


@pytest.mark.parametrize(
    "lang,fine",
    [
        ("en", "you may be fined"),
        ("nl", "kan u een boete krijgen"),
        ("fr", "vous pouvez recevoir une amende"),
    ],
)
def test_critical_warnings_mention_the_fine(lang, fine):
    for kind in ("round", "tournament", "report"):
        assert fine in TRANSLATIONS[lang]["messages"][f"report_deadline_critical_{kind}"]
