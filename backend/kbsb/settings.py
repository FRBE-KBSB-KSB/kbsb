# copyright Ruben Decrop 2012 - 2022

import os
from pathlib import Path
import logging.config

API_BASE_URL = "/api"

BOOKS_CC = "ruben@kosk.be"
BOARDROLES_PATH = os.environ.get("BOARDROLES", "./boardroles.yaml")
COLORLOG = False
DEBUG = os.environ.get("DEBUG_KBSB", False)

EMAIL = {
    "backend": "GMAIL",
    "serviceaccountfile": "kbsb-gmail.json",
    "sender": "ruben.decrop@frbe-kbsb-ksb.be",
    "account": "ruben.decrop@frbe-kbsb-ksb.be",
    "blindcopy": "ruben.kbsb@gmail.com",
}

EXTRASALT = "Zugzwang"

FILESTORE = {
    "manager": "google",
    "bucket": os.environ.get("FILESTORE_BUCKET", "website-kbsb-prod.appspot.com"),
}

# login details
GOOGLE_CLIENT_ID = os.environ.get(
    "GOOGLE_CLIENT_ID",
    "658290412135-v6ah768urdv83dn76ra4mkiovdalal2k.apps.googleusercontent.com",
)
GOOGLE_LOGIN_DOMAINS = ["frbe-kbsb-ksb.be"]
GOOGLE_PROJECT_ID = os.environ.get("GOOGLE_PROJECT_ID", "website-kbsb-prod")
GOOGLEDRIVE_TRANSLATIONID = "1sLMHvI9nM_EmT3kqqxQRz59b42zGjfbOdlzoFEStbD0"

ICDATA_PATH = os.environ.get("ICDATA_PATH", "../data/ic2425.yml")
INTERCLUBS_CC_EMAIL = "interclubs@frbe-kbsb-ksb.be"

JWT_ALGORITHM = "HS256"
JWT_SECRET = "levedetorrevanostende"


LOG_CONFIG = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": "%(levelname)s: %(name)s - %(message)s",
        },
        "color": {
            "format": "%(log_color)s%(levelname)s%(reset)s: %(asctime)s %(bold)s%(name)s%(reset)s %(message)s",
            "()": "reddevil.core.colorlogfactory.c_factory",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        }
    },
    "loggers": {
        "kbsb": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "reddevil": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "fastapi": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

KBSB_MODE = os.environ.get("KBSB_MODE", "production")

MEMBERDB = "oldmysql"

SECRETS = {
    "mongodb": {
        "name": "kbsb-mongodb",
        "manager": "googlejson",
    },
    "mysql": {
        "name": "kbsb-mysql",
        "manager": "googlejson",
    },
    "gmail": {
        "name": "kbsb-gmail",
        "manager": "googlejson",
    },
    "known-hosts": {
        "name": "known-hosts",
        "manager": "googlejson",
    },
    "S_001": {
        "name": "S_001",
        "manager": "googlejson",
    },
}

SECRETS_PATH = Path(os.environ.get("SECRETS_PATH", ""))

SHARED_PATH = Path(os.environ.get("SHARED_PATH", "./shared"))

SHORTCUT_INFOMANIAKLOGIN = False

TEMPLATES_PATH = os.environ.get("TEMPLATES_PATH", "./kbsb/templates")

TOKEN = {
    "timeout": 180,  # timeout in minutes
    "secret": "Pakjezakjemaggoan,jangtvierkantmeklootnuut",
    "algorithm": "HS256",
    "nocheck": False,
}


if KBSB_MODE == "local":
    from env_local import *  # noqa F403


if KBSB_MODE == "prodtest":
    from env_prodtest import *  # noqa F403


if COLORLOG:
    LOG_CONFIG["handlers"]["console"]["formatter"] = "color"

logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger(__name__)

settings_message = {
    "local": "env_local settings loaded",
    "prodtest": "env_prodtest settings loaded",
}
logger.info(settings_message.get(KBSB_MODE, "no local settings loaded"))
