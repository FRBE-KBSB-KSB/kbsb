# helpers for values written into spreadsheet (XLSX/CSV) exports

import re

# a leading character a spreadsheet may read as the start of a formula
_FORMULA_START = ("=", "+", "-", "@", "\t", "\r")

# a leading + or - followed only by these is a number or a phone number,
# e.g. "+32 478 12 34 56"; with no letters or cell references it cannot call
# anything, so it is left as it is
_NUMBERLIKE = re.compile(r"[+\-][0-9 ()./+\-]*")


def safe_cell(value):
    """
    a value made safe for a spreadsheet cell: a string that would be read as
    a formula gets a leading single quote (the OWASP CSV injection
    mitigation), a dict or list (openpyxl refuses those) becomes its text,
    anything else (numbers, dates, None) is returned unchanged
    """
    if isinstance(value, (dict, list, tuple, set)):
        value = str(value)
    if (
        isinstance(value, str)
        and value.startswith(_FORMULA_START)
        and not _NUMBERLIKE.fullmatch(value)
    ):
        return "'" + value
    return value


# line breaks and tabs that may not open a text cell
_LEADING_CONTROL = "\t\r\n"


def write_text(cell, value):
    """
    writes a value into an openpyxl cell so that it can never be a formula:
    a string is stored as a literal text cell, byte for byte the same as what
    was given (no leading quote as safe_cell adds), except that a leading tab
    or line break is dropped; openpyxl would otherwise turn any string that
    starts with "=" into a formula. Numbers, booleans and None are stored as
    they are, a dict or list as its text.
    """
    if isinstance(value, (dict, list, tuple, set)):
        value = str(value)
    if isinstance(value, str):
        value = value.lstrip(_LEADING_CONTROL)
        cell.value = value
        # set after the value: assigning "=..." makes openpyxl mark the cell
        # as a formula, this marks it as text again
        cell.data_type = "s"
    else:
        cell.value = value
    return cell
