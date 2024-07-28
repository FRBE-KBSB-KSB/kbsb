import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from kbsb.interclubs.registrations import (
    find_icregistration,
    set_icregistration,
    csv_ICenrollments,
)


@patch("kbsb.interclubs.enrollments.DbICEnrollment2425")
@patch("kbsb.interclubs.enrollments.get_interclubenrollments")
@pytest.mark.asyncio
async def test_find_interclubenrollment(
    get_interclubenrollments: AsyncMock,
    DbICEnrollment: MagicMock,
    ic_enrollment_factory,
):
    enr1 = ic_enrollment_factory.build(idclub=123)
    get_interclubenrollments.return_value = [enr1]
    enr2 = await find_icregistration(123)
    assert enr2 == enr1


@patch("kbsb.interclubs.enrollments.DbICEnrollment2425")
@patch("kbsb.interclubs.enrollments.get_club_idclub")
@patch("kbsb.interclubs.enrollments.find_interclubenrollment")
@patch("kbsb.interclubs.enrollments.update_interclubenrollment")
@patch("kbsb.interclubs.enrollments.sendEmail")
@pytest.mark.asyncio
async def test_set_interclubenrollment_existing(
    sendEmail: MagicMock,
    update_interclubenrollment: AsyncMock,
    find_interclubenrollment: AsyncMock,
    get_club_idclub: AsyncMock,
    DbICEnrollment: MagicMock,
    club_factory,
    ic_enrollment_factory,
    ic_enrollment_in_factory,
    settings,
):
    club1 = club_factory.build(idclub=123, federation="F")
    enr1 = ic_enrollment_factory.build(idclub=123, id="id1")
    enr2 = ic_enrollment_factory.build(idclub=123)
    enr_in1 = ic_enrollment_in_factory.build()
    get_club_idclub.return_value = club1
    find_interclubenrollment.return_value = enr1
    update_interclubenrollment.return_value = enr2
    enr3 = await set_icregistration(456, enr_in1)
    assert enr3 == enr2
    sendEmail.assert_called()


@patch("kbsb.interclubs.enrollments.DbICEnrollment2425")
@patch("kbsb.interclubs.enrollments.get_club_idclub")
@patch("kbsb.interclubs.enrollments.find_interclubenrollment")
@patch("kbsb.interclubs.enrollments.create_interclubenrollment")
@patch("kbsb.interclubs.enrollments.get_interclubenrollment")
@patch("kbsb.interclubs.enrollments.sendEmail")
@pytest.mark.asyncio
async def test_set_interclubenrollment_new(
    sendEmail: MagicMock,
    get_interclubenrollment: AsyncMock,
    create_interclubenrollment: AsyncMock,
    find_interclubenrollment: AsyncMock,
    get_club_idclub: AsyncMock,
    DbICEnrollment: MagicMock,
    club_factory,
    ic_enrollment_factory,
    ic_enrollment_in_factory,
    settings,
):
    club1 = club_factory.build(idclub=123, federation="F")
    enr2 = ic_enrollment_factory.build(idclub=123)
    enr_in1 = ic_enrollment_in_factory.build()
    get_club_idclub.return_value = club1
    find_interclubenrollment.return_value = None
    get_interclubenrollment.return_value = enr2
    create_interclubenrollment.return_value = 123
    enr3 = await set_icregistration(456, enr_in1)
    assert enr3 == enr2
    sendEmail.assert_called()


@patch("kbsb.interclubs.enrollments.DbICEnrollment2425")
@pytest.mark.asyncio
async def test_csv_ICenrollments(
    DbICEnrollment: MagicMock,
    ic_enrollment_out_factory,
):
    enrs = ic_enrollment_out_factory.batch(size=2)
    DbICEnrollment.find_multiple = AsyncMock(return_value=enrs)
    output = await csv_ICenrollments()
    lines = output.split("\r\n")
    assert len(lines) == 4  # count the last \n
    fields = lines[0].split(",")
    assert "idclub" in fields
    assert "wishes.grouping" in fields
