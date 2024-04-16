# settings to run everything on the deployment machine
#   - we need to have maildev running locally in docker
#   - we are still reading from the Google Cloud Bucket for the common files
#   - mongodb is running in local odcker container
#   - mysql is reffring to the Infomaniak server

EMAIL = {
    "backend": "SMTP",
    "host": "localhost",
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
}

TOKEN = {
    "timeout": 180,  # timeout in minutes
    "secret": "Pakjezakjemaggoan,jangtvierkantmeklootnuut",
    "algorithm": "HS256",
    "nocheck": False,
}
