import pytest

from returns.io import IO, IOFailure, IOSuccess
from returns.primitives.exceptions import UnwrapFailedError


def test_ioresult_value_or():
    """Ensures that ``value_or`` works correctly."""
    assert IOSuccess(1).value_or(0) == IO(1)
    assert IOFailure(1).value_or(0) == IO(0)


def test_unwrap_iosuccess():
    """Ensures that unwrap works for IOSuccess container."""
    assert IOSuccess(5).unwrap() == IO(5)


def test_unwrap_iofailure():
    """Ensures that unwrap works for IOFailure container."""
    with pytest.raises(UnwrapFailedError):
        assert IOFailure(5).unwrap()


def test_unwrap_iofailure_with_exception():
    """Ensures that unwrap raises from the original exception."""
    expected_exception = ValueError('error')
    with pytest.raises(UnwrapFailedError) as excinfo:
        IOFailure(expected_exception).unwrap()

    assert 'ValueError: error' in str(
        excinfo.getrepr(),  # noqa: WPS441
    )


def test_failure_iosuccess():
    """Ensures that failure works for IOSuccess container."""
    with pytest.raises(UnwrapFailedError):
        IOSuccess(5).failure()


def test_failure_iofailure():
    """Ensures that failure works for IOFailure container."""
    assert IOFailure(5).failure() == IO(5)
