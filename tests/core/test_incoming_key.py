import pytest
from reddevil.core import RdNotAuthorized

from kbsb.core import apikey


def _secret(monkeypatch, value):
    monkeypatch.setattr(apikey, "get_secret", lambda name: value)


def test_configured_incoming_key_works():
    # Uses test-incoming-server.json configured in tests/settings.py
    apikey.validate_header_incoming("test-api-key", "testdomain")


def test_valid_key_for_domain(monkeypatch):
    _secret(monkeypatch, {"vsf": "secret-vsf-key", "fefb": "secret-fefb-key"})
    apikey.validate_header_incoming("secret-vsf-key", "vsf")
    apikey.validate_header_incoming("secret-fefb-key", "fefb")


def test_secret_key_with_whitespace_is_stripped(monkeypatch):
    _secret(monkeypatch, {"vsf": "secret-vsf-key\n"})
    apikey.validate_header_incoming("secret-vsf-key", "vsf")


def test_wrong_key_for_domain_is_refused(monkeypatch):
    _secret(monkeypatch, {"vsf": "secret-vsf-key"})
    with pytest.raises(RdNotAuthorized) as exc_info:
        apikey.validate_header_incoming("wrong-key", "vsf")
    assert exc_info.value.description == "InvalidIncomingServerKey"


def test_unknown_domain_is_refused(monkeypatch):
    _secret(monkeypatch, {"vsf": "secret-vsf-key"})
    with pytest.raises(RdNotAuthorized) as exc_info:
        apikey.validate_header_incoming("secret-vsf-key", "unknown-domain")
    assert exc_info.value.description == "InvalidIncomingServerKey"


def test_empty_secret_for_domain_refuses_everything(monkeypatch):
    _secret(monkeypatch, {"vsf": "", "fefb": "   "})
    with pytest.raises(RdNotAuthorized) as exc_info:
        apikey.validate_header_incoming("secret-vsf-key", "vsf")
    assert exc_info.value.description == "InvalidIncomingServerKey"

    with pytest.raises(RdNotAuthorized) as exc_info:
        apikey.validate_header_incoming("", "vsf")
    assert exc_info.value.description == "InvalidIncomingServerKey"

    with pytest.raises(RdNotAuthorized) as exc_info:
        apikey.validate_header_incoming("secret-fefb-key", "fefb")
    assert exc_info.value.description == "InvalidIncomingServerKey"


def test_empty_apikey_is_refused(monkeypatch):
    _secret(monkeypatch, {"vsf": "secret-vsf-key"})
    with pytest.raises(RdNotAuthorized) as exc_info:
        apikey.validate_header_incoming("", "vsf")
    assert exc_info.value.description == "InvalidIncomingServerKey"


@pytest.mark.parametrize("invalid_key", [None, 12345, b"secret-vsf-key", ["key"]])
def test_non_string_apikey_is_refused(monkeypatch, invalid_key):
    _secret(monkeypatch, {"vsf": "secret-vsf-key"})
    with pytest.raises(RdNotAuthorized) as exc_info:
        apikey.validate_header_incoming(invalid_key, "vsf")
    assert exc_info.value.description == "InvalidIncomingServerKey"


@pytest.mark.parametrize("secret", [None, "", b"", [], "not-a-dict"])
def test_missing_or_invalid_secret_refuses_everything(monkeypatch, secret):
    _secret(monkeypatch, secret)
    with pytest.raises(RdNotAuthorized) as exc_info:
        apikey.validate_header_incoming("secret-vsf-key", "vsf")
    assert exc_info.value.description == "InvalidIncomingServerKey"
