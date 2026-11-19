"""
A FIDE ID is digits. On 17 November 2026 a club typed the chief arbiter's and
the chief organizer's name into the FIDE-ID box and the number into the name
box ("Tournoi Hiver 2026 2027"). The form showed the FIDE-ID box first while
the workbook lists the name first; the server took the text as an ID. Now the
name comes first on the form, the browser asks for digits, and the server
refuses anything else (kbsb.fide.api_fide.validate_form, fide_registration.vue).
"""

import json
import re

import pytest

from kbsb import ROOT_DIR
from kbsb.fide.api_fide import FIDE_ID_FIELDS, validate_form

FIDE_DIR = ROOT_DIR / "src" / "kbsb" / "fide"
TRANSLATIONS = json.loads((FIDE_DIR / "translations.json").read_text(encoding="utf-8"))
VUE = (ROOT_DIR / "frontend" / "pages" / "tools" / "fide_registration.vue").read_text(
    encoding="utf-8"
)


def id_errors(form, lang="en"):
    msg = TRANSLATIONS[lang]["messages"]["fide_id_digits_only"]
    return [e for e in validate_form(dict(form), lang) if e.endswith(msg)]


def test_every_arbiter_and_organizer_id_is_checked():
    assert len(FIDE_ID_FIELDS) == 11
    assert "chief_arbiter_fide_id" in FIDE_ID_FIELDS
    assert "organizer3_fide_id" in FIDE_ID_FIELDS


def test_the_swapped_workbook_is_refused():
    errors = id_errors(
        {
            "chief_arbiter_name": "200859",
            "chief_arbiter_fide_id": "Marchal, Georges",
            "chief_organizer_name": "202312",
            "chief_organizer_fide_id": "Lievens, Robert",
        }
    )
    assert len(errors) == 2
    assert errors[0].startswith(TRANSLATIONS["en"]["fields"]["chief_arbiter_fide_id"])


@pytest.mark.parametrize("value", ["200859", " 205024 ", 200859, "", None])
def test_digits_and_empty_boxes_pass(value):
    assert id_errors({"arbiter1_name": "Marchal, Georges", "arbiter1_fide_id": value}) == []


@pytest.mark.parametrize("value", ["n/a", "2008 59", "200859a", "Marchal"])
def test_anything_else_is_refused(value):
    assert len(id_errors({"arbiter2_fide_id": value})) == 1


@pytest.mark.parametrize("lang", ["en", "nl", "fr"])
def test_the_message_exists_in_every_language(lang):
    text = TRANSLATIONS[lang]["messages"]["fide_id_digits_only"]
    assert text and "—" not in text
    assert len(id_errors({"arbiter3_fide_id": "x"}, lang)) == 1


def test_the_form_asks_for_the_name_first_and_digits_in_the_id():
    rows = re.findall(r'<div class="person-row">(.*?)\n      </div>', VUE, re.S)
    assert len(rows) == 11
    for row in rows:
        name = re.search(r"v-model=\"form\.(\w+)_name\"", row)
        fide = re.search(r"v-model=\"form\.(\w+)_fide_id\"", row)
        assert name and fide and name.group(1) == fide.group(1)
        assert name.start() < fide.start(), name.group(1)
        assert 'pattern="[0-9]*"' in row and 'inputmode="numeric"' in row, name.group(1)
