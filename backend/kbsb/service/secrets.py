#    Copyright 2021 Chessdevil Consulting
import logging
import json
import yaml
from pathlib import Path
from typing import Any
from google.cloud import secretmanager
from kbsb.main import settings
from reddevil.common.errors import RdInternalServerError

log = logging.getLogger(__name__)


def secretmanager_client():
    if not hasattr(secretmanager_client, "sc"):
        setattr(secretmanager_client, "sc", secretmanager.SecretManagerServiceClient())
        log.info(f"secretmanagerclient {secretmanager_client.sc}")
    return secretmanager_client.sc


def get_secret(name: str) -> Any:
    project = settings.GOOGLE_PROJECT
    sconfig = settings.SECRETS.get(name, None)
    if not sconfig:
        log.error(f"Secret {name} not configured")
        raise RdInternalServerError(desription="SecretNotConfigured")
    sname = sconfig.get("name", name)
    manager = sconfig.get("manager", "filejson")
    if manager == "googlejson":
        version = sconfig.get("version", "latest")
        reply = secretmanager_client().access_secret_version(
            request={"name": f"projects/{project}/secrets/{sname}/versions/{version}"}
        )
        return json.loads(reply.payload.data)
    if manager == "googleyaml":
        version = sconfig.get("version", "latest")
        reply = secretmanager_client().access_secret_version(
            request={"name": f"projects/{project}/secrets/{sname}/versions/{version}"}
        )
        return yaml.safe_load(reply.payload.data)
    if manager == "filejson":
        extension = sconfig.get("extension", ".json")
        sfile = Path(settings.SECRETS_PATH) / f"{sname}{extension}"
        with open(sfile) as f:
            return json.load(f)
    if manager == "fileyaml":
        extension = sconfig.get("extension", ".yaml")
        sfile = Path(settings.SECRETS_PATH) / f"{sname}{extension}"
        with open(sfile) as f:
            return yaml.safe_load(f)
