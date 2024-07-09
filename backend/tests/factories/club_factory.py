from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture
from kbsb.club import (
    Club,
)


@register_fixture
class ClubFactory(ModelFactory[Club]):
    __model__ = Club
