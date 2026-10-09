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
    "odoo": {
        "name": "kbsb-odoo",
        "manager": "filejson",
    },
    "gdrive": {
        "name": "kbsb-gdrive-staging",
        "manager": "filejson",
    },
    "SU__ruben": {
        "name": "su_ruben",
        "manager": "filejson",
    },
    "eloserver": {
        "name": "hetzner-api-master",
        "manager": "filetext",
    },
    "mailrelay": {
        "name": "mail-relay-key",
        "manager": "filetext",
    },    
}

TOKEN = {
    "timeout": 180,  # timeout in minutes
    "secret": "Pakjezakjemaggoan,jangtvierkantmeklootnuut",
    "algorithm": "HS256",
    "nocheck": False,
}

TEMPLATES_PATH = "./src/kbsb/templates"

ICDATA = "local"
