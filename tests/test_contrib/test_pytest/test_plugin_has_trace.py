import pytest

from returns.io import IOFailure, IOSuccess
from returns.result import Failure, Success


def _create_container_function(container_type, container_value):
    return container_type(container_value)


def _create_container_function_intermediate(container_type, container_value):
    return _create_container_function(
        container_type, container_value,
    )  # type: ignore


@pytest.mark.parametrize('container_type', [  # noqa: WPS118
    Success,
    Failure,
    IOSuccess,
    IOFailure,
])
def test_has_trace_with_one_function_call_in_the_call_stack(  # noqa: WPS118
    container_type, returns,
):
    """Test if our plugin will identify the container creation correctly."""
    with returns.has_trace(container_type, _create_container_function):
        _create_container_function(container_type, 1)  # type: ignore


@pytest.mark.parametrize('container_type', [  # noqa: WPS118
    Success,
    Failure,
    IOSuccess,
    IOFailure,
])
def test_has_trace_with_two_functions_call_in_the_call_stack(  # noqa: WPS118
    container_type, returns,
):
    """Test if our plugin will identify the container creation correctly."""
    with returns.has_trace(container_type, _create_container_function):
        _create_container_function_intermediate(
            container_type, 1,
        )  # type: ignore


@pytest.mark.parametrize(('desired_container_type', 'wrong_container_type'), [  # noqa: E501, WPS118
    (Success, Failure),
    (Failure, Success),
    (IOSuccess, IOFailure),
    (IOFailure, IOSuccess),
])
def test_failed_has_trace_with_one_function_call_in_the_call_stack(  # noqa: E501, WPS118
    desired_container_type, wrong_container_type, returns,
):
    """Test if our plugin will identify the conainter was not created."""
    with pytest.raises(pytest.fail.Exception):  # noqa: PT012
        with returns.has_trace(
            desired_container_type, _create_container_function,
        ):
            _create_container_function(wrong_container_type, 1)  # type: ignore


@pytest.mark.parametrize(('desired_container_type', 'wrong_container_type'), [  # noqa: E501, WPS118
    (Success, Failure),
    (Failure, Success),
    (IOSuccess, IOFailure),
    (IOFailure, IOSuccess),
])
def test_failed_has_trace_with_two_functions_call_in_the_call_stack(  # noqa: E501, WPS118
    desired_container_type, wrong_container_type, returns,
):
    """Test if our plugin will identify the conainter was not created."""
    with pytest.raises(pytest.fail.Exception):  # noqa: PT012
        with returns.has_trace(
            desired_container_type, _create_container_function,
        ):
            _create_container_function_intermediate(
                wrong_container_type, 1,
            )  # type: ignore
