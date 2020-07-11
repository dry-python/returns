from returns.io import IOResult


def test_ioresult_types():
    """Ensures that Result has two types inside a class."""
    assert isinstance(IOResult.success_type, type)
    assert isinstance(IOResult.failure_type, type)
