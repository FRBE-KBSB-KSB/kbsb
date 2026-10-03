import json
import re
import calendar
from pathlib import Path
from io import BytesIO
from datetime import date, datetime, timedelta
import logging
import base64
import html
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from openpyxl import load_workbook

from zerotwocloud.mail import MailAttachment, MailParams
from zerotwocloud.mail import get_setting as get_mail_setting
from zerotwocloud.mail.mail import sendEmailMessage

from kbsb.core.cells import write_text
from kbsb.fide import ratelimit, turnstile

logger = logging.getLogger(__name__)

# The form's mail goes through zerotwocloud.mail: sent as noreply-jorian@ over
# keyless Gmail delegation, and a failed send raises. It matters here more than
# anywhere. A registration exists only as the mail to fide@, and the organiser's
# only copy is their confirmation mail: the page does not save the workbook.
# reddevil.mail reported a failed send as sent, so the form's "Failed to send
# registration email" answer below could never appear.
FIDE_MAILBOX = "fide@frbe-kbsb-ksb.be"
# Read by the dataplatform every 30 minutes; it queues the workbook for processing.
AUTORATING_MAILBOX = "autoratingfide@frbe-kbsb-ksb.be"
INTERNAL_TEST_ADDRESS = "jorian.burssens@frbe-kbsb-ksb.be"

# One plain address: the invoice and contact e-mails become mail headers (To,
# Reply-To), so no line breaks or spaces, and no comma, semicolon or angle
# bracket that would turn one address into several recipients.
EMAIL_RE = re.compile(r"[^\s@,;:<>()\[\]\\\"']+@[^\s@,;:<>()\[\]\\\"']+\.[^\s@,;:<>()\[\]\\\"']+")

router = APIRouter(prefix="/api/v1/fide", tags=["fide"])

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "template_fide_form.xlsx"
TRANSLATIONS_PATH = BASE_DIR / "translations.json"

with open(TRANSLATIONS_PATH, "r", encoding="utf-8") as f:
    TRANSLATIONS = json.load(f)

FIDE_FIELDS = [
    ("fide_laws_followed", "Will FIDE Laws be followed?"),
    ("national_championship_143a", "National Championship 1.43a"),
    ("on_fide_calendar", "Is information put on FIDE Calendar?"),
    ("tournament_report", "Tournament report"),
    ("tournament_type", "Tournament type"),
    ("event_name", "Event Name"),
    ("city", "City"),
    ("country", "Country"),
    ("expected_players", "Expected number of players"),
    ("tournament_system", "Tournament system"),
    ("rounds_reported", "Number of Rounds reported"),
    ("multiple_round_days", "Number of multiple round days"),
    ("female_only", "Female players only"),
    ("start_date", "Start Date (YYYY-MM-DD)"),
    ("end_date", "End Date (YYYY-MM-DD)"),
    ("title_norms", "Title Norms available"),
    ("gm_wgm_norms", "GM/WGM Norms available"),
    ("chief_arbiter_name", "Chief Arbiter Name"),
    ("chief_arbiter_fide_id", "Chief Arbiter FIDE-ID"),
    ("dep_chief_arbiter1_name", "Deputy Chief Arbiter 1 Name"),
    ("dep_chief_arbiter1_fide_id", "Deputy Chief Arbiter 1 FIDE-ID"),
    ("dep_chief_arbiter2_name", "Deputy Chief Arbiter 2 Name"),
    ("dep_chief_arbiter2_fide_id", "Deputy Chief Arbiter 2 FIDE-ID"),
    ("kind_of_arbiters", "Kind of Arbiters"),
    ("arbiter1_name", "Arbiter 1 Name"),
    ("arbiter1_fide_id", "Arbiter 1 FIDE-ID"),
    ("arbiter2_name", "Arbiter 2 Name"),
    ("arbiter2_fide_id", "Arbiter 2 FIDE-ID"),
    ("arbiter3_name", "Arbiter 3 Name"),
    ("arbiter3_fide_id", "Arbiter 3 FIDE-ID"),
    ("arbiter4_name", "Arbiter 4 Name"),
    ("arbiter4_fide_id", "Arbiter 4 FIDE-ID"),
    ("chief_organizer_name", "Chief Organizer Name"),
    ("chief_organizer_fide_id", "Chief Organizer FIDE-ID"),
    ("organizer1_name", "Organizer 1 Name"),
    ("organizer1_fide_id", "Organizer 1 FIDE-ID"),
    ("organizer2_name", "Organizer 2 Name"),
    ("organizer2_fide_id", "Organizer 2 FIDE-ID"),
    ("organizer3_name", "Organizer 3 Name"),
    ("organizer3_fide_id", "Organizer 3 FIDE-ID"),
    ("time_control_code", "Time Control"),
    ("time_control_desc", "Time Control Description"),
    ("timectl_other_desc", "Time Control Description if it is not listed"),
    ("timectl1_moves", "Moves to first time control"),
    ("timectl1_minutes", "Minutes to first time control"),
    ("timectl1_inc_type", "Increment/Delay (1st control)"),
    ("timectl1_inc_seconds", "Seconds of Increment/Delay (1st control)"),
    ("timectl2_moves", "Moves to second time control"),
    ("timectl2_minutes", "Minutes to second time control"),
    ("timectl2_inc_type", "Increment/Delay (2nd control)"),
    ("timectl2_inc_seconds", "Seconds of Increment/Delay (2nd control)"),
    ("timectl_final_minutes", "Minutes for final session"),
    ("timectl_final_inc_type", "Increment/Delay (final)"),
    ("timectl_final_inc_seconds", "Seconds of Increment/Delay (final)"),
    ("max_rating", "Max Rating"),
    ("age_limit", "Age Limit"),
    ("age_limit_value", "Age Limit Value"),
    ("all_digital_clocks", "All Digital Clocks"),
    ("internet_tx", "Internet Transmission"),
    ("internet_tx_boards", "Enter number of boards"),
    ("tiebreak_method", "Tiebreak Method"),
    ("tiebreak_other", "If Tiebreak Method = 'Other', specify 'Other'"),
    ("software", "Software"),
    ("software_other", "If Software = 'Other', specify 'Other'"),
    ("software_version", "Version Software"),
    ("pgn_provided", "Will PGN be provided?"),
    ("contact_email", "Contact E-mail"),
    ("homepage", "Internet Homepage"),
    ("prize_fund", "Prize Fund"),
    ("remarks", "Remarks"),
    ("communication_language", "Language for communication"),
]

