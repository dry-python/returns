from returns.maybe import Maybe, Nothing, Some


def test_maybe_new_some():
    """Ensures that `new` works for Some container."""
    assert Maybe.from_value(5) == Some(5)


def test_maybe_new_nothing():
    """Ensures that `new` works for Nothing container."""
    assert Maybe.from_value(None) == Nothing
