from returns.maybe import Nothing, Some


def test_maybe_filter():
    """Ensures that .filter works correctly."""
    def factory(argument):
        return argument % 2 == 0

    assert Some(5).filter(factory) == Nothing
    assert Some(6).filter(factory) == Some(6)
    assert Nothing.filter(factory) == Nothing
