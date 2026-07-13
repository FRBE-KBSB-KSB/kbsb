COLORLOG = True

EMAIL = {
    "backend": "SMTP",
    "host": "server.chessdevil.be",
    "port": "1025",
    "sender": "ruben.decrop@frbe-kbsb-ksb.be",
}

SECRETS = {
    "mongodb": {
        "name": "kbsb-mongodb-local",
        "manager": "filejson",
    },
    "mysql": {
        "name": "kbsb-mysql-infomaniak",
        "manager": "filejson",
    },
    "gdrive": {
        "name": "kbsb-gdrive-staging",
        "manager": "filejson",
    },
    "known-hosts": {
        "name": "known-hosts",
        "manager": "filejson",
    },
}

TOKEN = {
    "timeout": 180,  # timeout in minutes
    "secret": "Pakjezakjemaggoan,jangtvierkantmeklootnuut",
    "algorithm": "HS256",
    "nocheck": False,
}

TEMPLATES_PATH = "./src/kbsb/templates"