MANDATORY_ALWAYS = [
    "invoice_email",
    "invoice_clubnr",
    "fide_laws_followed",
    "national_championship_143a",
    "on_fide_calendar",
    "tournament_report",
    "tournament_type",
    "event_name",
    "city",
    "country",
    "expected_players",
    "tournament_system",
    "rounds_reported",
    "female_only",
    "start_date",
    "end_date",
    "title_norms",
    "gm_wgm_norms",
    "chief_arbiter_name",
    "chief_arbiter_fide_id",
    "chief_organizer_name",
    "chief_organizer_fide_id",
    "time_control_code",
    "time_control_desc",
    "all_digital_clocks",
    "tiebreak_method",
    "software",
    "contact_email",
]

LOOKUP_DATA = {
    "yes_no": ["Yes", "No"],
    "age_limit_options": ["None", "Under", "Over"],
    "inc_delay_options": ["Increment", "Delay"],
    "tiebreak_options": [],
    "software_options": [],
    "tournament_report_options": [],
    "kind_of_arbiters_options": [],
    "tournament_system_options": [],
    "fide_people": {},
    "fide_names": [],
    "time_control_types": [],
    "time_control_desc": {},
}


def load_lookup_values():
    global LOOKUP_DATA
    if not TEMPLATE_PATH.exists():
        logger.error(f"Template path not found: {TEMPLATE_PATH}")
        return

    wb = load_workbook(TEMPLATE_PATH, data_only=True)

    if "Tiebreak_Method" in wb.sheetnames:
        ws_tb = wb["Tiebreak_Method"]
        LOOKUP_DATA["tiebreak_options"] = [c.value for c in ws_tb["A"] if c.value]

    if "Software" in wb.sheetnames:
        ws_sw = wb["Software"]
        opts = [c.value for c in ws_sw["A"] if c.value]
        if "Swar" not in opts:
            if "Other" in opts:
                idx = opts.index("Other")
                opts.insert(idx, "Swar")
            else:
                opts.append("Swar")
        LOOKUP_DATA["software_options"] = opts

    if "Tournament_Report" in wb.sheetnames:
        ws_tr = wb["Tournament_Report"]
        LOOKUP_DATA["tournament_report_options"] = [
            c.value for c in ws_tr["A"] if c.value
        ]

    if "Kind_of_Arbiters" in wb.sheetnames:
        ws_ka = wb["Kind_of_Arbiters"]
        LOOKUP_DATA["kind_of_arbiters_options"] = [
            c.value for c in ws_ka["A"] if c.value
        ]

    if "Tournament_System" in wb.sheetnames:
        ws_ts = wb["Tournament_System"]
        LOOKUP_DATA["tournament_system_options"] = [
            c.value for c in ws_ts["A"] if c.value
        ]

    if "FIDE_ID" in wb.sheetnames:
        ws_id = wb["FIDE_ID"]
        for row in ws_id.iter_rows(min_row=2, max_col=3, values_only=True):
            name, fide_id, license_flag = row
            if not name:
                continue
            LOOKUP_DATA["fide_people"][name] = {
                "id": fide_id if fide_id is not None else "",
                "license": (license_flag or "").strip(),
            }
            LOOKUP_DATA["fide_names"].append(name)

    if "Time_Control" in wb.sheetnames:
        ws_tc = wb["Time_Control"]
        header_row = [c.value for c in ws_tc[1]]
        col_letters = ["B", "C", "D"]
        types = []
        for idx, col in enumerate(col_letters, start=1):
            if idx < len(header_row):
                label = header_row[idx]
                if label and label not in types:
                    types.append(label)
        LOOKUP_DATA["time_control_types"] = types
        for t, col in zip(types, col_letters):
            values = [c.value for c in ws_tc[col][1:] if c.value]
            if t == "Standard" and "45min/end+30sec/move from move 1" not in values:
                values.append("45min/end+30sec/move from move 1")
            LOOKUP_DATA["time_control_desc"][t] = values


load_lookup_values()
turnstile.log_status()


@router.get("/form-data")
def get_form_data():
    return {
        "translations": TRANSLATIONS,
        "lookups": LOOKUP_DATA,
        # "" while Turnstile is off: the page then shows no widget
        "turnstile_sitekey": turnstile.sitekey_if_enabled(),
    }


