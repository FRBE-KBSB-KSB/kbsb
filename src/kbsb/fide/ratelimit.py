# Limits on the FIDE registration form, so it cannot be used to make the
# federation mail its workbook to any address over and over. The form mails a
# confirmation copy to the addresses typed in it; Turnstile keeps the bots out,
# these limits are the second line for whoever gets past it.
#
# Counted in MongoDB, not in memory: App Engine runs several instances and
# restarts them, so a count in memory would start over on each. Every accepted
# submit stores one document per key (the client IP, each confirmation
# address) with its time; a submit is refused when a key already has its
# maximum within the window. A TTL index removes the documents after KEEP.
# The keys are stored hashed, so the collection holds no IPs or addresses.
#
# When MongoDB cannot be reached the submit is let through (and logged): a
# registration that does not reach fide@ costs more than a missed count, and
# Turnstile is still in front.

import hashlib
import logging
from datetime import UTC, datetime, timedelta

from reddevil.core.mongodb import a_get_mongodb

logger = logging.getLogger(__name__)

# submits per client IP
IP_PER_HOUR = 5
IP_PER_DAY = 20
# confirmation mails per destination address
ADDRESS_PER_DAY = 5

HOUR = timedelta(hours=1)
DAY = timedelta(days=1)
# how long a document is kept: longer than the longest window
KEEP = 2 * DAY

COLLECTION = "fide_form_ratelimit"

# message key in translations.json
MSG_RATE_LIMITED = "rate_limited"

_index = {"done": False}


def hashed_key(kind: str, value: str) -> str:
    """The stored key for an IP ("ip") or an address ("mail")."""
    text = f"{kind}:{str(value).strip().lower()}"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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


async def _count(coll, key: str, since: datetime) -> int:
    return await coll.count_documents({"key": key, "ts": {"$gte": since}})


async def check_and_record(ip: str, addresses: list[str]) -> str | None:
    """
    For a submit from ip that mails a confirmation to each of addresses:
    None when it is within the limits, and then it is counted; else the
    message key of the refusal, and nothing is counted.
    """
    keys = []
    try:
        coll = _collection()
        await _ensure_index(coll)
        now = datetime.now(UTC)
        if ip:
            key = hashed_key("ip", ip)
            if await _count(coll, key, now - HOUR) >= IP_PER_HOUR:
                logger.warning("FIDE form refused: too many submits from one IP in an hour")
                return MSG_RATE_LIMITED
            if await _count(coll, key, now - DAY) >= IP_PER_DAY:
                logger.warning("FIDE form refused: too many submits from one IP in a day")
                return MSG_RATE_LIMITED
            keys.append(key)
        for address in dict.fromkeys(a.strip().lower() for a in addresses if a):
            key = hashed_key("mail", address)
            if await _count(coll, key, now - DAY) >= ADDRESS_PER_DAY:
                logger.warning("FIDE form refused: too many confirmation mails to one address in a day")
                return MSG_RATE_LIMITED
            keys.append(key)
        if keys:
            await coll.insert_many([{"key": k, "ts": now} for k in keys])
    except Exception as e:
        logger.warning(f"FIDE form rate limit not checked ({type(e).__name__}); submit let through")
        return None
    return None
