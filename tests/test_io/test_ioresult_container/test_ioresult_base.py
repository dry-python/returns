from returns.io import IOFailure, IOSuccess


def test_ioresult_types():
    """Ensures that Result has two types inside a class."""
    assert isinstance(IOSuccess, type)
    assert isinstance(IOFailure, type)
