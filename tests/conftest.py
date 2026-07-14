import pytest
import mysql.connector
from reddevil.core import register_app, get_settings
from kbsb.main import app
from tests.factories import *  # noqa F401


@pytest.fixture
def mysql_connection():
    cnx = mysql.connector.connect(
        pool_name="kbsbpool",
        pool_size=5,
        user="root",
        password="tiger",
        host="127.0.0.1",
        database="testkbsb",
    )
    return cnx


@pytest.fixture
def settings():
    register_app(app=app, settingsmodule="kbsb.settings")
    return get_settings()
