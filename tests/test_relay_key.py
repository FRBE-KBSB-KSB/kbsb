import pytest
from reddevil.core import RdNotAuthorized

from kbsb.core import apikey


@pytest.fixture(autouse=True)
def _reset():
    apikey._cache["key"] = None
    yield
    apikey._cache["key"] = None


def test_the_key_comes_from_the_secret_not_the_code(monkeypatch):
    monkeypatch.setattr(apikey, "_read_key", lambda: "from-secret-manager")
    apikey.validate_header("from-secret-manager")
    with pytest.raises(RdNotAuthorized):
        apikey.validate_header("JeanMarieWampers")


def test_a_key_that_cannot_be_read_refuses_every_call(monkeypatch):
    def boom():
        raise RuntimeError("no access")

    monkeypatch.setattr(apikey, "_read_key", boom)
    with pytest.raises(RdNotAuthorized):
        apikey.validate_header("anything")


def test_an_empty_key_never_matches_an_empty_header(monkeypatch):
    monkeypatch.setattr(apikey, "_read_key", lambda: "")
    with pytest.raises(RdNotAuthorized):
        apikey.validate_header("")


def test_the_old_key_is_no_longer_in_the_settings():
    assert not hasattr(apikey.settings, "API_KEY")
