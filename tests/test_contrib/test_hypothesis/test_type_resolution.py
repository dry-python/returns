from typing import Sequence, Type

import pytest
from hypothesis import strategies as st

from returns.context import (
    Reader,
    RequiresContext,
    RequiresContextFutureResult,
    RequiresContextIOResult,
    RequiresContextResult,
    RequiresContextResultE,
)
from returns.future import Future, FutureResult
from returns.io import IO, IOResult
from returns.maybe import Maybe
from returns.primitives.laws import Lawful
from returns.result import Result, ResultE

_all_containers: Sequence[Type[Lawful]] = (
    Maybe,
    Result,
    IO,
    IOResult,
    Future,
    FutureResult,
    RequiresContext,
    RequiresContextResult,
    RequiresContextIOResult,
    RequiresContextFutureResult,

    # Aliases:
    ResultE,
    Reader,
    RequiresContextResultE,
)


@pytest.mark.xfail
@pytest.mark.filterwarnings('ignore:.*')
@pytest.mark.parametrize('container_type', _all_containers)
def test_all_containers_resolves(container_type: Type[Lawful]) -> None:
    """Ensures all containers do resolve."""
    # TODO: add our containers to `hypothesis.entrypoint`
    # TODO: remove `xfail` from this test
    assert st.from_type(container_type).example()
