import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from kbsb.interclubs import (
    # create_icregistration,
    find_icregistration,
    set_icregistration,
    # get_icregistran,
    # get_icregistrations,
    # xls_registrations,
)


@patch("kbsb.interclubs.registrations.DbICRegistration")
@patch("kbsb.interclubs.registrations.get_icregistrations")
@pytest.mark.asyncio
async def test_find_icregistration(
    get_icregistrations: AsyncMock,
    DbICRegistration: MagicMock,
    ic_registration_factory,
):
    enr1 = ic_registration_factory.build(idclub=123)
    get_icregistrations.return_value = [enr1]
    enr2 = await find_icregistration(123)
    assert enr2 == enr1


@patch("kbsb.interclubs.registrations.DbICRegistration")
@patch("kbsb.interclubs.registrations.get_club_idclub")
@patch("kbsb.interclubs.registrations.find_icregistration")
@patch("kbsb.interclubs.registrations.update_icregistration")
@pytest.mark.asyncio
async def test_set_interclubregistration_existing(
    update_interclubregistration: AsyncMock,
    find_icregistration: AsyncMock,
    get_club_idclub: AsyncMock,
    DbICRegistration: MagicMock,
    club_factory,
    ic_registration_factory,
    ic_registration_in_factory,
    settings,
):
    club1 = club_factory.build(idclub=123, federation="F")
    enr1 = ic_registration_factory.build(idclub=123, id="id1")
    enr2 = ic_registration_factory.build(idclub=123)
    enr_in1 = ic_registration_in_factory.build()
    get_club_idclub.return_value = club1
    find_icregistration.return_value = enr1
    update_interclubregistration.return_value = enr2
    enr3 = await set_icregistration(456, enr_in1, None)
    assert enr3 == enr2


@patch("kbsb.interclubs.registrations.DbICRegistration")
@patch("kbsb.interclubs.registrations.get_club_idclub")
@patch("kbsb.interclubs.registrations.find_icregistration")
@patch("kbsb.interclubs.registrations.create_icregistration")
@patch("kbsb.interclubs.registrations.get_icregistration")
@pytest.mark.asyncio
async def test_set_interclubregistration_new(
    get_interclubregistration: AsyncMock,
    create_interclubregistration: AsyncMock,
    find_icregistration: AsyncMock,
    get_club_idclub: AsyncMock,
    DbICRegistration: MagicMock,
    club_factory,
    ic_registration_factory,
    ic_registration_in_factory,
    settings,
):
    club1 = club_factory.build(idclub=123, federation="F")
    enr2 = ic_registration_factory.build(idclub=123)
    enr_in1 = ic_registration_in_factory.build()
    get_club_idclub.return_value = club1
    find_icregistration.return_value = None
    get_interclubregistration.return_value = enr2
    create_interclubregistration.return_value = 123
    enr3 = await set_icregistration(456, enr_in1, None)
    assert enr3 == enr2


# @patch("kbsb.interclubs.registrations.DbICRegistration")
# @pytest.mark.asyncio
# async def test_csv_ICregistrations(
#     DbICRegistration: MagicMock,
#     ic_registration_out_factory,
# ):
#     assert True
# enrs = ic_registration_out_factory.batch(size=2)
# DbICRegistration.find_multiple = AsyncMock(return_value=enrs)
# output = await csv_ICregistrations()
# lines = output.split("\r\n")
# assert len(lines) == 4  # count the last \n
# fields = lines[0].split(",")
# assert "idclub" in fields
# assert "wishes.grouping" in fields
