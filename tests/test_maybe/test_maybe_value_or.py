from returns.maybe import Nothing, Some


def test_some_value():
    """Ensures that value is fetch correctly from the Some."""
    assert Some(5).value_or(None) == 5


def test_nothing_value():
    """Ensures that value is fetch correctly from the Nothing."""
    assert Nothing.value_or(default_value=1) == 1
