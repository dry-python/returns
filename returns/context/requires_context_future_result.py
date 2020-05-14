from typing import Generic, TypeVar

from typing_extensions import final

from returns.primitives.container import BaseContainer

# Context:
_EnvType = TypeVar('_EnvType', contravariant=True)

# Result:
_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType', covariant=True)
_NewErrorType = TypeVar('_NewErrorType')

# Helpers:
_FirstType = TypeVar('_FirstType')


@final
class RequiresContextFutureResult(
    BaseContainer,
    Generic[_EnvType, _ValueType, _ErrorType],
):
    """Someday this container will grow very big."""


# Aliases:

#: Alias for a popular case when ``Result`` has ``Exception`` as error type.
RequiresContextFutureResultE = RequiresContextFutureResult[
    _EnvType, _ValueType, Exception,
]

#: Sometimes `RequiresContextFutureResult` is too long to type.
ReaderFutureResult = RequiresContextFutureResult

#: Alias to save you some typing. Uses ``Exception`` as error type.
ReaderFutureResultE = RequiresContextFutureResult[
    _EnvType, _ValueType, Exception,
]
