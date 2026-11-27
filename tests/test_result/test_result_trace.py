import pytest

from returns.io import IOFailure, IOSuccess
from returns.primitives.tracing import collect_traces
from returns.result import Failure, Success


@pytest.mark.parametrize('container_type', [Success, IOSuccess])
def test_success_trace_without_collect_traces(container_type):
    """Ensures that successful containers always expose a ``None`` trace."""
    assert container_type(1).trace is None


@pytest.mark.parametrize('container_type', [Success, IOSuccess])
def test_success_trace_with_collect_traces(container_type):
    """Ensures that traces are only collected for failed containers."""
    with collect_traces():
        traced_container = container_type(1)
    assert traced_container.trace is None


@pytest.mark.parametrize('container_type', [Failure, IOFailure])
def test_failure_trace_without_collect_traces(container_type):
    """Ensures that failed containers expose a ``None`` trace by default."""
    assert container_type(1).trace is None


@pytest.mark.parametrize('container_type', [Failure, IOFailure])
def test_failure_trace_with_collect_traces(container_type):
    """Ensures that failed containers keep collecting their traces."""
    with collect_traces():
        traced_container = container_type(1)
    assert isinstance(traced_container.trace, list)
