from typing import TypeVar, overload

from returns.context import (
    RequiresContext,
    RequiresContextIOResult,
    RequiresContextResult,
)
from returns.future import Future, FutureResult
from returns.io import IO, IOResult
from returns.maybe import Maybe
from returns.result import Result

_EnvType = TypeVar('_EnvType')
_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')


@overload
def _flatten(container: IO[IO[_ValueType]]) -> IO[_ValueType]:
    ...


@overload
def _flatten(container: Maybe[Maybe[_ValueType]]) -> Maybe[_ValueType]:
    ...


@overload
def _flatten(
    container: Result[Result[_ValueType, _ErrorType], _ErrorType],
) -> Result[_ValueType, _ErrorType]:
    ...


@overload
def _flatten(
    container: IOResult[IOResult[_ValueType, _ErrorType], _ErrorType],
) -> IOResult[_ValueType, _ErrorType]:
    ...


@overload
def _flatten(
    container: RequiresContext[
        _EnvType, RequiresContext[_EnvType, _ValueType],
    ],
) -> RequiresContext[_EnvType, _ValueType]:
    ...


@overload
def _flatten(
    container: RequiresContextResult[
        _EnvType,
        RequiresContextResult[_EnvType, _ValueType, _ErrorType],
        _ErrorType,
    ],
) -> RequiresContextResult[_EnvType, _ValueType, _ErrorType]:
    ...


@overload
def _flatten(
    container: RequiresContextIOResult[
        _EnvType,
        RequiresContextIOResult[_EnvType, _ValueType, _ErrorType],
        _ErrorType,
    ],
) -> RequiresContextIOResult[_EnvType, _ValueType, _ErrorType]:
    ...


@overload
def _flatten(container: Future[Future[_ValueType]]) -> Future[_ValueType]:
    ...


@overload
def _flatten(
    container: FutureResult[FutureResult[_ValueType, _ErrorType], _ErrorType],
) -> FutureResult[_ValueType, _ErrorType]:
    ...
