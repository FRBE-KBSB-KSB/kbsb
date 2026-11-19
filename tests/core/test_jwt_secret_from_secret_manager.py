"""
In production the JWT secret comes from Secret Manager (kbsb-jwt): the one in
settings.py is in a public repository. Without a usable secret the site does
not start.
"""

import pytest
import reddevil.core
from reddevil.core import get_setting, get_settings

from kbsb import main


@pytest.fixture
def restore(monkeypatch):
    monkeypatch.setitem(get_setting("JWT"), "secret", get_setting("JWT")["secret"])
    monkeypatch.setattr(get_settings(), "JWT_SECRET", get_setting("JWT_SECRET"))
    return monkeypatch


def test_the_secret_replaces_the_public_one_everywhere(restore):
    public = get_setting("JWT")["secret"]
    new = "s" * 40
    restore.setattr(
        reddevil.core,
        "get_secret",
        lambda name: {"secret": new} if name == "jwt" else None,
    )

    main._use_jwt_secret_from_secret_manager()

    from kbsb.core import tokens

    assert tokens.jwt_settings["secret"] == new
    assert get_setting("JWT_SECRET") == new
    assert new != public


@pytest.mark.parametrize(
    "value", [{}, {"secret": ""}, {"secret": "short"}, "text", None]
)
def test_without_a_usable_secret_the_site_does_not_start(restore, value):
    before = get_setting("JWT")["secret"]
    restore.setattr(reddevil.core, "get_secret", lambda name: value)

    with pytest.raises(RuntimeError):
        main._use_jwt_secret_from_secret_manager()
    assert get_setting("JWT")["secret"] == before


def test_production_switches():
    from kbsb import settings

    # testing mode here; production is the default when KBSB_MODE is unset
    assert settings.KBSB_MODE != "production"
    assert settings.JWT_FROM_SECRET_MANAGER is False
    assert settings.OPENAPI_URL == "/openapi.json"
