"""
The Odoo login presents its own secret to the API, not the mail bridge's
(security review 19 Nov 2026, finding 12): the bridge secret rides on every
confirmation mail and must not also be enough to log in as any member.
"""

import types

import kbsb.tournament_registrations.api_tournament_registrations as trn


def _reset(monkeypatch):
    monkeypatch.setattr(trn, "_odoo_login_secret_cache", None, raising=False)
    monkeypatch.delenv("TOURNAMENT_REG_ODOO_LOGIN_SECRET", raising=False)
    monkeypatch.setattr(trn, "get_mail_bridge_secret", lambda: "bridge")
    monkeypatch.setattr(trn.google.auth, "default", lambda: (None, "p"))


def _secret_manager(monkeypatch, value):
    class Client:
        def access_secret_version(self, request):
            assert request["name"].endswith("/secrets/tournament-registrations-odoo-login/versions/latest")
            if value is None:
                raise RuntimeError("no such secret")
            return types.SimpleNamespace(
                payload=types.SimpleNamespace(data=value.encode("utf-8"))
            )

    monkeypatch.setattr(trn.secretmanager, "SecretManagerServiceClient", Client)


def test_the_env_override_comes_first(monkeypatch):
    _reset(monkeypatch)
    _secret_manager(monkeypatch, "from-gcp")
    monkeypatch.setenv("TOURNAMENT_REG_ODOO_LOGIN_SECRET", "from-env")
    assert trn.get_odoo_login_secret() == "from-env"


def test_the_secret_manager_secret_is_used_and_kept(monkeypatch):
    _reset(monkeypatch)
    _secret_manager(monkeypatch, "from-gcp\n")
    assert trn.get_odoo_login_secret() == "from-gcp"
    _secret_manager(monkeypatch, None)
    assert trn.get_odoo_login_secret() == "from-gcp"


def test_without_its_own_secret_it_falls_back_to_the_bridge_one_uncached(monkeypatch):
    _reset(monkeypatch)
    _secret_manager(monkeypatch, None)
    assert trn.get_odoo_login_secret() == "bridge"
    # Once the secret exists, the next login picks it up without a restart.
    _secret_manager(monkeypatch, "from-gcp")
    assert trn.get_odoo_login_secret() == "from-gcp"
