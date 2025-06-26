from returns.maybe import Nothing, Some


def test_some_is_true() -> None:
    """Ensures that ``Something(...)`` is ``True`` when treated as a boolean."""
    assert bool(Some(123))
    assert bool(Some('abc'))


def test_nothing_is_false():
    """Ensures that ``Nothing`` is ``False`` when treated as a boolean."""
    assert not bool(Nothing)


def test_some_none_is_true():
    """Ensures that ``Something(None)`` is ``True`` when treated as a boolean.

    See <https://github.com/dry-python/returns/issues/2177> for the discussion
    of this design choice.
    """
    assert bool(Some(None))
    assert bool(Some(Nothing))
