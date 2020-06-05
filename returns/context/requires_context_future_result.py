from abc import ABCMeta
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    TypeVar,
    Union,
)

from typing_extensions import final

from returns._generated.futures import _future_result
from returns.context import NoDeps
from returns.future import FutureResult
from returns.io import IO, IOResult
from returns.primitives.container import BaseContainer
from returns.primitives.types import Immutable
from returns.result import Result

if TYPE_CHECKING:
    from returns.context.requires_context import RequiresContext
    from returns.context.requires_context_result import RequiresContextResult

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

    #: Inner value of `RequiresContext`
    #: is just a function that returns `FutureResult`.
    #: This field has an extra 'RequiresContext' just because `mypy` needs it.
    _inner_value: Callable[
        ['RequiresContextFutureResult', _EnvType],
        FutureResult[_ValueType, _ErrorType],
    ]

    #: A convinient placeholder to call methods created by `.from_value()`.
    empty: ClassVar[NoDeps] = object()

    def __init__(
        self,
        inner_value: Callable[[_EnvType], FutureResult[_ValueType, _ErrorType]],
    ) -> None:
        """
        Public constructor for this type. Also required for typing.

        Only allows functions of kind ``* -> *``
        and returning :class:`returns.result.Result` instances.

        .. code:: python

          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.future import FutureResult

          >>> instance = RequiresContextFutureResult(
          ...    lambda deps: FutureResult.from_value(1),
          ... )
          >>> str(instance)
          '<RequiresContextFutureResult: <function <lambda> at ...>>'

        """
        super().__init__(inner_value)

    def __call__(self, deps: _EnvType) -> FutureResult[_ValueType, _ErrorType]:
        """
        Evaluates the wrapped function.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess

          >>> def first(lg: bool) -> RequiresContextFutureResult[int, int, str]:
          ...     # `deps` has `int` type here:
          ...     return RequiresContextFutureResult(
          ...         lambda deps: FutureResult.from_value(
          ...             deps if lg else -deps,
          ...         ),
          ...     )

          >>> instance = first(False)
          >>> assert anyio.run(instance(3).awaitable) == IOSuccess(-3)

          >>> instance = first(True)
          >>> assert anyio.run(instance(3).awaitable) == IOSuccess(3)

        In other things, it is a regular Python magic method.

        """
        return self._inner_value(deps)

    def map(  # noqa: WPS125
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Composes successful container with a pure function.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert anyio.run(RequiresContextFutureResult.from_value(1).map(
          ...     lambda x: x + 1,
          ... )(...).awaitable) == IOSuccess(2)

          >>> assert anyio.run(RequiresContextFutureResult.from_failure(1).map(
          ...     lambda x: x + 1,
          ... )(...).awaitable) == IOFailure(1)

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).map(function),
        )

    def apply(
        self,
        container: 'RequiresContextFutureResult['
            '_EnvType, Callable[[_ValueType], _NewValueType], _ErrorType]',
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Calls a wrapped function in a container on this container.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> def transform(arg: str) -> str:
          ...     return arg + 'b'

          >>> assert anyio.run(
          ...    RequiresContextFutureResult.from_value('a').apply(
          ...        RequiresContextFutureResult.from_value(transform),
          ...    ),
          ...    RequiresContextFutureResult.empty,
          ... ) == IOSuccess('ab')

          >>> assert anyio.run(
          ...    RequiresContextFutureResult.from_failure('a').apply(
          ...        RequiresContextFutureResult.from_value(transform),
          ...    ),
          ...    RequiresContextFutureResult.empty,
          ... ) == IOFailure('a')

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).apply(container(deps)),
        )

    def bind(
        self,
        function: Callable[
            [_ValueType],
            'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]',
        ],
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Composes this container with a function returning the same type.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> def first(lg: bool) -> RequiresContextFutureResult[int, int, int]:
          ...     # `deps` has `int` type here:
          ...     return RequiresContextFutureResult(
          ...         lambda deps: FutureResult.from_value(
          ...             deps,
          ...         ) if lg else FutureResult.from_failure(-deps),
          ...     )

          >>> def second(
          ...     number: int,
          ... ) -> RequiresContextFutureResult[int, str, int]:
          ...     # `deps` has `int` type here:
          ...     return RequiresContextFutureResult(
          ...         lambda deps: FutureResult.from_value(str(number + deps)),
          ...     )

          >>> assert anyio.run(
          ...     first(True).bind(second)(1).awaitable,
          ... ) == IOSuccess('2')
          >>> assert anyio.run(
          ...     first(False).bind(second)(2).awaitable,
          ... ) == IOFailure(-2)

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).bind(
                lambda inner: function(inner)(deps),  # type: ignore[misc]
            ),
        )

    def bind_result(
        self,
        function: Callable[[_ValueType], 'Result[_NewValueType, _ErrorType]'],
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Binds ``Result`` returning function to the current container.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.result import Success, Failure, Result
          >>> from returns.io import IOSuccess, IOFailure

          >>> def function(num: int) -> Result[int, str]:
          ...     return Success(num + 1) if num > 0 else Failure('<0')

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(1).bind_result(
          ...         function,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(2)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(0).bind_result(
          ...         function,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure('<0')

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_failure(':(').bind_result(
          ...         function,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure(':(')

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).bind_result(function),
        )

    def bind_context(
        self,
        function: Callable[
            [_ValueType],
            'RequiresContext[_EnvType, _NewValueType]',
        ],
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Binds ``RequiresContext`` returning function to current container.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContext
          >>> from returns.io import IOSuccess, IOFailure

          >>> def function(arg: int) -> RequiresContext[str, int]:
          ...     return RequiresContext(lambda deps: len(deps) + arg)

          >>> assert function(2)('abc') == 5

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(2).bind_context(
          ...         function,
          ...     ),
          ...     'abc',
          ... ) == IOSuccess(5)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_failure(0).bind_context(
          ...         function,
          ...     ),
          ...     'abc',
          ... ) == IOFailure(0)

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).map(
                lambda inner: function(inner)(deps),  # type: ignore[misc]
            ),
        )

    def bind_context_result(
        self,
        function: Callable[
            [_ValueType],
            'RequiresContextResult[_EnvType, _NewValueType, _ErrorType]',
        ],
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Binds ``RequiresContextResult`` returning function to the current one.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextResult
          >>> from returns.io import IOSuccess, IOFailure
          >>> from returns.result import Success, Failure

          >>> def function(arg: int) -> RequiresContextResult[str, int, int]:
          ...     if arg > 0:
          ...         return RequiresContextResult(
          ...             lambda deps: Success(len(deps) + arg),
          ...         )
          ...     return RequiresContextResult(
          ...         lambda deps: Failure(len(deps) + arg),
          ...     )

          >>> assert function(2)('abc') == Success(5)
          >>> assert function(-1)('abc') == Failure(2)

          >>> instance = RequiresContextFutureResult.from_value(
          ...    2,
          ... ).bind_context_result(
          ...     function,
          ... )('abc')
          >>> assert anyio.run(instance.awaitable) == IOSuccess(5)

          >>> instance = RequiresContextFutureResult.from_value(
          ...    -1,
          ... ).bind_context_result(
          ...     function,
          ... )('abc')
          >>> assert anyio.run(instance.awaitable) == IOFailure(2)

          >>> instance = RequiresContextFutureResult.from_failure(
          ...    2,
          ... ).bind_context_result(
          ...     function,
          ... )('abc')
          >>> assert anyio.run(instance.awaitable) == IOFailure(2)

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).bind_result(
                lambda inner: function(inner)(deps),  # type: ignore[misc]
            ),
        )

    def bind_io(
        self,
        function: Callable[[_ValueType], IO[_NewValueType]],
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Binds ``IO`` returning function to the current container.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.io import IO, IOSuccess, IOFailure

          >>> def do_io(number: int) -> IO[str]:
          ...     return IO(str(number))  # not IO operation actually

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(1).bind_io(do_io),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess('1')

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_failure(1).bind_io(do_io),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure(1)

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).bind_io(function),
        )

    def bind_ioresult(
        self,
        function: Callable[[_ValueType], IOResult[_NewValueType, _ErrorType]],
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Binds ``IOResult`` returning function to the current container.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.io import IOResult, IOSuccess, IOFailure

          >>> def function(num: int) -> IOResult[int, str]:
          ...     return IOSuccess(num + 1) if num > 0 else IOFailure('<0')

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(1).bind_ioresult(
          ...         function,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(2)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(0).bind_ioresult(
          ...         function,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure('<0')

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_failure(':(').bind_ioresult(
          ...         function,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure(':(')

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).bind_ioresult(function),
        )

    def fix(
        self, function: Callable[[_ErrorType], _NewValueType],
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Composes failed container with a pure function.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.io import IOSuccess

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(1).fix(
          ...        lambda x: x + 1,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(1)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_failure(1).fix(
          ...        lambda x: x + 1,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(2)

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).fix(function),
        )

    def alt(
        self, function: Callable[[_ErrorType], _NewErrorType],
    ) -> 'RequiresContextFutureResult[_EnvType, _ValueType, _NewErrorType]':
        """
        Composes failed container with a pure function.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(1).alt(
          ...        lambda x: x + 1,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(1)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_failure(1).alt(
          ...        lambda x: x + 1,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure(2)

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).alt(function),
        )

    def rescue(
        self,
        function: Callable[
            [_ErrorType],
            'RequiresContextFutureResult[_EnvType, _ValueType, _NewErrorType]',
        ],
    ) -> 'RequiresContextFutureResult[_EnvType, _ValueType, _NewErrorType]':
        """
        Composes this container with a function returning the same type.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> def rescuable(
          ...     arg: str,
          ... ) -> RequiresContextFutureResult[str, str, str]:
          ...      return RequiresContextFutureResult(
          ...          lambda deps: FutureResult.from_value(
          ...              deps + arg,
          ...          ) if len(arg) > 1 else FutureResult.from_failure(
          ...              arg + deps,
          ...          ),
          ...      )

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value('a').rescue(rescuable),
          ...     'c',
          ... ) == IOSuccess('a')

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_failure('a').rescue(
          ...         rescuable,
          ...     ),
          ...     'c',
          ... ) == IOFailure('ac')

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_failure('aa').rescue(
          ...         rescuable,
          ...     ),
          ...     'b',
          ... ) == IOSuccess('baa')

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).rescue(
                lambda inner: function(inner)(deps),  # type: ignore[misc]
            ),
        )

    def value_or(  # noqa: WPS234
        self, default_value: _FirstType,
    ) -> Callable[
        [_EnvType],
        Awaitable[IO[Union[_ValueType, _FirstType]]],
    ]:
        """
        Returns a callable that either returns a success or default value.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.io import IO

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(1).value_or(2),
          ...     RequiresContextFutureResult.empty,
          ... ) == IO(1)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_failure(1).value_or(2),
          ...     RequiresContextFutureResult.empty,
          ... ) == IO(2)

        """
        return lambda deps: _future_result.async_value_or(
            self(deps), default_value,
        )

    def unwrap(self) -> Callable[[_EnvType], Awaitable[IO[_ValueType]]]:
        """
        Returns a callable that unwraps success value or raises exception.

        .. code:: pycon

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.io import IO

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(1).unwrap(),
          ...     RequiresContextFutureResult.empty,
          ... ) == IO(1)

          >>> anyio.run(
          ...     RequiresContextFutureResult.from_failure(1).unwrap(),
          ...     RequiresContextFutureResult.empty,
          ... )
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
        return lambda deps: _future_result.async_unwrap(self(deps))

    def failure(self) -> Callable[[_EnvType], Awaitable[IO[_ErrorType]]]:
        """
        Returns a callable that unwraps failure value or raises exception.

        .. code:: pycon

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.io import IO

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_failure(1).failure(),
          ...     RequiresContextFutureResult.empty,
          ... ) == IO(1)

          >>> anyio.run(
          ...    RequiresContextFutureResult.from_value(1).failure(),
          ...    RequiresContextFutureResult.empty,
          ... )
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
        return lambda deps: _future_result.async_failure(self(deps))

    @classmethod
    def from_value(
        cls, inner_value: _FirstType,
    ) -> 'RequiresContextFutureResult[NoDeps, _FirstType, Any]':
        """
        Creates new container with successful ``FutureResult`` as a unit value.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.io import IOSuccess

          >>> assert anyio.run(RequiresContextFutureResult.from_value(1)(
          ...    RequiresContextFutureResult.empty,
          ... ).awaitable) == IOSuccess(1)

        """
        return RequiresContextFutureResult(
            lambda _: FutureResult.from_value(inner_value),
        )

    @classmethod
    def from_failure(
        cls, inner_value: _FirstType,
    ) -> 'RequiresContextFutureResult[NoDeps, Any, _FirstType]':
        """
        Creates new container with failed ``FutureResult`` as a unit value.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.io import IOFailure

          >>> assert anyio.run(RequiresContextFutureResult.from_failure(1)(
          ...     RequiresContextFutureResult.empty,
          ... ).awaitable) == IOFailure(1)

        """
        return RequiresContextFutureResult(
            lambda _: FutureResult.from_failure(inner_value),
        )


@final
class ContextFutureResult(Immutable, Generic[_EnvType], metaclass=ABCMeta):
    """
    Helpers that can be used to work with ``ReaderFutureResult`` container.

    Related to :class:`returns.context.requires_context.Context`
    and :class:`returns.context.requires_context_result.ContextResult`,
    refer there for the docs.
    """

    __slots__ = ()

    @classmethod
    def ask(cls) -> RequiresContextFutureResult[_EnvType, _EnvType, Any]:
        """
        Is used to get the current dependencies inside the call stack.

        Similar to :meth:`returns.context.requires_context.Context.ask`,
        but returns ``IOResult`` instead of a regular value.

        Please, refer to the docs there to learn how to use it.

        One important note that is worth duplicating here:
        you might need to provide ``_EnvType`` explicitly,
        so ``mypy`` will know about it statically.

        .. code:: python

          >>> import anyio
          >>> from returns.context import ContextFutureResult
          >>> from returns.io import IOSuccess

          >>> assert anyio.run(
          ...     ContextFutureResult[int].ask().map(str),
          ...     1,
          ... ) == IOSuccess('1')

        """
        return RequiresContextFutureResult(FutureResult.from_value)


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
