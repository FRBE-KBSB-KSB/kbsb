"""
A round with an end date is one round played over two dates, not the window
in which it may be played. In 2026-09 a workbook with 20 to 55 day "rounds"
spanning month ends reached FIDE registration; the form and the server now
refuse that (kbsb.fide.api_fide.round_span_errors, fide_registration.vue).
"""

import json
from pathlib import Path

import pytest

from kbsb.fide.api_fide import round_span_errors

MSG = json.loads(
    (Path(__file__).parents[1] / "src/kbsb/fide/translations.json").read_text(encoding="utf-8")
)["en"]["messages"]


# The rounds of the workbook that reached registration.
@pytest.mark.parametrize(
    "start,end,next_start",
    [
        ("2026-10-19", "2026-11-08", "2026-11-09"),
        ("2026-11-09", "2026-11-29", "2026-11-30"),
        ("2026-11-30", "2027-01-24", "2027-01-25"),
        ("2027-01-25", "2027-02-14", "2027-02-15"),
        ("2027-03-08", "2027-03-28", "2027-03-29"),
    ],
)
def test_window_rounds_are_refused(start, end, next_start):
    assert round_span_errors(1, start, end, next_start, 8, MSG)


@pytest.mark.parametrize(
    "start,end,next_start",
    [
        ("2026-10-18", "2026-10-19", "2026-10-25"),  # a weekend
        ("2026-10-18", "2026-10-25", "2026-11-01"),  # a week apart
        ("2026-10-18", "2026-10-18", "2026-10-19"),  # same day
        ("2026-10-24", "2026-10-25", "2026-10-25"),  # ends the day the next starts
    ],
)
def test_normal_rounds_pass(start, end, next_start):
    assert round_span_errors(1, start, end, next_start, 8, MSG) == []


def test_each_rule_has_its_own_message():
    period = round_span_errors(1, "2026-10-26", "2026-11-02", None, 8, MSG)[0]
    assert "rating periods" in period and "2026-10-26" in period
    too_long = round_span_errors(1, "2026-10-01", "2026-10-20", None, 8, MSG)[0]
    assert "19 days" in too_long
    overlap = round_span_errors(3, "2026-10-18", "2026-10-22", "2026-10-20", 8, MSG)[0]
    assert "Round 4" in overlap and "2026-10-20" in overlap


def test_month_end_transition_is_its_own_period():
    # the last two days of a month are a separate FIDE period
    assert round_span_errors(1, "2026-10-28", "2026-10-31", None, 8, MSG)


def test_last_round_has_no_next_round():
    assert round_span_errors(8, "2027-04-10", "2027-04-11", None, 8, MSG) == []


def test_messages_exist_in_every_language():
    t = json.loads(
        (Path(__file__).parents[1] / "src/kbsb/fide/translations.json").read_text(encoding="utf-8")
    )
    for lang in ("en", "nl", "fr"):
        for key in (
            "round_end_date_period_error",
            "round_end_date_too_long",
            "round_end_date_overlap_error",
        ):
            assert key in t[lang]["messages"], (lang, key)
