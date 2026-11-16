"""
Limits on failed logins, so a password cannot be guessed at full speed.

Only failures are counted. A key (the client IP, or the name tried) is locked
once it has its maximum of failures within the window; a successful login
does not reset anything, the window simply runs out.

Counted in MongoDB, not in memory: App Engine runs several instances and
restarts them, so a count in memory would start over on each. A TTL index
removes the documents after KEEP. The keys are stored hashed, so the
collection holds no IPs or names.

When MongoDB cannot be reached the login is let through (and logged): the
site cannot do much without MongoDB anyway, and refusing every login then
would lock out the people who have to fix it.
"""

import hashlib
import logging
from datetime import UTC, datetime, timedelta

from reddevil.core import RdException  # type: ignore[import-untyped]
from reddevil.core.mongodb import a_get_mongodb  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

COLLECTION = "login_failures"

# failures per name tried, and per client IP, in WINDOW
NAME_MAX = 5
IP_MAX = 20
WINDOW = timedelta(minutes=15)
KEEP = timedelta(hours=1)

_index = {"done": False}


class TooManyLoginAttempts(RdException):
    def __init__(self):
        super().__init__(status_code=429, description="TooManyLoginAttempts")


def hashed_key(kind: str, value: str) -> str:
    text = f"{kind}:{str(value).strip().lower()}"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _keys(ip: str, name: str) -> list[tuple[str, int]]:
    keys = []
    if name:
        keys.append((hashed_key("name", name), NAME_MAX))
    if ip:
        keys.append((hashed_key("ip", ip), IP_MAX))
    return keys


def _collection():
    db = a_get_mongodb()
    if db is None:
        raise RuntimeError("MongoDB is not connected")
    return db[COLLECTION]


async def _ensure_index(coll):
    if _index["done"]:
        return
    await coll.create_index("ts", expireAfterSeconds=int(KEEP.total_seconds()))
    await coll.create_index([("key", 1), ("ts", 1)])
    _index["done"] = True


async def check(ip: str, name: str) -> None:
    """Raises TooManyLoginAttempts when the IP or the name is locked."""
    keys = _keys(ip, name)
    if not keys:
        return
    try:
        coll = _collection()
        await _ensure_index(coll)
        since = datetime.now(UTC) - WINDOW
        for key, maximum in keys:
            if (
                await coll.count_documents({"key": key, "ts": {"$gte": since}})
                >= maximum
            ):
                logger.warning("login refused: too many failed attempts")
                raise TooManyLoginAttempts()
    except TooManyLoginAttempts:
        raise
    except Exception as e:
        logger.warning(
            f"login limit not checked ({type(e).__name__}); login let through"
        )


async def record_failure(ip: str, name: str) -> None:
    keys = _keys(ip, name)
    if not keys:
        return
    try:
        coll = _collection()
        await _ensure_index(coll)
        now = datetime.now(UTC)
        await coll.insert_many([{"key": key, "ts": now} for key, _ in keys])
    except Exception as e:
        logger.warning(f"login failure not recorded ({type(e).__name__})")
