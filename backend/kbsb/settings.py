# copyright Ruben Decrop 2012 - 2015
# copyright Chessdevil Consulting BVBA 2015 - 2020

import os
import logging

API_BASE_URL = "/api"

BOOKS_CC = "ruben@kosk.be"

EMAIL = {
    "backend": "GMAIL",
    "serviceaccountfile": "kbsb-gmail.json",
    "sender": "ruben.decrop@frbe-kbsb-ksb.be",
    "account": "ruben.decrop@frbe-kbsb-ksb.be",
}

EXTRASALT = "Zugzwang"

LOG_CONFIG = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": "%(levelname)s: %(asctime)s - %(name)s - %(message)s",
        },
        "color": {
            "format": "%(log_color)s%(levelname)s%(reset)s: %(asctime)s %(bold)s%(name)s%(reset)s %(message)s",
            "()": "kbsb.util.colorlogfactory.cf",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "color",
            # 'formatter': 'simple',
            "stream": "ext://sys.stderr",
        }
    },
    "loggers": {
        "kbsb": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "reddevil": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
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


# login details
GOOGLE_CLIENT_ID = (
    "767432590119-itkr36suu2qn41irsf5ie3mekfqdgt1q.apps.googleusercontent.com"
)
GOOGLE_LOGIN_DOMAINS = ["frbe-kbsb-ksb.be"]

SECRETS_PATH = "/etc//secrets"
SECRETS_EXTENSION = ""

TOKEN = {
    "timeout": 180,  # timeout in minutes
    "secret": "Pakjezakjemaggoan",
    "algorithm": "HS256",
    "nocheck": True,
}

try:
    from local_settings import *

    print("local settings loaded")
except ImportError:
    print("No local settings found")
