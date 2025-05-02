import pytest
from test_hypothesis.test_laws import (
    test_custom_interface_with_laws,
    test_custom_type_applicative,
)

from returns.context import (
    RequiresContext,
    RequiresContextFutureResult,
    RequiresContextIOResult,
    RequiresContextResult,
)
from returns.future import Future, FutureResult
from returns.io import IO, IOResult
from returns.maybe import Maybe
from returns.primitives.laws import Law, Lawful
from returns.result import Result


@pytest.mark.parametrize(
    'container',
    [
        Result,
        Maybe,
        Future,
        FutureResult,
        IO,
        IOResult,
        RequiresContext,
        RequiresContextFutureResult,
        RequiresContextIOResult,
        RequiresContextResult,
    ],
)
def test_laws_resolution(container: type[Lawful]):
    """Ensures all tests are unique."""
    all_laws: list[Law] = []
    for laws in container.laws().values():
        all_laws.extend(laws)
    assert len(all_laws) == len(set(all_laws))


def test_container_defined_in_returns() -> None:
    """Check that it returns all interfaces for a container in `returns`."""
    result = Result.laws()

    assert sorted(str(interface) for interface in result) == [
        "<class 'returns.interfaces.altable.AltableN'>",
        "<class 'returns.interfaces.applicative.ApplicativeN'>",
        "<class 'returns.interfaces.container.ContainerN'>",
        "<class 'returns.interfaces.equable.Equable'>",
        "<class 'returns.interfaces.failable.DiverseFailableN'>",
        "<class 'returns.interfaces.failable.FailableN'>",
        "<class 'returns.interfaces.mappable.MappableN'>",
        "<class 'returns.interfaces.swappable.SwappableN'>",
    ]


def test_container_defined_outside_returns() -> None:
    """Check container defined outside `returns`."""
    result = test_custom_type_applicative._Wrapper.laws()  # noqa: SLF001

    assert sorted(str(interface) for interface in result) == [
        "<class 'returns.interfaces.applicative.ApplicativeN'>",
        "<class 'returns.interfaces.mappable.MappableN'>",
    ]


def test_interface_defined_outside_returns() -> None:
    """Check container with interface defined outside `returns`."""
    result = test_custom_interface_with_laws._Wrapper.laws()  # noqa: SLF001

    assert sorted(str(interface) for interface in result) == [
        "<class 'test_hypothesis.test_laws.test_custom_interface_with_laws"
        "._MappableN'>"
    ]
