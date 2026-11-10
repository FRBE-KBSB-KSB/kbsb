"""
The tournament registrations proxy forwards only the path shapes the frontend
calls (SEC-32): the proxy adds the master-scoped key, so anything broader is
the whole dataplatform API. The OpenPairings and native SWAR file exports
are two more such shapes, and must not open anything else.
"""

import pytest
from fastapi import HTTPException

from kbsb.tournament_registrations.api_tournament_registrations import (
    TARGET_BASE_URL,
    _proxied_url,
)


@pytest.mark.parametrize(
    "path",
    [
        "admin/tournaments/42/export/openpairings",
        "admin/tournaments/42/export/swarfile",
        "admin/tournaments/42/export/csv",
        "admin/tournaments/42/export/swar/all",
        "admin/tournaments/42/registrations",
    ],
)
def test_frontend_shapes_are_forwarded(path):
    assert _proxied_url(path) == f"{TARGET_BASE_URL}/{path}"


@pytest.mark.parametrize(
    "path",
    [
        "admin/tournaments/42/export/openpairings/x",
        "admin/tournaments/42/export/openpairings/..",
        "admin/tournaments/../export/openpairings",
        "admin/tournaments/42/../../../players_fide/export/openpairings",
        "admin/tournaments/42/export/openpairings%2F..",
        "admin/tournaments/42/export/../../../players_fide",
        "admin/tournaments/42/export",
        "admin/tournaments/42/export/openpairingsx",
        "../players_fide/export/openpairings",
        "admin/tournaments/42/export/swarfile/x",
        "admin/tournaments/42/export/swarfile/..",
        "admin/tournaments/../export/swarfile",
        "admin/tournaments/42/../../../players_fide/export/swarfile",
        "admin/tournaments/42/export/swarfile%2F..",
        "admin/tournaments/42/export/swarfilex",
        "admin/tournaments/42/export/swarfile.swar",
        "../players_fide/export/swarfile",
    ],
)
def test_anything_else_is_refused(path):
    with pytest.raises(HTTPException) as exc:
        _proxied_url(path)
    assert exc.value.status_code == 404
