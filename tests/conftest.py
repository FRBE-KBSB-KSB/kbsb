import pytest
from reddevil.core import get_settings, register_app

from kbsb.main import app
from tests.factories import *


@pytest.fixture
def settings():
    register_app(app=app, settingsmodule="kbsb.settings")
    return get_settings()