def fill_workbook(form_data):
    # Every value goes in through write_text: the text is typed by whoever
    # fills in the public form, and fide@ and the staff open this workbook in
    # Excel, so a value starting with "=" must stay text, never a formula
    # (SEC-40). The text itself is kept as typed: the dataplatform reads these
    # cells. The template's own formulas, in cells not written here, stay.
    wb = load_workbook(TEMPLATE_PATH)
    ws = wb["FIDE Registration Form"]

    write_text(ws["B7"], form_data.get("invoice_email", ""))
    write_text(ws["B8"], form_data.get("invoice_clubnr", ""))

    start_row = 10
    lang_labels = {
        "nl": "Nederlands (NL)",
        "fr": "Français (FR)",
        "de": "Deutsch (DE)",
        "en": "English (EN)",
    }
    for index, (field_key, _label) in enumerate(FIDE_FIELDS):
        if field_key == "multiple_round_days":
            val = ""
        else:
            val = form_data.get(field_key, "")
            if field_key == "communication_language" and val in lang_labels:
                val = lang_labels[val]
        write_text(ws[f"B{start_row + index}"], val)

    if (
        form_data.get("tournament_report") == "New long tournament"
        and "Rounds_Long_Tournament" in wb.sheetnames
    ):
        ws_rounds = wb["Rounds_Long_Tournament"]
        write_text(ws_rounds["B1"], form_data.get("event_name", ""))
        # D1 is free in the template, so the optional end date gets its own
        # labelled column next to the report number.
        write_text(ws_rounds["D1"], "End Date (optional)")
        for r in range(2, 150):
            ws_rounds[f"B{r}"] = None
            ws_rounds[f"C{r}"] = None
            ws_rounds[f"D{r}"] = None
            if r > 12:
                ws_rounds[f"A{r}"] = None
        try:
            n_rounds = int(form_data.get("rounds_reported", 0))
        except ValueError:
            n_rounds = 0

        for i in range(1, n_rounds + 1):
            row = i + 1
            write_text(ws_rounds[f"A{row}"], f"Round {i} Date")
            write_text(ws_rounds[f"B{row}"], form_data.get(f"round{i}_date", ""))
            write_text(ws_rounds[f"C{row}"], form_data.get(f"round{i}_report", ""))
            # A one day round leaves D empty, which is the normal case.
            end_date = (form_data.get(f"round{i}_end_date") or "").strip()
            write_text(ws_rounds[f"D{row}"], end_date or None)

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def parse_int(value, field_label, errors, lang, min_value=None, max_value=None):
    t_msg = TRANSLATIONS.get(lang, TRANSLATIONS["en"])["messages"]
    if value is None or value == "":
        return None
    try:
        iv = int(value)
    except ValueError:
        logger.error(f"{field_label} must be an integer")
        errors.append(f"{field_label} {t_msg['field_must_be_integer']}")
        return None
    if min_value is not None and iv < min_value:
        logger.error(f"{field_label} must be at least {min}")
        errors.append(
            f"{field_label} {t_msg['field_must_be_at_least'].replace('{min}', str(min_value))}"
        )
    if max_value is not None and iv > max_value:
        logger.error(f"{field_label} must be at most {max}")
        errors.append(
            f"{field_label} {t_msg['field_must_be_at_most'].replace('{max}', str(max_value))}"
        )
    return iv


ROUND_MAX_DAYS = 7


def round_span_errors(i, start, end, next_start, rounds, t_msg):
    """
    A round with an end date: same FIDE rating period, at most a week, and
    ending before the next round starts. Dates are YYYY-MM-DD strings.
    """

    def fill(key, **extra):
        msg = t_msg[key].replace("{num}", str(i)).replace("{start}", start).replace("{end}", end)
        for k, v in extra.items():
            msg = msg.replace("{" + k + "}", str(v))
        return msg

    p1, p2 = get_fide_period(start), get_fide_period(end)
    if p1 and p2 and p1 != p2:
        return [fill("round_end_date_period_error")]
    try:
        days = (
            datetime.strptime(end, "%Y-%m-%d") - datetime.strptime(start, "%Y-%m-%d")
        ).days
    except ValueError:
        return []
    if days > ROUND_MAX_DAYS:
        return [fill("round_end_date_too_long", days=days)]
    if next_start and i < rounds and end > str(next_start):
        return [fill("round_end_date_overlap_error", next=i + 1, next_start=next_start)]
    return []


def get_fide_period(date_str):
    if not date_str:
        return None
    try:
        parts = [int(p) for p in str(date_str).split("-")]
        if len(parts) != 3:
            return None
        year, month, day = parts
        _, last_day = calendar.monthrange(year, month)
        if day >= last_day - 1:
            return f"{year}-{month:02d}-late"
        return f"{year}-{month:02d}"
    except Exception:
        return None


# KBSB rule: the report reaches the KBSB within 4 days after its end date (for
# a New long tournament, the end of the report's last round: its end date,
# else its date). Day x-1 at 12:00, x the last day of the month, is the last
# chance for that month's FIDE list. An end date from x-6 to x-2 is the
# critical window: 4 days would be too late, so the form warns and asks for a
# tick. The last two days of a month are FIDE's transition period
# (get_fide_period): not critical, and the report counts for the next month's
# list, so its last chance is day x-1 of the next month. Mirrors
# getReportDeadline in fide_registration.vue.
REPORT_DAYS = 4

MONTH_NAMES = {
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
    "nl": ["januari", "februari", "maart", "april", "mei", "juni", "juli",
           "augustus", "september", "oktober", "november", "december"],
    "fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
           "août", "septembre", "octobre", "novembre", "décembre"],
}
LIST_AND = {"en": "and", "nl": "en", "fr": "et"}


