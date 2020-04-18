import pytest

from returns.io import IOResult


@pytest.mark.parametrize('method_name', [
    'bind',
    'bind_result',
    'rescue',
])
def test_ioresult_abstract_method(method_name):
    """Checks that Result itself contains abstract methods."""
    method = getattr(IOResult, method_name)
    with pytest.raises(NotImplementedError):
        method(object, lambda to_output: to_output)


def test_ioresult_types():
    """Ensures that Result has two types inside a class."""
    assert isinstance(IOResult.success_type, type)
    assert isinstance(IOResult.failure_type, type)
