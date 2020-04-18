from typing import Callable, Coroutine, Type, TypeVar, overload

from typing_extensions import Protocol

from returns.io import IOResult
from returns.maybe import Maybe
from returns.result import Result

# Just aliases:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')

# Hacks for functions:
_ReturnMaybeType = TypeVar(
    '_ReturnMaybeType',
    bound=Callable[..., Maybe],
)
_AsyncReturnMaybeType = TypeVar(
    '_AsyncReturnMaybeType',
    bound=Callable[..., Coroutine[_FirstType, _SecondType, Maybe]],
)

_ReturnResultType = TypeVar(
    '_ReturnResultType',
    bound=Callable[..., Result],
)
_AsyncReturnResultType = TypeVar(
    '_AsyncReturnResultType',
    bound=Callable[..., Coroutine[_FirstType, _SecondType, Result]],
)

_ReturnIOResultType = TypeVar(
    '_ReturnIOResultType',
    bound=Callable[..., IOResult],
)
_AsyncReturnIOResultType = TypeVar(
    '_AsyncReturnIOResultType',
    bound=Callable[..., Coroutine[_FirstType, _SecondType, IOResult]],
)


class _PipelineMaybeProtocol(Protocol):
    @overload
    def __call__(self, function: _ReturnMaybeType) -> _ReturnMaybeType:
        ...

    @overload  # noqa: F811
    def __call__(  # noqa: F811
        self, function: _AsyncReturnMaybeType,
    ) -> _AsyncReturnMaybeType:
        ...


class _PipelineResultProtocol(Protocol):
    @overload
    def __call__(self, function: _ReturnResultType) -> _ReturnResultType:
        ...

    @overload  # noqa: F811
    def __call__(  # noqa: F811
        self, function: _AsyncReturnResultType,
    ) -> _AsyncReturnResultType:
        ...


class _PipelineIOResultProtocol(Protocol):
    @overload
    def __call__(self, function: _ReturnIOResultType) -> _ReturnIOResultType:
        ...

    @overload  # noqa: F811
    def __call__(  # noqa: F811
        self, function: _AsyncReturnIOResultType,
    ) -> _AsyncReturnIOResultType:
        ...


@overload
def _pipeline(
    container_type: Type[Maybe],
) -> _PipelineMaybeProtocol:
    ...


@overload
def _pipeline(
    container_type: Type[Result],
) -> _PipelineResultProtocol:
    ...


@overload
def _pipeline(
    container_type: Type[IOResult],
) -> _PipelineIOResultProtocol:
    ...