def get_report_deadline(date_str):
    """
    For an end date (YYYY-MM-DD): the date the report is expected by, the last
    chance (day x-1 of the month whose FIDE list it counts for, the report due
    at 12:00), whether the end date is in the critical window, and then the
    cutoff (the last chance again). None when the date is not valid.
    """
    try:
        end = datetime.strptime(str(date_str or "").strip(), "%Y-%m-%d").date()
    except ValueError:
        return None
    _, last_day = calendar.monthrange(end.year, end.month)
    critical = last_day - 6 <= end.day <= last_day - 2
    if end.day >= last_day - 1:
        # transition period: the next month's list
        year, month = (end.year + 1, 1) if end.month == 12 else (end.year, end.month + 1)
        last_chance = date(year, month, calendar.monthrange(year, month)[1] - 1)
    else:
        last_chance = end.replace(day=last_day - 1)
    return {
        "end": end,
        "expected": end + timedelta(days=REPORT_DAYS),
        "last_chance": last_chance,
        "critical": critical,
        "cutoff": last_chance if critical else None,
    }


def report_groups(form):
    """
    The reports of the tournament, in order, as dicts with the report number,
    its rounds and its end (YYYY-MM-DD). A New long tournament groups its
    rounds the way recalculateReportNumbers in fide_registration.vue does: one
    report per FIDE rating period of the round dates, or one per round when
    report_per_round is ticked. The report's last round decides its deadline.
    Any other tournament is one report ending on the end date (number and
    rounds None).
    """
    if form.get("tournament_report") != "New long tournament":
        end = (form.get("end_date") or "").strip()
        return [{"num": None, "rounds": None, "end": end}] if end else []
    try:
        n = int(form.get("rounds_reported") or 0)
    except ValueError:
        n = 0
    per_round = is_ticked(form.get("report_per_round"))
    groups = {}
    for i in range(1, n + 1):
        start = (form.get(f"round{i}_date") or "").strip()
        period = get_fide_period(start)
        if not period:
            continue
        end = (form.get(f"round{i}_end_date") or "").strip() or start
        group = groups.setdefault(i if per_round else period, {"rounds": [], "end": ""})
        group["rounds"].append(i)
        group["end"] = max(group["end"], end)
    # Period keys sort like the form sorts them: "2026-09" < "2026-09-late" < "2026-10".
    return [
        {"num": num, **groups[key]} for num, key in enumerate(sorted(groups), start=1)
    ]


def report_deadlines(form):
    """The reports with their deadline (get_report_deadline of their end)."""
    reports = []
    for group in report_groups(form):
        deadline = get_report_deadline(group["end"])
        if deadline:
            reports.append({**group, "deadline": deadline})
    return reports


def format_date(d, lang, year=True):
    """5 October 2026 / 5 oktober 2026 / 5 octobre 2026, as the form shows it."""
    months = MONTH_NAMES.get(lang, MONTH_NAMES["en"])
    text = f"{d.day} {months[d.month - 1]}"
    return f"{text} {d.year}" if year else text


def format_list(texts, lang):
    """A, B and C in the given language, like Intl.ListFormat on the form."""
    texts = list(texts)
    if len(texts) < 2:
        return "".join(texts)
    return f"{', '.join(texts[:-1])} {LIST_AND.get(lang, 'and')} {texts[-1]}"


def format_rounds(rounds, lang):
    """round 5 / rounds 7, 8 and 9, in the given language."""
    t_msg = TRANSLATIONS.get(lang, TRANSLATIONS["en"])["messages"]
    key = "report_rounds_one" if len(rounds) == 1 else "report_rounds_many"
    return t_msg[key].replace("{rounds}", format_list((str(r) for r in rounds), lang))


def fill_cutoff(template, cutoff, lang):
    """Fills {deadline}, {month} and {of_month} (French: de/d' + month)."""
    month = MONTH_NAMES.get(lang, MONTH_NAMES["en"])[cutoff.month - 1]
    of_month = f"d'{month}" if month[0] in "aeiou" else f"de {month}"
    return (
        template.replace("{deadline}", format_date(cutoff, lang, year=False))
        .replace("{month}", month)
        .replace("{of_month}", of_month)
    )


def fill_report(template, report, lang):
    """Fills {num}, {rounds} and {date} (the expected date) for a report."""
    text = template.replace("{date}", format_date(report["deadline"]["expected"], lang))
    if report["num"] is not None:
        text = text.replace("{num}", str(report["num"])).replace(
            "{rounds}", format_rounds(report["rounds"], lang)
        )
    return text


def report_ack_text(reports, lang):
    """
    The reports the tick is for (those in the critical window), as the form's
    checkbox and the error for a missing tick list them.
    """
    t_msg = TRANSLATIONS.get(lang, TRANSLATIONS["en"])["messages"]
    items = []
    for report in reports:
        key = "report_ack_item_tournament" if report["num"] is None else "report_ack_item_report"
        item = t_msg[key].replace("{cutoff}", format_date(report["deadline"]["cutoff"], lang))
        items.append(fill_report(item, report, lang))
    return format_list(items, lang)


def is_ticked(value):
    return value is True or str(value).strip().lower() in ("true", "1", "yes", "on")


