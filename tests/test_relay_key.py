from reddevil.core import get_settings


def test_the_old_key_is_no_longer_in_the_settings():
    settings = get_settings()
    assert not hasattr(settings, "API_KEY")
