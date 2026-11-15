"""
A FIDE registration that starts in less than 14 days is tagged LATE_. The
days are counted from today in Brussels, not from the server's UTC date, which
is still yesterday between midnight and 01:00 (02:00 in summer).
"""

from datetime import UTC, date, datetime

from kbsb.fide import api_fide


class FrozenDatetime(datetime):
    """datetime, with now() fixed at a given UTC instant."""

    instant = datetime(2027, 3, 7, 23, 30, tzinfo=UTC)

    @classmethod
    def now(cls, tz=None):
        if tz is None:
            return cls.instant.replace(tzinfo=None)
        return cls.instant.astimezone(tz)


def test_today_is_the_brussels_date_just_after_midnight(monkeypatch):
    # 23:30 UTC on 7 March is 00:30 on 8 March in Brussels (winter time)
    monkeypatch.setattr(api_fide, "datetime", FrozenDatetime)
    assert api_fide.today_in_brussels() == date(2027, 3, 8)


def test_today_in_summer_time(monkeypatch):
    # 22:30 UTC on 1 July is 00:30 on 2 July in Brussels (summer time)
    monkeypatch.setattr(
        FrozenDatetime, "instant", datetime(2027, 7, 1, 22, 30, tzinfo=UTC)
    )
    monkeypatch.setattr(api_fide, "datetime", FrozenDatetime)
    assert api_fide.today_in_brussels() == date(2027, 7, 2)


def _submit(monkeypatch, today, start, send=None):
    from fastapi.testclient import TestClient
    from reddevil.core import get_settings

    from kbsb.fide import ratelimit, turnstile
    from kbsb.main import app

    monkeypatch.setattr(get_settings(), "TURNSTILE_SITEKEY", "", raising=False)
    monkeypatch.setattr(turnstile, "_secret_cache", {"value": None, "failed_at": 0.0})
    monkeypatch.setattr(ratelimit, "a_get_mongodb", lambda: None)
    mails = []
    monkeypatch.setattr(api_fide, "sendEmailMessage", send or mails.append)
    monkeypatch.setattr(api_fide, "today_in_brussels", lambda: today)
    end = start.isoformat()
    form = {
        "invoice_email": "club@example.be",
        "invoice_clubnr": "601",
        "national_championship_143a": "No",
        "on_fide_calendar": "Yes",
        "tournament_report": "All rounds in 1 report",
        "tournament_type": "Individual",
        "event_name": "Brussels Open 2027",
        "city": "Brussels",
        "country": "BEL",
        "expected_players": "60",
        "tournament_system": "Swiss",
        "rounds_reported": "7",
        "female_only": "No",
        "start_date": start.isoformat(),
        "end_date": end,
        "title_norms": "No",
        "gm_wgm_norms": "No",
        "chief_arbiter_name": "Arbiter, Chief",
        "chief_arbiter_fide_id": "200000",
        "chief_organizer_name": "Organiser, Chief",
        "chief_organizer_fide_id": "200001",
        "time_control_code": "Standard",
        "time_control_desc": "90min/40moves+30min/end+30sec/move from move 1",
        "all_digital_clocks": "Yes",
        "tiebreak_method": "Buchholz",
        "software": "Swiss Manager",
        "contact_email": "organiser@example.be",
        "communication_language": "en",
        "report_deadline_ack": True,
    }
    r = TestClient(app).post(
        "/api/v1/fide/generate?locale=en", json={"formdata": form}
    )
    assert r.status_code == 200, r.text
    return r.headers["content-disposition"], mails


def test_thirteen_days_ahead_in_brussels_is_late(monkeypatch):
    disposition, mails = _submit(monkeypatch, date(2027, 3, 8), date(2027, 3, 21))
    assert "LATE_Tournament_Registration" in disposition
    assert mails[0].subject.startswith("[LATE REGISTRATION]")


def test_fourteen_days_ahead_in_brussels_is_not_late(monkeypatch):
    disposition, mails = _submit(monkeypatch, date(2027, 3, 7), date(2027, 3, 21))
    assert "LATE_" not in disposition


def _on_the_event_loop():
    import asyncio

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return False
    return True


def test_the_mails_are_sent_off_the_event_loop(monkeypatch):
    # the send blocks; on the event loop it would stall every other request
    seen = []
    _submit(
        monkeypatch,
        date(2027, 3, 1),
        date(2027, 6, 1),
        send=lambda p: seen.append(_on_the_event_loop()),
    )
    assert seen == [False, False, False]