def report_deadline_mail(form, lang):
    """
    The deadline part of the confirmation mail, per report: its rounds, the
    date it is expected by, the last chance for its rating list and, when its
    last round ends in the critical window, the warning.
    """
    t_msg = TRANSLATIONS.get(lang, TRANSLATIONS["en"])["messages"]
    warn_style = "color: #b45309; font-weight: bold;"
    reports = report_deadlines(form)
    if not reports:
        return ""

    if reports[0]["num"] is None:
        report = reports[0]
        deadline = report["deadline"]
        text = (
            t_msg["mail_report_deadline_tournament"]
            .replace("{end}", format_date(deadline["end"], lang))
            .replace("{date}", format_date(deadline["expected"], lang))
        )
        text += " " + fill_cutoff(t_msg["report_last_chance"], deadline["last_chance"], lang)
        html = f"<p>{text}</p>"
        if deadline["critical"]:
            text = fill_cutoff(t_msg["report_deadline_critical_tournament"], deadline["cutoff"], lang)
            html += f'<p style="{warn_style}">{text}</p>'
        return html

    items = []
    for report in reports:
        deadline = report["deadline"]
        item = fill_report(t_msg["mail_report_deadline_report"], report, lang).replace(
            "{end}", format_date(deadline["end"], lang)
        )
        item += " " + fill_cutoff(t_msg["report_last_chance"], deadline["last_chance"], lang)
        if deadline["critical"]:
            text = fill_report(t_msg["report_deadline_critical_report"], report, lang)
            text = fill_cutoff(text, deadline["cutoff"], lang)
            item += f'<br><span style="{warn_style}">{text}</span>'
        items.append(f"<li>{item}</li>")
    return f"<p>{t_msg['mail_report_deadline_intro']}</p><ul>{''.join(items)}</ul>"


