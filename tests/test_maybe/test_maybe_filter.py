from returns.maybe import Maybe, Nothing, Some


def test_maybe_filter():
    def predicate(value):
        return value % 2 == 0

    assert Some(5).filter(predicate) == Nothing
    assert Some(6).filter(predicate) == Some(6)
    assert Nothing.filter(predicate) == Nothing
