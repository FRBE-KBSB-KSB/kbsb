from pathlib import Path

EMAIL = {
    "backend": "SMTP",
    "host": "server.chessdevil.be",
    "port": "1025",
    "sender": "ruben.decrop@frbe-kbsb-ksb.be",
}

ICDATA = "local"

ODOO_CONNECTION_PARAMETERS = {
    "url": "https://frbe-kbsb.odoo.com",
    "db": "frbe-kbsb",
    "timeout": 10.0,
    "max_keepalive": 20,
    "max_connections": 100,
}

# The test suite must start without any real secret and without network
# access (CI has neither). All secrets resolve to dummy files in
# tests/secrets; nothing in there is a real credential.
SECRETS_PATH = Path(__file__).parent / "secrets"

SECRETS = {
    "mongodb": {
        # a local MongoDB, only used by tests/interclub/testwithdb, which
        # are skipped unless KBSB_TEST_MONGODB=1
        "name": "test-mongodb",
        "manager": "filejson",
    },
    "gmail": {
        "name": "test-gmail",
        "manager": "filejson",
    },
    "odoo": {
        # read real odoo secret
        "name": "test-odoo",
        "manager": "filejson",
    },
    "salt": {
        # use dummy salt
        "name": "test-salt",
        "manager": "filejson",
    },
}

SHORTCUT_INFOMANIAKLOGIN = True

LOG_CONFIG = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": "%(levelname)s: %(asctime)s - %(name)s - %(message)s",
        },
        "color": {
            "format": "%(log_color)s%(levelname)s%(reset)s: %(asctime)s %(bold)s%(name)s%(reset)s %(message)s",
            "()": "reddevil.core.colorlogfactory.c_factory",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "color",
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
            "level": "DEBUG",
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

TEMPLATES_PATH = "./src/kbsb/templates"

TESTING = True

TOKEN = {
    "timeout": 180,  # timeout in minutes
    "secret": "Pakjezakjemaggoan,jangtvierkantmeklootnuut",
    "algorithm": "HS256",
    "nocheck": False,
}
