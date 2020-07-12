from returns.io import IOFailure, IOSuccess


def test_map_iosuccess():
    """Ensures that IOSuccess is mappable."""
    assert IOSuccess(5).map(str) == IOSuccess('5')


def test_alt_iofailure():
    """Ensures that IOFailure is mappable."""
    assert IOFailure(5).map(str) == IOFailure(5)
    assert IOFailure(5).alt(str) == IOFailure('5')


def test_alt_iosuccess():
    """Ensures that IOSuccess.alt is NoOp."""
    assert IOSuccess(5).alt(str) == IOSuccess(5)