def validate_form(form, lang):
    errors = []
    trans = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    t_msg = trans["messages"]
    t_fields = trans["fields"]

    if not form.get("country"):
        form["country"] = "BEL"

    for key in MANDATORY_ALWAYS:
        if not form.get(key):
            label = t_fields.get(key, key)
            logger.error(f"value required for {label}")
            errors.append(f"{label} {t_msg['value_required']}")

    start_date = form.get("start_date")
    end_date = form.get("end_date")
    if start_date and end_date:
        if end_date < start_date:
            logger.error(f"End date {end_date} cannot be earlier than start date {start_date}")
            errors.append(t_msg.get("end_date_order_error", "End Date cannot be earlier than Start Date."))
        elif form.get("tournament_report") == "All rounds in 1 report":
            p_start = get_fide_period(start_date)
            p_end = get_fide_period(end_date)
            if p_start and p_end and p_start != p_end:
                logger.error(f"Dates {start_date} ({p_start}) and {end_date} ({p_end}) span multiple FIDE periods for 1 report")
                errors.append(t_msg.get("all_rounds_one_report_period_error", "Dates span multiple FIDE rating periods. For tournaments across multiple months or end-of-month dates, please select 'New long tournament'."))

    for key in ("invoice_email", "contact_email"):
        value = form.get(key)
        if not value:
            continue
        if not isinstance(value, str) or not (
            value.strip() == "JORIAN.INTERNAL" or EMAIL_RE.fullmatch(value.strip())
        ):
            logger.error(f"{key} is not a valid e-mail address")
            errors.append(f"{t_fields.get(key, key)} {t_msg['invalid_email']}")

    event_name = form.get("event_name", "")
    if event_name and not re.fullmatch(r"[A-Za-z0-9 -]+", event_name):
        logger.error(
            f"Event name: {event_name} can only contain letters, number, hyphens or spaces"
        )
        errors.append(
            f"{t_fields.get('event_name', 'Event Name')} {t_msg['only_letters_numbers_spaces']}"
        )

    if form.get("fide_laws_followed") != "Yes":
        logger.error("Fide laws must be followed")
        errors.append(t_msg["fide_laws_error"])

    if form.get("tiebreak_method") == "Other" and not form.get("tiebreak_other"):
        logger.error("Cannot have empty tiebreak other")
        errors.append(
            f"{t_fields.get('tiebreak_other', 'tiebreak_other')} {t_msg['value_required']}"
        )

    if form.get("software") == "Other" and not form.get("software_other"):
        logger.error("Cannot have empty software other")
        errors.append(
            f"{t_fields.get('software_other', 'software_other')} {t_msg['value_required']}"
        )

    rounds_reported = parse_int(
        form.get("rounds_reported"),
        t_fields.get("rounds_reported", "Number of Rounds reported"),
        errors,
        lang,
        min_value=0,
        max_value=100,
    )
    parse_int(
        form.get("expected_players"),
        t_fields.get("expected_players", "Expected number of players"),
        errors,
        lang,
        min_value=1,
        max_value=2500,
    )

    age_limit = form.get("age_limit")
    age_limit_value = form.get("age_limit_value")
    if age_limit and age_limit != "None":
        if not age_limit_value:
            dep_msg = (
                t_msg["value_required_for"]
                .replace("{dependency}", t_fields.get("age_limit", "Age Limit"))
                .replace("{value}", age_limit)
            )
            logger.error("Age limit value is required")
            errors.append(
                f"{t_fields.get('age_limit_value', 'Age Limit Value')} {dep_msg}"
            )
        else:
            parse_int(
                age_limit_value,
                t_fields.get("age_limit_value", "Age Limit Value"),
                errors,
                lang,
                min_value=0,
            )

    parse_int(
        form.get("max_rating"),
        t_fields.get("max_rating", "Max Rating"),
        errors,
        lang,
        min_value=0,
    )

    if form.get("internet_tx") == "Yes":
        boards = form.get("internet_tx_boards")
        if not boards:
            dep_msg = (
                t_msg["value_required_for"]
                .replace(
                    "{dependency}", t_fields.get("internet_tx", "Internet Transmission")
                )
                .replace("{value}", "Yes")
            )
            logger.error(f"{boards} is required")
            errors.append(
                f"{t_fields.get('internet_tx_boards', 'Enter number of boards')} {dep_msg}"
            )
        else:
            parse_int(
                boards,
                t_fields.get("internet_tx_boards", "Enter number of boards"),
                errors,
                lang,
                min_value=1,
            )

    if form.get("time_control_desc") == "Other":
        if not form.get("timectl_other_desc"):
            dep_msg = (
                t_msg["value_required_for"]
                .replace(
                    "{dependency}",
                    t_fields.get("time_control_desc", "Time Control Description"),
                )
                .replace("{value}", "Other")
            )
            logger.error("Time control description is required")
            errors.append(
                f"{t_fields.get('timectl_other_desc', 'Time Control Description if not listed')} {dep_msg}"
            )
        tc_fields_required = [
            (
                "timectl1_moves",
                t_fields.get("timectl1_moves", "Moves to first time control"),
            ),
            (
                "timectl1_minutes",
                t_fields.get("timectl1_minutes", "Minutes to first time control"),
            ),
            (
                "timectl1_inc_seconds",
                t_fields.get(
                    "timectl1_inc_seconds", "Seconds of Increment/Delay (1st control)"
                ),
            ),
        ]
        for key, label in tc_fields_required:
            if not form.get(key):
                dep_msg = (
                    t_msg["value_required_for"]
                    .replace(
                        "{dependency}",
                        t_fields.get("time_control_desc", "Time Control Description"),
                    )
                    .replace("{value}", "Other")
                )
                logger.error(f"Time Control Description: {key} field missing")
                errors.append(f"{label} {dep_msg}")
            else:
                parse_int(form.get(key), label, errors, lang, min_value=0)

        # 2nd and final time controls are optional
        tc_fields_optional = [
            (
                "timectl2_moves",
                t_fields.get("timectl2_moves", "Moves to second time control"),
            ),
            (
                "timectl2_minutes",
                t_fields.get("timectl2_minutes", "Minutes to second time control"),
            ),
            (
                "timectl2_inc_seconds",
                t_fields.get(
                    "timectl2_inc_seconds", "Seconds of Increment/Delay (2nd control)"
                ),
            ),
            (
                "timectl_final_minutes",
                t_fields.get("timectl_final_minutes", "Minutes for final session"),
            ),
            (
                "timectl_final_inc_seconds",
                t_fields.get(
                    "timectl_final_inc_seconds", "Seconds of Increment/Delay (final)"
                ),
            ),
        ]
        for key, label in tc_fields_optional:
            if form.get(key):
                parse_int(form.get(key), label, errors, lang, min_value=0)
        if not form.get("timectl1_inc_type"):
            dep_msg = (
                t_msg["value_required_for"]
                .replace(
                    "{dependency}",
                    t_fields.get("time_control_desc", "Time Control Description"),
                )
                .replace("{value}", "Other")
            )
            errors.append(f"{t_fields.get('timectl1_inc_type', 'timectl1_inc_type')} {dep_msg}")

    if form.get("tournament_report") == "New long tournament":
        n = rounds_reported if rounds_reported is not None else 0
        prev_date = None
        prev_idx = None
        for i in range(1, n + 1):
            date_key = f"round{i}_date"
            report_key = f"round{i}_report"
            end_date_key = f"round{i}_end_date"
            date_val = form.get(date_key)
            # The round end date is optional: absent means a one day round,
            # which keeps older submissions valid.
            end_date_val = (form.get(end_date_key) or "").strip()
            if end_date_val:
                try:
                    datetime.strptime(end_date_val, "%Y-%m-%d")
                except ValueError:
                    logger.error(f"Round {i} end date {end_date_val} is not a valid date")
                    errors.append(
                        t_msg["round_end_date_invalid"].replace("{num}", str(i))
                    )
                else:
                    if date_val and end_date_val < date_val:
                        logger.error(
                            f"Round {i} end date {end_date_val} is earlier than round date {date_val}"
                        )
                        errors.append(
                            t_msg["round_end_date_order_error"].replace("{num}", str(i))
                        )
                    elif date_val:
                        # Same rules as the form: one round played over two
                        # dates, not a window (see fide_registration.vue).
                        errors.extend(
                            round_span_errors(
                                i, date_val, end_date_val, form.get(f"round{i + 1}_date"), n, t_msg
                            )
                        )
            if not date_val:
                errors.append(t_msg["round_date_required"].replace("{num}", str(i)))
            else:
                if prev_date and date_val < prev_date:
                    msg = (
                        t_msg["round_dates_order_error"]
                        .replace("{num}", str(i))
                        .replace("{prev_num}", str(prev_idx))
                    )
                    errors.append(msg)
                prev_date = date_val
                prev_idx = i
            if not form.get(report_key):
                errors.append(t_msg["round_report_required"].replace("{num}", str(i)))
            else:
                parse_int(
                    form.get(report_key),
                    t_msg["round_report_required"].replace("{num}", str(i)),
                    errors,
                    lang,
                    min_value=1,
                )

    # A report whose last round ends in the critical window: the organiser has
    # to tick that it is due by noon on day x-1 (the checkbox above the submit
    # button). An earlier round of the report in the window does not count.
    critical = [r for r in report_deadlines(form) if r["deadline"]["critical"]]
    if critical and not is_ticked(form.get("report_deadline_ack")):
        logger.error(
            f"Report deadline not acknowledged for reports {[(r['num'], r['end']) for r in critical]}"
        )
        errors.append(
            t_msg["report_deadline_ack_required"].replace(
                "{reports}", report_ack_text(critical, lang)
            )
        )

    return errors


