#    Copyright 2021 Chessdevil Consulting
import json
import aiofiles
fron pathlib import Path
from google.cloud import secretmanager
from kbsb.main import settings


def secretmanager_client():
    if not hasattr(secretmanager_client, "sc"):
        setattr(
            secretmanager_client, "sc", secretmanager.SecretManagerServiceClient()
        )
    return


def get_secret(name: str):
    project = settings.GOOGLE_PROJECT
    version = settings.SECRETS.get(name, "latest")
    if settings.SECRET_MANAGER == "google":
        reply = secretmanager_client().access_secret_version(request={
            "name": f"projects/{project}/secrets/{name}/versions/{version}"
        })
        return json.loads(reply.payload.data)
    if settings.SECRET_MANAGER == "filejson":
        secretfile = Path(settings.SECRET_PATH) / f"{name}.json"
        with open(secretfile) as f:
            return json.load(f)
