import logging

from fastapi import HTTPException, APIRouter, Depends
from reddevil.core import RdException
from kbsb.core.apikey import header_schema, validate_header
from . import MailRelayValidator, mail_relay

logger = logging.getLogger("kbsb")
router = APIRouter(prefix="/api/v1/oldsite")


@router.post("/mail_relay", include_in_schema=False, status_code=201)
async def api_mail_relay(
    mrv: MailRelayValidator,
    apikey: str = Depends(header_schema),
):
    """
    call mail_relay
    """
    try:
        if mrv.attachments is None:
            mrv.attachments = []
        logger.info(f"{mrv.sender=} {len(mrv.attachments)}")
        validate_header(apikey)
        await mail_relay(mrv)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call api_mail_relay")
        raise HTTPException(status_code=500, detail="Internal Server Error")