def calculate_standard_total_minutes(form: dict) -> float:
    tc_code = form.get("time_control_code")
    if tc_code != "Standard":
        return 0.0

    tc_desc = form.get("time_control_desc", "")
    if tc_desc == "Other":
        try:
            m1 = int(form.get("timectl1_minutes") or 0)
        except ValueError:
            m1 = 0
        try:
            m2 = int(form.get("timectl2_minutes") or 0)
        except ValueError:
            m2 = 0
        try:
            m3 = int(form.get("timectl_final_minutes") or 0)
        except ValueError:
            m3 = 0
        try:
            inc = int(form.get("timectl1_inc_seconds") or 0)
        except ValueError:
            inc = 0
        return float(m1 + m2 + m3 + inc)

    if not tc_desc:
        return 0.0

    total_mins = 0.0
    for match in re.finditer(r"(\d+)min", tc_desc):
        try:
            total_mins += int(match.group(1))
        except ValueError:
            pass

    inc_mins = 0.0
    inc_match = re.search(r"(\d+)sec(?:\s+DELAY)?/move(?: from move (\d+))?", tc_desc)
    if inc_match:
        try:
            sec = int(inc_match.group(1))
            start_move = int(inc_match.group(2)) if inc_match.group(2) else 1
            if start_move == 1:
                inc_mins = float(sec)
            elif start_move < 60:
                inc_mins = (sec * (60 - start_move)) / 60.0
        except ValueError:
            pass

    return total_mins + inc_mins


def normalise_homepage(form):
    """The homepage is optional: empty stays empty, a typed one without a
    scheme gets https://."""
    homepage = (form.get("homepage") or "").strip()
    if homepage and not homepage.lower().startswith(("http://", "https://")):
        homepage = "https://" + homepage
    form["homepage"] = homepage


def refuse(key, status_code, locale):
    """A refused submit, with the translated message of key."""
    t_refusal = TRANSLATIONS.get(locale, TRANSLATIONS["en"])["messages"]
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "errors": [t_refusal[key]]},
        # the page asks for a file, so it cannot read this JSON body; it
        # shows its own translation of this key instead
        headers={
            "X-Fide-Error": key,
            "Access-Control-Expose-Headers": "X-Fide-Error",
        },
    )


