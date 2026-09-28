import ipaddress
import os
import socket

import pytest

# Tests that need a real MongoDB (tests/interclub/testwithdb). They are
# skipped unless KBSB_TEST_MONGODB=1 and a MongoDB listens on localhost:27017
# (see tests/secrets/test-mongodb.json).
WITH_MONGODB = os.environ.get("KBSB_TEST_MONGODB") == "1"


def pytest_collection_modifyitems(config, items):
    if WITH_MONGODB:
        return
    skip_db = pytest.mark.skip(reason="needs MongoDB; set KBSB_TEST_MONGODB=1")
    for item in items:
        if "testwithdb" in item.path.parts:
            item.add_marker(skip_db)


# The suite must never reach the network: block every outgoing connection
# that is not to the loopback interface, so a missing mock fails loudly
# instead of calling Odoo, the ELO server or Google.
_real_connect = socket.socket.connect
_real_connect_ex = socket.socket.connect_ex


def _is_local(address) -> bool:
    if not isinstance(address, tuple):
        return True  # AF_UNIX and friends
    host = address[0]
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _guarded_connect(self, address):
    if not _is_local(address):
        raise RuntimeError(f"network access blocked in tests: {address!r}")
    return _real_connect(self, address)


def _guarded_connect_ex(self, address):
    if not _is_local(address):
        raise RuntimeError(f"network access blocked in tests: {address!r}")
    return _real_connect_ex(self, address)


socket.socket.connect = _guarded_connect
socket.socket.connect_ex = _guarded_connect_ex

# imported after the guard so import-time side effects are covered too
from reddevil.core import get_settings, register_app  # noqa: E402

from kbsb.main import app  # noqa: E402
from tests.factories import *  # noqa: E402, F403


@pytest.fixture
def settings():
    register_app(app=app, settingsmodule="kbsb.settings")
    return get_settings()
