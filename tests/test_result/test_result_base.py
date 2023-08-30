from returns.result import Failure, Success


def test_result_types():
    """Ensures that Result has two types inside a class."""
    assert isinstance(Success, type)
    assert isinstance(Failure, type)