@router.post("/generate")
async def generate_fide_form(locale: str, formdata: dict, request: Request):
    locale = locale or "en"
    # Turnstile first, before anything is processed or mailed. A no-op while
    # Turnstile is off (see kbsb.fide.turnstile).
    refusal = await turnstile.check(request, formdata.get("turnstile_token"))
    if refusal:
        return refuse(
            refusal, 503 if refusal == turnstile.MSG_UNAVAILABLE else 400, locale
        )
    form = formdata.get("formdata", {})
    if not TEMPLATE_PATH.exists():
        raise HTTPException(status_code=500, detail="Template not found")

    form["fide_laws_followed"] = "Yes"
    if form.get("software") == "Swar":
        form["software"] = "Other"
        form["software_other"] = "Swar (with JaVaFo)"

    normalise_homepage(form)

    errors = validate_form(form, locale)
    if errors:
        return JSONResponse(
            status_code=400, content={"success": False, "errors": errors}
        )

    # validate_form checked these are single addresses without line breaks:
    # they go into the To and Reply-To headers below
    invoice_email = form.get("invoice_email", "").strip()
    is_internal_test = (invoice_email == "JORIAN.INTERNAL")
    contact_email = form.get("contact_email", "").strip()

    # The confirmation copies go to the addresses typed in the form.
    recipients = []
    if is_internal_test:
        recipients.append(INTERNAL_TEST_ADDRESS)
    else:
        if invoice_email:
            recipients.append(invoice_email)
        if contact_email and contact_email != invoice_email and contact_email != "JORIAN.INTERNAL":
            recipients.append(contact_email)

    # Counted only once the form is valid, since an invalid one mails
    # nothing. Our own test address is not a stranger's inbox, so only the
    # IP limit applies to it.
    limited = await ratelimit.check_and_record(
        turnstile.client_ip(request),
        [r for r in recipients if r != INTERNAL_TEST_ADDRESS],
    )
    if limited:
        return refuse(limited, 429, locale)

    start_date_str = form.get("start_date", "").strip()
    is_late = False
    if start_date_str:
        try:
            start_date_val = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            if (start_date_val - today).days < 14:
                is_late = True
        except Exception:
            pass

    filled = fill_workbook(form)
    event_name = form.get("event_name", "").strip()
    safe_event = re.sub(r"\s+", "_", event_name) or "Unknown"
    filename = f"Tournament_Registration_{safe_event}.xlsx"
    if is_late:
        filename = f"LATE_{filename}"

    # Send email with FIDE registration Excel attachment
    excel_content = filled.getvalue()
    encoded_excel = base64.b64encode(excel_content)

    excel_attachment = MailAttachment(
        filename=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        content_base64=encoded_excel,
    )

    # zerotwocloud.mail only sends as the mailbox it acts as: Gmail would
    # silently rewrite any other From, so it refuses one.
    sender_email = get_mail_setting("EMAIL")["account"]
    club_number = form.get("invoice_clubnr", "N/A")

    # Check FIDE Rating Regulations B.02 Article 1.1 time control vs max rating constraints
    tc_code = form.get("time_control_code")
    total_mins = calculate_standard_total_minutes(form)
    unapproved_key = None

    if tc_code == "Standard" and total_mins > 0:
        max_rating_str = str(form.get("max_rating", "")).strip()
        max_rating_val = None
        if max_rating_str:
            try:
                max_rating_val = int(float(max_rating_str))
            except ValueError:
                pass

        if total_mins < 60:
            unapproved_key = "fide_under_60_email"
        elif total_mins < 90:
            if max_rating_val is None or max_rating_val >= 1800:
                unapproved_key = "fide_under_90_email"
        elif total_mins < 120:
            if max_rating_val is None or max_rating_val >= 2400:
                unapproved_key = "fide_under_120_email"

    is_unapproved = bool(unapproved_key)

    # The mails are written in the language the organiser chose for
    # communication, not in whatever language the page happened to be shown
    # in. The page's own language is only the fallback.
    comm_lang_code = form.get("communication_language") or locale
    mail_lang = comm_lang_code if comm_lang_code in TRANSLATIONS else locale
    t_msg = TRANSLATIONS.get(mail_lang, TRANSLATIONS["en"])["messages"]

    warning_banner = ""
    if is_unapproved:
        default_warn = (
            "WARNING: This tournament uses a standard time control under 60 minutes. This is not rateable under FIDE regulations, and this registration is NOT approved."
            if unapproved_key == "fide_under_60_email"
            else (
                "WARNING: This tournament uses a standard time control under 90 minutes but the Max Rating is either not set or is >= 1800. This is incorrect under FIDE regulations, and this registration is NOT approved."
                if unapproved_key == "fide_under_90_email"
                else "WARNING: This tournament uses a standard time control under 120 minutes but the Max Rating is either not set or is >= 2400. This is incorrect under FIDE regulations, and this registration is NOT approved."
            )
        )
        email_warn_msg = t_msg.get(unapproved_key, default_warn)
        warning_banner = f'<div style="color: #b91c1c; font-weight: bold; border: 2px solid #b91c1c; padding: 1rem; margin-bottom: 1.5rem; background-color: #fef2f2;">{email_warn_msg}</div>'

    late_banner = ""
    if is_late:
        late_banner = '<div style="color: #b91c1c; font-weight: bold; border: 2px solid #b91c1c; padding: 1rem; margin-bottom: 1.5rem; background-color: #fef2f2; font-size: 1.05rem;">WARNING: THIS IS A LATE REGISTRATION (STARTS IN LESS THAN 14 DAYS).</div>'

    mail_subject = f"{event_name} - Fide registration form"
    if is_late:
        mail_subject = f"[LATE REGISTRATION] {mail_subject}"
    if is_unapproved:
        mail_subject = f"[UNAPPROVED] {mail_subject}"

    comm_lang_map = {
        "nl": "Nederlands (NL)",
        "fr": "Français (FR)",
        "de": "Deutsch (DE)",
        "en": "English (EN)",
    }
    comm_lang_display = comm_lang_map.get(comm_lang_code, comm_lang_code.upper() if comm_lang_code else "English (EN)")

    mail_body = f"""
    {warning_banner}
    {late_banner}
    <p>Beste,</p>
    <p>Hierbij vindt u het FIDE-registratieformulier voor het toernooi: <strong>{event_name}</strong>.</p>
    <p><strong>Clubnummer:</strong> {html.escape(str(club_number))}</p>
    <p><strong>Voorkeurstaal communicatie / Langue:</strong> {html.escape(str(comm_lang_display))}</p>
    <br>
    <p>Groetjes!</p>
    """

    fide_receiver = INTERNAL_TEST_ADDRESS if is_internal_test else FIDE_MAILBOX
    # Replying to the registration from the fide@ inbox reaches the organiser.
    organiser_email = (
        contact_email if contact_email and contact_email != "JORIAN.INTERNAL" else invoice_email
    )

    mail_params = MailParams(
        locale=locale,
        receiver=fide_receiver,
        sender=sender_email,
        subject=mail_subject if not is_internal_test else f"[INTERNAL TEST] {mail_subject}",
        template=mail_body,
        attachments=[excel_attachment],
        reply_to=INTERNAL_TEST_ADDRESS if is_internal_test else organiser_email,
        bcc="" if is_internal_test else AUTORATING_MAILBOX,
    )

    try:
        sendEmailMessage(mail_params)
        logger.info(
            f"FIDE Registration email sent to {fide_receiver} from {sender_email}"
        )
    except Exception as e:
        logger.exception(f"Failed to send FIDE registration email to {fide_receiver}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to send registration email. Please try again or contact fide@frbe-kbsb-ksb.be directly."
            }
        )

    # Send confirmation email to invoice_email and contact_email (if provided)
    conf_subject = t_msg.get(
        "conf_subject", "FIDE Registration Confirmation: {event_name}"
    ).replace("{event_name}", event_name)
    conf_body = t_msg.get(
        "conf_body", "<p>Thank you for submitting the FIDE registration form.</p>"
    ).replace("{event_name}", event_name)
    conf_body = conf_body.replace("{report_deadlines}", report_deadline_mail(form, mail_lang))

    if is_unapproved:
        conf_body = warning_banner + conf_body

    failed_confirmations = []
    for recipient in recipients:
        conf_params = MailParams(
            locale=mail_lang,
            receiver=recipient,
            sender=sender_email,
            subject=conf_subject,
            template=conf_body,
            attachments=[excel_attachment],
            reply_to=INTERNAL_TEST_ADDRESS if is_internal_test else FIDE_MAILBOX,
        )
        try:
            sendEmailMessage(conf_params)
            logger.info(
                f"FIDE Registration confirmation email sent from {sender_email}"
            )
        except Exception:
            logger.exception("Failed to send FIDE registration confirmation email")
            failed_confirmations.append(recipient)

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    if failed_confirmations:
        # Still a success: the registration reached fide@. But this confirmation
        # is the organiser's only copy, so the page names the addresses that did
        # not get one. Percent-encoded: organisers type these, and they must not
        # be able to break or add a response header.
        headers["X-Confirmation-Failed"] = quote(", ".join(failed_confirmations))
        headers["Access-Control-Expose-Headers"] = "X-Confirmation-Failed"

    return StreamingResponse(
        iter([filled.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
