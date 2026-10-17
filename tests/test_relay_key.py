import pytest
from reddevil.core import RdNotAuthorized, get_settings

import kbsb.core.apikey as apikey


def test_the_old_key_is_no_longer_in_the_settings():
    settings = get_settings()
    assert not hasattr(settings, "API_KEY")


def _secret(monkeypatch, value):
    monkeypatch.setattr(apikey, "get_secret", lambda name: value)


def test_the_key_from_secret_manager_comes_as_bytes(monkeypatch):
    # what the googletext manager returns; this crashed every relay call
    _secret(monkeypatch, b"right-key\n")
    apikey.validate_header("right-key")


def test_a_text_key_still_works(monkeypatch):
    _secret(monkeypatch, "right-key")
    apikey.validate_header("right-key")


@pytest.mark.parametrize("secret", [b"right-key", "right-key"])
def test_a_wrong_key_is_refused(monkeypatch, secret):
    _secret(monkeypatch, secret)
    with pytest.raises(RdNotAuthorized):
        apikey.validate_header("wrong-key")


@pytest.mark.parametrize("secret", [None, b"", ""])
def test_no_key_configured_refuses_everything(monkeypatch, secret):
    _secret(monkeypatch, secret)
    with pytest.raises(RdNotAuthorized):
        apikey.validate_header("")
