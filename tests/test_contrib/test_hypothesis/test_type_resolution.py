from typing import Any, Sequence, Type

import pytest
from hypothesis import given
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
from returns.pipeline import is_successful
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


@pytest.mark.filterwarnings('ignore:.*')
@pytest.mark.parametrize('container_type', _all_containers)
def test_all_containers_resolves(container_type: Type[Lawful]) -> None:
    """Ensures all containers do resolve."""
    assert st.from_type(container_type).example()


@given(
    st.from_type(ResultE).filter(
        lambda container: not is_successful(container),
    ),
)
def test_result_error_alias_resolves(thing: ResultE[Any]) -> None:
    """Ensures that type aliases are resolved correctly."""
    assert isinstance(thing.failure(), Exception)


CustomResult = Result[int, str]


@given(st.from_type(CustomResult))
def test_custom_result_error_types_resolve(thing: CustomResult) -> None:
    """Ensures that type aliases are resolved correctly."""
    if is_successful(thing):
        assert isinstance(thing.unwrap(), int)
    else:
        assert isinstance(thing.failure(), str)


@given(
    st.from_type(RequiresContextResultE).filter(
        lambda container: not is_successful(
            container(RequiresContextResultE.empty),
        ),
    ),
)
def test_reader_result_error_alias_resolves(
    thing: RequiresContextResultE,
) -> None:
    """Ensures that type aliases are resolved correctly."""
    real_result = thing(RequiresContextResultE.empty)
    assert isinstance(real_result.failure(), Exception)


CustomReaderResult = RequiresContextResult[int, str, bool]


@given(st.from_type(CustomReaderResult))
def test_custom_readerresult_types_resolve(
    thing: CustomReaderResult,
) -> None:
    """Ensures that type aliases are resolved correctly."""
    real_result = thing(RequiresContextResultE.empty)
    if is_successful(real_result):
        assert isinstance(real_result.unwrap(), int)
    else:
        assert isinstance(real_result.failure(), str)
