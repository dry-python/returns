from returns.maybe import Nothing, Some


def test_map_some():
    """Ensures that map works for Some container."""
    assert Some(5).map(str) == Some('5')
    assert Some(5).map(lambda num: None) == Nothing


def test_map_nothing():
    """Ensures that map works for Nothing container."""
    assert Nothing.map(str) == Nothing
