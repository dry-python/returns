from abc import ABCMeta
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterable,
    Sequence,
    TypeVar,
    Union,
)

from typing_extensions import final

from returns._generated.futures import _future_result, _reader_future_result
from returns._generated.iterable import iterable
from returns.context import NoDeps
from returns.future import Future, FutureResult
from returns.io import IO, IOResult
from returns.primitives.container import BaseContainer
from returns.primitives.types import Immutable
from returns.result import Result

if TYPE_CHECKING:
    from returns.context.requires_context import RequiresContext
    from returns.context.requires_context_result import RequiresContextResult
    from returns.context.requires_context_ioresult import (
        RequiresContextIOResult,
    )

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
    """
    The ``RequiresContextFutureResult`` combinator.

    This probably the main type people are going to use in ``async`` programms.

    See :class:`returns.context.requires_context.RequiresContext`,
    :class:`returns.context.requires_context_result.RequiresContextResult`,
    and
    :class:`returns.context.requires_context_result.RequiresContextIOResult`
    for more docs.

    This is just a handy wrapper around
    ``RequiresContext[env, FutureResult[a, b]]``
    which represents a context-dependent impure operation that might fail.

    So, this is a thin wrapper, without any changes in logic.
    Why do we need this wrapper? That's just for better usability!

    This way ``RequiresContextIOResult`` allows to simply work with:

    - raw values and pure functions
    - ``RequiresContext`` values and pure functions returning it
    - ``RequiresContextResult`` values and pure functions returning it
    - ``RequiresContextIOResult`` values and pure functions returning it
    - ``Result`` and pure functions returning it
    - ``IOResult`` and functions returning it
    - ``FutureResult`` and functions returning it
    - other ``RequiresContextFutureResult`` related functions and values

    This is a complex type for complex tasks!

    Important implementation detail:
    due it is meaning, ``RequiresContextFutureResult``
    cannot have ``Success`` and ``Failure`` subclasses.

    We only have just one type. That's by design.

    Different converters are also not supported for this type.
    Use converters inside the ``RequiresContext`` context, not outside.

    See also:
        https://dev.to/gcanti/getting-started-with-fp-ts-reader-1ie5
        https://en.wikipedia.org/wiki/Lazy_evaluation
        https://bit.ly/2R8l4WK
        https://bit.ly/2RwP4fp

    """

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

          >>> def function(
          ...     number: int,
          ... ) -> RequiresContextFutureResult[int, str, int]:
          ...     # `deps` has `int` type here:
          ...     return RequiresContextFutureResult(
          ...         lambda deps: FutureResult.from_value(str(number + deps)),
          ...     )

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(2).bind(function),
          ...     3,
          ... ) == IOSuccess('5')
          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_failure(2).bind(function),
          ...     3,
          ... ) == IOFailure(2)

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).bind(
                lambda inner: function(inner)(deps),  # type: ignore[misc]
            ),
        )

    def bind_async(
        self,
        function: Callable[
            [_ValueType],
            Awaitable[
                'RequiresContextFutureResult'
                '[_EnvType, _NewValueType, _ErrorType]'
            ],
        ],
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Composes this container with a async function returning the same type.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> async def function(
          ...     number: int,
          ... ) -> RequiresContextFutureResult[int, str, int]:
          ...     return RequiresContextFutureResult.from_value(number + 1)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(1).bind_async(
          ...        function,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(2)
          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_failure(1).bind_async(
          ...        function,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure(1)

        """
        return RequiresContextFutureResult(
            lambda deps: FutureResult(_reader_future_result.async_bind_async(
                function, self, deps,
            )),
        )

    def bind_awaitable(
        self,
        function: Callable[[_ValueType], 'Awaitable[_NewValueType]'],
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Allows to compose a container and a regular ``async`` function.

        This function should return plain, non-container value.
        See :meth:`~RequiresContextFutureResult.bind_async`
        to bind ``async`` function that returns a container.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> async def coroutine(x: int) -> int:
          ...    return x + 1

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(1).bind_awaitable(
          ...         coroutine,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(2)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_failure(1).bind_awaitable(
          ...         coroutine,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure(1)

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).bind_awaitable(function),
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
          >>> from returns.result import Success, Result
          >>> from returns.io import IOSuccess, IOFailure

          >>> def function(num: int) -> Result[int, str]:
          ...     return Success(num + 1)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(1).bind_result(
          ...         function,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(2)

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
          >>> from returns.result import Success

          >>> def function(arg: int) -> RequiresContextResult[str, int, int]:
          ...     return RequiresContextResult(
          ...         lambda deps: Success(len(deps) + arg),
          ...     )

          >>> instance = RequiresContextFutureResult.from_value(
          ...    2,
          ... ).bind_context_result(
          ...     function,
          ... )('abc')
          >>> assert anyio.run(instance.awaitable) == IOSuccess(5)

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

    def bind_context_ioresult(
        self,
        function: Callable[
            [_ValueType],
            'RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]',
        ],
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Binds ``RequiresContextIOResult`` returning function to the current one.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> def function(arg: int) -> RequiresContextIOResult[str, int, int]:
          ...     return RequiresContextIOResult(
          ...         lambda deps: IOSuccess(len(deps) + arg),
          ...     )

          >>> instance = RequiresContextFutureResult.from_value(
          ...    2,
          ... ).bind_context_ioresult(
          ...     function,
          ... )('abc')
          >>> assert anyio.run(instance.awaitable) == IOSuccess(5)

          >>> instance = RequiresContextFutureResult.from_failure(
          ...    2,
          ... ).bind_context_ioresult(
          ...     function,
          ... )('abc')
          >>> assert anyio.run(instance.awaitable) == IOFailure(2)

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).bind_ioresult(
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
          ...     return IOSuccess(num + 1)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(1).bind_ioresult(
          ...         function,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(2)

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

    def bind_future(
        self,
        function: Callable[[_ValueType], Future[_NewValueType]],
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Binds ``Future`` returning function to the current container.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.future import Future
          >>> from returns.io import IOSuccess, IOFailure

          >>> def function(num: int) -> Future[int]:
          ...     return Future.from_value(num + 1)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(1).bind_future(
          ...         function,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(2)

          >>> failed = RequiresContextFutureResult.from_failure(':(')
          >>> assert anyio.run(
          ...     failed.bind_future(function),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure(':(')

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).bind_future(function),
        )

    def bind_future_result(
        self,
        function: Callable[
            [_ValueType],
            FutureResult[_NewValueType, _ErrorType],
        ],
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Binds ``FutureResult`` returning function to the current container.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> def function(num: int) -> FutureResult[int, str]:
          ...     return FutureResult.from_value(num + 1)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(1).bind_future_result(
          ...         function,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(2)

          >>> failed = RequiresContextFutureResult.from_failure(':(')
          >>> assert anyio.run(
          ...     failed.bind_future_result(function),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure(':(')

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).bind(function),
        )

    def bind_async_future(
        self,
        function: Callable[[_ValueType], Awaitable[Future[_NewValueType]]],
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Binds ``Future`` returning async function to the current container.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.future import Future
          >>> from returns.io import IOSuccess, IOFailure

          >>> async def function(num: int) -> Future[int]:
          ...     return Future.from_value(num + 1)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(1).bind_async_future(
          ...         function,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(2)

          >>> failed = RequiresContextFutureResult.from_failure(':(')
          >>> assert anyio.run(
          ...     failed.bind_async_future(function),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure(':(')

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).bind_async_future(function),
        )

    def bind_async_future_result(
        self,
        function: Callable[
            [_ValueType],
            Awaitable[FutureResult[_NewValueType, _ErrorType]],
        ],
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Bind ``FutureResult`` returning async function to the current container.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> async def function(num: int) -> FutureResult[int, str]:
          ...     return FutureResult.from_value(num + 1)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value(
          ...         1,
          ...     ).bind_async_future_result(
          ...         function,
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(2)

          >>> failed = RequiresContextFutureResult.from_failure(':(')
          >>> assert anyio.run(
          ...     failed.bind_async_future_result(function),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure(':(')

        """
        return RequiresContextFutureResult(
            lambda deps: self(deps).bind_async(function),
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
          >>> from returns.io import IOSuccess

          >>> def rescuable(
          ...     arg: str,
          ... ) -> RequiresContextFutureResult[str, str, str]:
          ...      return RequiresContextFutureResult(
          ...          lambda deps: FutureResult.from_value(
          ...              deps + arg,
          ...          ),
          ...      )

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_value('a').rescue(rescuable),
          ...     'c',
          ... ) == IOSuccess('a')

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
    def from_result(
        cls, inner_value: Result[_ValueType, _ErrorType],
    ) -> 'RequiresContextFutureResult[NoDeps, _ValueType, _ErrorType]':
        """
        Creates new container with ``Result`` as a unit value.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.result import Success, Failure
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert anyio.run(
          ...    RequiresContextFutureResult.from_result(Success(1)),
          ...    RequiresContextFutureResult.empty,
          ... ) == IOSuccess(1)

          >>> assert anyio.run(
          ...    RequiresContextFutureResult.from_result(Failure(1)),
          ...    RequiresContextFutureResult.empty,
          ... ) == IOFailure(1)

        """
        return RequiresContextFutureResult(
            lambda _: FutureResult.from_result(inner_value),
        )

    @classmethod
    def from_io(
        cls,
        inner_value: IO[_NewValueType],
    ) -> 'RequiresContextFutureResult[NoDeps, _NewValueType, Any]':
        """
        Creates new container from successful ``IO`` value.

        .. code:: python

          >>> import anyio
          >>> from returns.io import IO, IOSuccess
          >>> from returns.context import RequiresContextFutureResult

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_io(IO(1)),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(1)

        """
        return RequiresContextFutureResult(
            lambda deps: FutureResult.from_io(inner_value),
        )

    @classmethod
    def from_failed_io(
        cls,
        inner_value: IO[_NewErrorType],
    ) -> 'RequiresContextFutureResult[NoDeps, Any, _NewErrorType]':
        """
        Creates a new container from failed ``IO`` value.

        .. code:: python

          >>> import anyio
          >>> from returns.io import IO, IOFailure
          >>> from returns.context import RequiresContextFutureResult

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_failed_io(IO(1)),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure(1)

        """
        return RequiresContextFutureResult(
            lambda deps: FutureResult.from_failed_io(inner_value),
        )

    @classmethod
    def from_ioresult(
        cls, inner_value: IOResult[_ValueType, _ErrorType],
    ) -> 'RequiresContextFutureResult[NoDeps, _ValueType, _ErrorType]':
        """
        Creates new container with ``IOResult`` as a unit value.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert anyio.run(
          ...    RequiresContextFutureResult.from_ioresult(IOSuccess(1)),
          ...    RequiresContextFutureResult.empty,
          ... ) == IOSuccess(1)

          >>> assert anyio.run(
          ...    RequiresContextFutureResult.from_ioresult(IOFailure(1)),
          ...    RequiresContextFutureResult.empty,
          ... ) == IOFailure(1)

        """
        return RequiresContextFutureResult(
            lambda _: FutureResult.from_ioresult(inner_value),
        )

    @classmethod
    def from_future(
        cls,
        inner_value: Future[_ValueType],
    ) -> 'RequiresContextFutureResult[NoDeps, _ValueType, Any]':
        """
        Creates new container with successful ``Future`` as a unit value.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.future import Future
          >>> from returns.io import IOSuccess

          >>> assert anyio.run(
          ...    RequiresContextFutureResult.from_future(Future.from_value(1)),
          ...    RequiresContextFutureResult.empty,
          ... ) == IOSuccess(1)

        """
        return RequiresContextFutureResult(
            lambda _: FutureResult.from_future(inner_value),
        )

    @classmethod
    def from_failed_future(
        cls,
        inner_value: Future[_ErrorType],
    ) -> 'RequiresContextFutureResult[NoDeps, Any, _ErrorType]':
        """
        Creates new container with failed ``Future`` as a unit value.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.future import Future
          >>> from returns.io import IOFailure

          >>> assert anyio.run(
          ...    RequiresContextFutureResult.from_failed_future(
          ...        Future.from_value(1),
          ...    ),
          ...    RequiresContextFutureResult.empty,
          ... ) == IOFailure(1)

        """
        return RequiresContextFutureResult(
            lambda _: FutureResult.from_failed_future(inner_value),
        )

    @classmethod
    def from_future_result(
        cls,
        inner_value: FutureResult[_ValueType, _ErrorType],
    ) -> 'RequiresContextFutureResult[NoDeps, _ValueType, _ErrorType]':
        """
        Creates new container with ``FutureResult`` as a unit value.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert anyio.run(
          ...    RequiresContextFutureResult.from_future_result(
          ...        FutureResult.from_value(1),
          ...    ),
          ...    RequiresContextFutureResult.empty,
          ... ) == IOSuccess(1)

          >>> assert anyio.run(
          ...    RequiresContextFutureResult.from_future_result(
          ...        FutureResult.from_failure(1),
          ...    ),
          ...    RequiresContextFutureResult.empty,
          ... ) == IOFailure(1)

        """
        return RequiresContextFutureResult(lambda _: inner_value)

    @classmethod
    def from_typecast(
        cls,
        inner_value: 'RequiresContext['
            '_EnvType, FutureResult[_NewValueType, _NewErrorType]]',
    ) -> 'RequiresContextFutureResult[_EnvType, _NewValueType, _NewErrorType]':
        """
        You might end up with ``RequiresContext[FutureResult]`` as a value.

        This method is designed to turn it into ``RequiresContextFutureResult``.
        It will save all the typing information.

        It is just more useful!

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContext
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_typecast(
          ...         RequiresContext.from_value(FutureResult.from_value(1)),
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(1)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_typecast(
          ...         RequiresContext.from_value(FutureResult.from_failure(1)),
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure(1)

        """
        return RequiresContextFutureResult(inner_value)

    @classmethod
    def from_context(
        cls, inner_value: 'RequiresContext[_EnvType, _FirstType]',
    ) -> 'RequiresContextFutureResult[_EnvType, _FirstType, Any]':
        """
        Creates new container from ``RequiresContext`` as a success unit.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContext
          >>> from returns.io import IOSuccess

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_context(
          ...         RequiresContext.from_value(1),
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(1)

        """
        return RequiresContextFutureResult(
            lambda deps: FutureResult.from_value(inner_value(deps)),
        )

    @classmethod
    def from_failed_context(
        cls, inner_value: 'RequiresContext[_EnvType, _FirstType]',
    ) -> 'RequiresContextFutureResult[_EnvType, Any, _FirstType]':
        """
        Creates new container from ``RequiresContext`` as a failure unit.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContext
          >>> from returns.io import IOFailure

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_failed_context(
          ...         RequiresContext.from_value(1),
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure(1)

        """
        return RequiresContextFutureResult(
            lambda deps: FutureResult.from_failure(inner_value(deps)),
        )

    @classmethod
    def from_result_context(
        cls,
        inner_value: 'RequiresContextResult[_EnvType, _ValueType, _ErrorType]',
    ) -> 'RequiresContextFutureResult[_EnvType, _ValueType, _ErrorType]':
        """
        Creates new container from ``RequiresContextResult`` as a unit value.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_result_context(
          ...         RequiresContextResult.from_value(1),
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(1)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_result_context(
          ...         RequiresContextResult.from_failure(1),
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure(1)

        """
        return RequiresContextFutureResult(
            lambda deps: FutureResult.from_result(inner_value(deps)),
        )

    @classmethod
    def from_ioresult_context(
        cls,
        inner_value:
            'RequiresContextIOResult[_EnvType, _ValueType, _ErrorType]',
    ) -> 'RequiresContextFutureResult[_EnvType, _ValueType, _ErrorType]':
        """
        Creates new container from ``RequiresContextIOResult`` as a unit value.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_ioresult_context(
          ...         RequiresContextIOResult.from_value(1),
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOSuccess(1)

          >>> assert anyio.run(
          ...     RequiresContextFutureResult.from_ioresult_context(
          ...         RequiresContextIOResult.from_failure(1),
          ...     ),
          ...     RequiresContextFutureResult.empty,
          ... ) == IOFailure(1)

        """
        return RequiresContextFutureResult(
            lambda deps: FutureResult.from_ioresult(inner_value(deps)),
        )

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

    @classmethod
    def from_iterable(
        cls,
        inner_value:
            Iterable[
                'RequiresContextFutureResult[_EnvType, _ValueType, _ErrorType]',
            ],
    ) -> 'ReaderFutureResult[_EnvType, Sequence[_ValueType], _ErrorType]':
        """
        Transforms an iterable of ``RequiresContextFutureResult`` containers.

        Returns a single container with multiple elements inside.

        .. code:: python

          >>> import anyio
          >>> from returns.context import RequiresContextFutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert anyio.run(
          ...    RequiresContextFutureResult.from_iterable([
          ...        RequiresContextFutureResult.from_value(1),
          ...        RequiresContextFutureResult.from_value(2),
          ...    ]),
          ...    RequiresContextFutureResult.empty,
          ... ) == IOSuccess((1, 2))

          >>> assert anyio.run(
          ...    RequiresContextFutureResult.from_iterable([
          ...        RequiresContextFutureResult.from_value(1),
          ...        RequiresContextFutureResult.from_failure('a'),
          ...    ]),
          ...    RequiresContextFutureResult.empty,
          ... ) == IOFailure('a')

        """
        return iterable(cls, inner_value)


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
