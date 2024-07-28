import pytest

from unittest.mock import AsyncMock, patch, MagicMock

from kbsb.interclubs.icclubs import (
    create_icclub,
    get_icclub,
    ICClubDB,
)


@patch("kbsb.interclubs.icclubs.DbICClub")
@pytest.mark.asyncio
async def test_create_icclub(
    DbICClub: MagicMock,
    ic_club_db_factory,
):
    icc = ic_club_db_factory.build()
    DbICClub.add = AsyncMock(return_value="123")
    id = await create_icclub(icc)
    assert id == "123"


@patch("kbsb.interclubs.icclubs.DbICClub")
@pytest.mark.asyncio
async def test_get_icclub(
    DbICClub: MagicMock,
    ic_club_db_factory,
):
    icc = ic_club_db_factory.build(idclub=17)
    DbICClub.find_single = AsyncMock(return_value=icc)
    c = await get_icclub({"idclub": 15})
    assert isinstance(c, ICClubDB)
    assert c.idclub == 17


@patch("kbsb.interclubs.icclubs.DbICClub")
@patch("kbsb.interclubs.icclubs.get_icclub")
@patch("kbsb.interclubs.icclubs.find_icregistration")
@patch("kbsb.interclubs.icclubs.update_interclubenrollment")
@patch("kbsb.interclubs.icclubs.sendEmail")
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


# @patch("kbsb.interclubs.icclubs.DbICEnrollment2425")
# @patch("kbsb.interclubs.icclubs.get_club_idclub")
# @patch("kbsb.interclubs.icclubs.find_interclubenrollment")
# @patch("kbsb.interclubs.icclubs.create_interclubenrollment")
# @patch("kbsb.interclubs.icclubs.get_interclubenrollment")
# @patch("kbsb.interclubs.icclubs.sendEmail")
# @pytest.mark.asyncio
# async def test_set_interclubenrollment_new(
#     sendEmail: MagicMock,
#     get_interclubenrollment: AsyncMock,
#     create_interclubenrollment: AsyncMock,
#     find_interclubenrollment: AsyncMock,
#     get_club_idclub: AsyncMock,
#     DbICEnrollment: MagicMock,
#     club_factory,
#     ic_enrollment_factory,
#     ic_enrollment_in_factory,
#     settings,
# ):
#     club1 = club_factory.build(idclub=123, federation="F")
#     enr2 = ic_enrollment_factory.build(idclub=123)
#     enr_in1 = ic_enrollment_in_factory.build()
#     get_club_idclub.return_value = club1
#     find_interclubenrollment.return_value = None
#     get_interclubenrollment.return_value = enr2
#     create_interclubenrollment.return_value = 123
#     enr3 = await set_icregistration(456, enr_in1)
#     assert enr3 == enr2
#     sendEmail.assert_called()


# @patch("kbsb.interclubs.icclubs.DbICEnrollment2425")
# @pytest.mark.asyncio
# async def test_csv_ICicclubs(
#     DbICEnrollment: MagicMock,
#     ic_enrollment_out_factory,
# ):
#     enrs = ic_enrollment_out_factory.batch(size=2)
#     DbICEnrollment.find_multiple = AsyncMock(return_value=enrs)
#     output = await csv_ICicclubs()
#     lines = output.split("\r\n")
#     assert len(lines) == 4  # count the last \n
#     fields = lines[0].split(",")
#     assert "idclub" in fields
#     assert "wishes.grouping" in fields
