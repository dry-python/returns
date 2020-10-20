import pytest

from returns.contrib.pytest import ReturnsAsserts
from returns.io import IOFailure, IOSuccess
from returns.result import Failure, Success


def _create_container_function(container_type, container_value):
    return container_type(container_value)


def _create_container_function_intermediate(container_type, container_value):
    return _create_container_function(  # type: ignore
        container_type, container_value,
    )


@pytest.mark.parametrize('container_type', [  # noqa: WPS118
    Success,
    Failure,
    IOSuccess,
    IOFailure,
])
def test_assert_trace1(container_type, returns: ReturnsAsserts):
    """Test if our plugin will identify the container creation correctly."""
    with returns.assert_trace(container_type, _create_container_function):
        _create_container_function(container_type, 1)  # type: ignore


@pytest.mark.parametrize('container_type', [  # noqa: WPS118
    Success,
    Failure,
    IOSuccess,
    IOFailure,
])
def test_assert_trace2(container_type, returns: ReturnsAsserts):
    """Test if our plugin will identify the container creation correctly."""
    with returns.assert_trace(container_type, _create_container_function):
        _create_container_function_intermediate(  # type: ignore
            container_type, 1,
        )


@pytest.mark.parametrize(('desired_type', 'wrong_type'), [
    (Success, Failure),
    (Failure, Success),
    (IOSuccess, IOFailure),
    (IOFailure, IOSuccess),
])
def test_failed_assert_trace1(
    desired_type, wrong_type, returns: ReturnsAsserts,
):
    """Test if our plugin will identify the conainter was not created."""
    with pytest.raises(pytest.fail.Exception):  # noqa: PT012
        with returns.assert_trace(desired_type, _create_container_function):
            _create_container_function(wrong_type, 1)  # type: ignore


@pytest.mark.parametrize(('desired_type', 'wrong_type'), [
    (Success, Failure),
    (Failure, Success),
    (IOSuccess, IOFailure),
    (IOFailure, IOSuccess),
])
def test_failed_assert_trace2(
    desired_type, wrong_type, returns: ReturnsAsserts,
):
    """Test if our plugin will identify the conainter was not created."""
    with pytest.raises(pytest.fail.Exception):  # noqa: PT012
        with returns.assert_trace(desired_type, _create_container_function):
            _create_container_function_intermediate(  # type: ignore
                wrong_type, 1,
            )
