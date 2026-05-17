import pytest

from returns.transducers import treduce


def test_reduce():
    """Should fail when iterable is empty and non initial value is given."""
    with pytest.raises(TypeError):
        treduce(lambda acc, value: acc + value, [])  # noqa: WPS110
