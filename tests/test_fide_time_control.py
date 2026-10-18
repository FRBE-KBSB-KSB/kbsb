"""
The custom time control ("Other") on the FIDE registration form is one
sentence: X min/end + S sec increment or delay, which is FRS's final session,
or with a first period X min / first Y moves + X min/end + S sec, which adds
its first control (fide_registration.vue, validate_form).
"""

import json
from pathlib import Path

from kbsb.fide.api_fide import calculate_standard_total_minutes, validate_form

FIDE_DIR = Path(__file__).parents[1] / "src/kbsb/fide"
FIELDS = json.loads((FIDE_DIR / "translations.json").read_text(encoding="utf-8"))["en"]["fields"]

TC_KEYS = [
    "timectl_other_desc",
    "timectl1_moves",
    "timectl1_minutes",
    "timectl1_inc_type",
    "timectl1_inc_seconds",
    "timectl_final_minutes",
    "timectl_final_inc_type",
    "timectl_final_inc_seconds",
]


def tc_errors(**fields):
    form = {"time_control_code": "Standard", "time_control_desc": "Other", **fields}
    labels = [FIELDS[k] for k in TC_KEYS]
    return [e for e in validate_form(form, "en") if any(e.startswith(label) for label in labels)]


def test_minutes_to_the_end_with_an_increment_is_enough():
    assert tc_errors(
        timectl_other_desc="40min/end+5sec/move from move 1",
        timectl_final_minutes="40",
        timectl_final_inc_type="Increment",
        timectl_final_inc_seconds="5",
    ) == []


def test_a_first_period_needs_both_its_moves_and_its_minutes():
    errors = tc_errors(
        timectl_other_desc="x",
        timectl1_minutes="90",
        timectl_final_minutes="30",
        timectl_final_inc_type="Increment",
        timectl_final_inc_seconds="30",
    )
    assert any(e.startswith(FIELDS["timectl1_moves"]) for e in errors)


def test_the_full_shape_passes():
    assert tc_errors(
        timectl_other_desc="90min/40moves+30min/end+30sec/move from move 1",
        timectl1_moves="40",
        timectl1_minutes="90",
        timectl1_inc_type="Increment",
        timectl1_inc_seconds="30",
        timectl_final_minutes="30",
        timectl_final_inc_type="Increment",
        timectl_final_inc_seconds="30",
    ) == []


def test_minutes_to_the_end_and_the_increment_are_required():
    errors = tc_errors(timectl_other_desc="x")
    assert any(e.startswith(FIELDS["timectl_final_minutes"]) for e in errors)
    assert any(e.startswith(FIELDS["timectl_final_inc_seconds"]) for e in errors)
    assert any(e.startswith(FIELDS["timectl_final_inc_type"]) for e in errors)


def test_total_minutes_counts_the_increment_of_the_final_session():
    # 40 min + 5 sec over 60 moves = 45 min: the 1800 ceiling applies.
    form = {
        "time_control_code": "Standard",
        "time_control_desc": "Other",
        "timectl_final_minutes": "40",
        "timectl_final_inc_seconds": "5",
    }
    assert calculate_standard_total_minutes(form) == 45.0
