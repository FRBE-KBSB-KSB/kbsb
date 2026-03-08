from .md_oldsite import MailRelayValidator  # noqa F401

from .oldsite import mail_relay

from . import api_oldsite  # noqa: F401, E402


__all__ = ["mail_relay", "MailRelayValidator", "api_oldsite"]
