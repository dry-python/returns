from abc import ABCMeta
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Generic,
    Iterable,
    Sequence,
    TypeVar,
)

from typing_extensions import final

from returns._generated.iterable import iterable_kind
from returns.context import NoDeps
from returns.interfaces import iterable
from returns.interfaces.specific import ioresult
from returns.io import IO, IOFailure, IOResult, IOSuccess
from returns.primitives.container import BaseContainer
from returns.primitives.hkt import Kind3, SupportsKind3, dekind
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
class RequiresContextIOResult(
    BaseContainer,
    SupportsKind3['RequiresContextIOResult', _ValueType, _ErrorType, _EnvType],
    ioresult.IOResultBased3[_ValueType, _ErrorType, _EnvType],
    iterable.Iterable3[_ValueType, _ErrorType, _EnvType],
):
    """
    The ``RequiresContextIOResult`` combinator.

    See :class:`returns.context.requires_context.RequiresContext`
    and :class:`returns.context.requires_context_result.RequiresContextResult`
    for more docs.

    This is just a handy wrapper around
    ``RequiresContext[env, IOResult[a, b]]``
    which represents a context-dependent impure operation that might fail.

    It has several important differences from the regular ``Result`` classes.
    It does not have ``Success`` and ``Failure`` subclasses.
    Because, the computation is not yet performed.
    And we cannot know the type in advance.

    So, this is a thin wrapper, without any changes in logic.

    Why do we need this wrapper? That's just for better usability!

    .. code:: python

      >>> from returns.context import RequiresContext
      >>> from returns.io import IOSuccess, IOResult

      >>> def function(arg: int) -> IOResult[int, str]:
      ...      return IOSuccess(arg + 1)

      >>> # Without wrapper:
      >>> assert RequiresContext.from_value(IOSuccess(1)).map(
      ...     lambda ioresult: ioresult.bind(function),
      ... )(...) == IOSuccess(2)

      >>> # With wrapper:
      >>> assert RequiresContextIOResult.from_value(1).bind_ioresult(
      ...     function,
      ... )(...) == IOSuccess(2)

    This way ``RequiresContextIOResult`` allows to simply work with:

    - raw values and pure functions
    - ``RequiresContext`` values and pure functions returning it
    - ``RequiresContextResult`` values and pure functions returning it
    - ``Result`` and pure functions returning it
    - ``IOResult`` and functions returning it
    - other ``RequiresContextIOResult`` related functions and values

    This is a complex type for complex tasks!

    Important implementation detail:
    due it is meaning, ``RequiresContextIOResult``
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
    #: is just a function that returns `IOResult`.
    #: This field has an extra 'RequiresContext' just because `mypy` needs it.
    _inner_value: Callable[
        ['RequiresContextIOResult', _EnvType],
        IOResult[_ValueType, _ErrorType],
    ]

    #: A convinient placeholder to call methods created by `.from_value()`.
    empty: ClassVar[NoDeps] = object()

    def __init__(
        self,
        inner_value: Callable[[_EnvType], IOResult[_ValueType, _ErrorType]],
    ) -> None:
        """
        Public constructor for this type. Also required for typing.

        Only allows functions of kind ``* -> *``
        and returning :class:`returns.result.Result` instances.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess
          >>> str(RequiresContextIOResult(lambda deps: IOSuccess(deps + 1)))
          '<RequiresContextIOResult: <function <lambda> at ...>>'

        """
        super().__init__(inner_value)

    def __call__(self, deps: _EnvType) -> IOResult[_ValueType, _ErrorType]:
        """
        Evaluates the wrapped function.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess

          >>> def first(lg: bool) -> RequiresContextIOResult[int, str, float]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContextIOResult(
          ...         lambda deps: IOSuccess(deps if lg else -deps),
          ...     )

          >>> instance = first(False)
          >>> assert instance(3.5) == IOSuccess(-3.5)

        In other things, it is a regular Python magic method.

        """
        return self._inner_value(deps)

    def swap(
        self,
    ) -> 'RequiresContextIOResult[_ErrorType, _ValueType, _EnvType]':
        """
        Swaps value and error types.

        So, values become errors and errors become values.
        It is useful when you have to work with errors a lot.
        And since we have a lot of ``.bind_`` related methods
        and only a single ``.rescue`` - it is easier to work with values.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> success = RequiresContextIOResult.from_value(1)
          >>> failure = RequiresContextIOResult.from_failure(1)

          >>> assert success.swap()(...) == IOFailure(1)
          >>> assert failure.swap()(...) == IOSuccess(1)

        """
        return RequiresContextIOResult(lambda deps: self(deps).swap())

    def map(  # noqa: WPS125
        self, function: Callable[[_ValueType], _NewValueType],
    ) -> 'RequiresContextIOResult[_NewValueType, _ErrorType, _EnvType]':
        """
        Composes successful container with a pure function.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert RequiresContextIOResult.from_value(1).map(
          ...     lambda x: x + 1,
          ... )(...) == IOSuccess(2)

          >>> assert RequiresContextIOResult.from_failure(1).map(
          ...     lambda x: x + 1,
          ... )(...) == IOFailure(1)

        """
        return RequiresContextIOResult(lambda deps: self(deps).map(function))

    def apply(
        self,
        container: Kind3[
            'RequiresContextIOResult',
            Callable[[_ValueType], _NewValueType],
            _ErrorType,
            _EnvType,
        ],
    ) -> 'RequiresContextIOResult[_NewValueType, _ErrorType, _EnvType]':
        """
        Calls a wrapped function in a container on this container.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess, IOFailure, IOResult

          >>> def transform(arg: str) -> str:
          ...     return arg + 'b'

          >>> assert RequiresContextIOResult.from_value('a').apply(
          ...    RequiresContextIOResult.from_value(transform),
          ... )(...) == IOSuccess('ab')

          >>> assert RequiresContextIOResult.from_failure('a').apply(
          ...    RequiresContextIOResult.from_value(transform),
          ... )(...) == IOFailure('a')

          >>> assert isinstance(RequiresContextIOResult.from_value('a').apply(
          ...    RequiresContextIOResult.from_failure(transform),
          ... )(...), IOResult.failure_type) is True

        """
        return RequiresContextIOResult(
            lambda deps: self(deps).apply(dekind(container)(deps)),
        )

    def bind(
        self,
        function: Callable[
            [_ValueType],
            Kind3[
                'RequiresContextIOResult',
                _NewValueType,
                _ErrorType,
                _EnvType,
            ],
        ],
    ) -> 'RequiresContextIOResult[_NewValueType, _ErrorType, _EnvType]':
        """
        Composes this container with a function returning the same type.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> def first(lg: bool) -> RequiresContextIOResult[int, int, float]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContextIOResult(
          ...         lambda deps: IOSuccess(deps) if lg else IOFailure(-deps),
          ...     )

          >>> def second(
          ...     number: int,
          ... ) -> RequiresContextIOResult[str, int, float]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContextIOResult(
          ...         lambda deps: IOSuccess('>=' if number >= deps else '<'),
          ...     )

          >>> assert first(True).bind(second)(1) == IOSuccess('>=')
          >>> assert first(False).bind(second)(2) == IOFailure(-2)

        """
        return RequiresContextIOResult(
            lambda deps: self(deps).bind(
                lambda inner: dekind(  # type: ignore[misc]
                    function(inner),
                )(deps),
            ),
        )

    def bind_result(
        self,
        function: Callable[[_ValueType], 'Result[_NewValueType, _ErrorType]'],
    ) -> 'RequiresContextIOResult[_NewValueType, _ErrorType, _EnvType]':
        """
        Binds ``Result`` returning function to the current container.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.result import Success, Failure, Result
          >>> from returns.io import IOSuccess, IOFailure

          >>> def function(num: int) -> Result[int, str]:
          ...     return Success(num + 1) if num > 0 else Failure('<0')

          >>> assert RequiresContextIOResult.from_value(1).bind_result(
          ...     function,
          ... )(RequiresContextIOResult.empty) == IOSuccess(2)

          >>> assert RequiresContextIOResult.from_value(0).bind_result(
          ...     function,
          ... )(RequiresContextIOResult.empty) == IOFailure('<0')

          >>> assert RequiresContextIOResult.from_failure(':(').bind_result(
          ...     function,
          ... )(RequiresContextIOResult.empty) == IOFailure(':(')

        """
        return RequiresContextIOResult(
            lambda deps: self(deps).bind_result(function),
        )

    def bind_context(
        self,
        function: Callable[
            [_ValueType],
            'RequiresContext[_NewValueType, _EnvType]',
        ],
    ) -> 'RequiresContextIOResult[_NewValueType, _ErrorType, _EnvType]':
        """
        Binds ``RequiresContext`` returning function to current container.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> from returns.io import IOSuccess, IOFailure

          >>> def function(arg: int) -> RequiresContext[int, str]:
          ...     return RequiresContext(lambda deps: len(deps) + arg)

          >>> assert function(2)('abc') == 5

          >>> assert RequiresContextIOResult.from_value(2).bind_context(
          ...     function,
          ... )('abc') == IOSuccess(5)

          >>> assert RequiresContextIOResult.from_failure(2).bind_context(
          ...     function,
          ... )('abc') == IOFailure(2)

        """
        return RequiresContextIOResult(
            lambda deps: self(deps).map(
                lambda inner: function(inner)(deps),  # type: ignore[misc]
            ),
        )

    def bind_context_result(
        self,
        function: Callable[
            [_ValueType],
            'RequiresContextResult[_NewValueType, _ErrorType, _EnvType]',
        ],
    ) -> 'RequiresContextIOResult[_NewValueType, _ErrorType, _EnvType]':
        """
        Binds ``RequiresContextResult`` returning function to the current one.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.io import IOSuccess, IOFailure
          >>> from returns.result import Success, Failure

          >>> def function(arg: int) -> RequiresContextResult[int, int, str]:
          ...     if arg > 0:
          ...         return RequiresContextResult(
          ...             lambda deps: Success(len(deps) + arg),
          ...         )
          ...     return RequiresContextResult(
          ...         lambda deps: Failure(len(deps) + arg),
          ...     )

          >>> assert function(2)('abc') == Success(5)
          >>> assert function(-1)('abc') == Failure(2)

          >>> assert RequiresContextIOResult.from_value(
          ...    2,
          ... ).bind_context_result(
          ...     function,
          ... )('abc') == IOSuccess(5)

          >>> assert RequiresContextIOResult.from_value(
          ...    -1,
          ... ).bind_context_result(
          ...     function,
          ... )('abc') == IOFailure(2)

          >>> assert RequiresContextIOResult.from_failure(
          ...    2,
          ... ).bind_context_result(
          ...     function,
          ... )('abc') == IOFailure(2)

        """
        return RequiresContextIOResult(
            lambda deps: self(deps).bind_result(
                lambda inner: function(inner)(deps),  # type: ignore[misc]
            ),
        )

    def bind_io(
        self,
        function: Callable[[_ValueType], IO[_NewValueType]],
    ) -> 'RequiresContextIOResult[_NewValueType, _ErrorType, _EnvType]':
        """
        Binds ``IO`` returning function to the current container.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IO, IOSuccess, IOFailure

          >>> def function(number: int) -> IO[str]:
          ...     return IO(str(number))

          >>> assert RequiresContextIOResult.from_value(1).bind_io(
          ...     function,
          ... )(RequiresContextIOResult.empty) == IOSuccess('1')

          >>> assert RequiresContextIOResult.from_failure(1).bind_io(
          ...     function,
          ... )(RequiresContextIOResult.empty) == IOFailure(1)

        """
        return RequiresContextIOResult(
            lambda deps: self(deps).bind_io(function),
        )

    def bind_ioresult(
        self,
        function: Callable[[_ValueType], IOResult[_NewValueType, _ErrorType]],
    ) -> 'RequiresContextIOResult[_NewValueType, _ErrorType, _EnvType]':
        """
        Binds ``IOResult`` returning function to the current container.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOResult, IOSuccess, IOFailure

          >>> def function(num: int) -> IOResult[int, str]:
          ...     return IOSuccess(num + 1) if num > 0 else IOFailure('<0')

          >>> assert RequiresContextIOResult.from_value(1).bind_ioresult(
          ...     function,
          ... )(RequiresContextIOResult.empty) == IOSuccess(2)

          >>> assert RequiresContextIOResult.from_value(0).bind_ioresult(
          ...     function,
          ... )(RequiresContextIOResult.empty) == IOFailure('<0')

          >>> assert RequiresContextIOResult.from_failure(':(').bind_ioresult(
          ...     function,
          ... )(RequiresContextIOResult.empty) == IOFailure(':(')

        """
        return RequiresContextIOResult(
            lambda deps: self(deps).bind(function),
        )

    def alt(
        self, function: Callable[[_ErrorType], _NewErrorType],
    ) -> 'RequiresContextIOResult[_ValueType, _NewErrorType, _EnvType]':
        """
        Composes failed container with a pure function.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert RequiresContextIOResult.from_value(1).alt(
          ...     lambda x: x + 1,
          ... )(...) == IOSuccess(1)

          >>> assert RequiresContextIOResult.from_failure(1).alt(
          ...     lambda x: x + 1,
          ... )(...) == IOFailure(2)

        """
        return RequiresContextIOResult(lambda deps: self(deps).alt(function))

    def rescue(
        self,
        function: Callable[
            [_ErrorType],
            Kind3[
                'RequiresContextIOResult',
                _ValueType,
                _NewErrorType,
                _EnvType,
            ],
        ],
    ) -> 'RequiresContextIOResult[_ValueType, _NewErrorType, _EnvType]':
        """
        Composes this container with a function returning the same type.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> def rescuable(
          ...     arg: str,
          ... ) -> RequiresContextIOResult[str, str, str]:
          ...      if len(arg) > 1:
          ...          return RequiresContextIOResult(
          ...              lambda deps: IOSuccess(deps + arg),
          ...          )
          ...      return RequiresContextIOResult(
          ...          lambda deps: IOFailure(arg + deps),
          ...      )

          >>> assert RequiresContextIOResult.from_value('a').rescue(
          ...     rescuable,
          ... )('c') == IOSuccess('a')
          >>> assert RequiresContextIOResult.from_failure('a').rescue(
          ...     rescuable,
          ... )('c') == IOFailure('ac')
          >>> assert RequiresContextIOResult.from_failure('aa').rescue(
          ...     rescuable,
          ... )('b') == IOSuccess('baa')

        """
        return RequiresContextIOResult(
            lambda deps: self(deps).rescue(
                lambda inner: function(inner)(deps),  # type: ignore
            ),
        )

    def compose_result(
        self,
        function: Callable[
            [Result[_ValueType, _ErrorType]],
            Kind3[
                'RequiresContextIOResult',
                _NewValueType,
                _ErrorType,
                _EnvType,
            ],
        ],
    ) -> 'RequiresContextIOResult[_NewValueType, _ErrorType, _EnvType]':
        """
        Composes inner ``Result`` with ``ReaderIOResult`` returning function.

        Can be useful when you need an access to both states of the result.

        .. code:: python

          >>> from returns.context import ReaderIOResult, NoDeps
          >>> from returns.io import IOSuccess, IOFailure
          >>> from returns.result import Result

          >>> def count(
          ...    container: Result[int, int],
          ... ) -> ReaderIOResult[int, int, NoDeps]:
          ...     return ReaderIOResult.from_result(
          ...         container.map(lambda x: x + 1).alt(abs),
          ...     )

          >>> success = ReaderIOResult.from_value(1)
          >>> failure = ReaderIOResult.from_failure(-1)
          >>> assert success.compose_result(count)(...) == IOSuccess(2)
          >>> assert failure.compose_result(count)(...) == IOFailure(1)

        """
        return RequiresContextIOResult(
            lambda deps: dekind(
                function(self(deps)._inner_value),  # noqa: WPS437
            )(deps),
        )

    @classmethod
    def from_result(
        cls, inner_value: 'Result[_ValueType, _ErrorType]',
    ) -> 'RequiresContextIOResult[_ValueType, _ErrorType, NoDeps]':
        """
        Creates new container with ``Result`` as a unit value.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.result import Success, Failure
          >>> from returns.io import IOSuccess, IOFailure
          >>> deps = RequiresContextIOResult.empty

          >>> assert RequiresContextIOResult.from_result(
          ...    Success(1),
          ... )(deps) == IOSuccess(1)

          >>> assert RequiresContextIOResult.from_result(
          ...    Failure(1),
          ... )(deps) == IOFailure(1)

        """
        return RequiresContextIOResult(
            lambda _: IOResult.from_result(inner_value),
        )

    @classmethod
    def from_io(
        cls,
        inner_value: IO[_NewValueType],
    ) -> 'RequiresContextIOResult[_NewValueType, Any, NoDeps]':
        """
        Creates new container from successful ``IO`` value.

        .. code:: python

          >>> from returns.io import IO, IOSuccess
          >>> from returns.context import RequiresContextIOResult

          >>> assert RequiresContextIOResult.from_io(IO(1))(
          ...     RequiresContextIOResult.empty,
          ... ) == IOSuccess(1)

        """
        return RequiresContextIOResult(
            lambda deps: IOResult.from_io(inner_value),
        )

    @classmethod
    def from_failed_io(
        cls,
        inner_value: IO[_NewErrorType],
    ) -> 'RequiresContextIOResult[Any, _NewErrorType, NoDeps]':
        """
        Creates a new container from failed ``IO`` value.

        .. code:: python

          >>> from returns.io import IO, IOFailure
          >>> from returns.context import RequiresContextIOResult

          >>> assert RequiresContextIOResult.from_failed_io(IO(1))(
          ...     RequiresContextIOResult.empty,
          ... ) == IOFailure(1)

        """
        return RequiresContextIOResult(
            lambda deps: IOResult.from_failed_io(inner_value),
        )

    @classmethod
    def from_ioresult(
        cls, inner_value: IOResult[_ValueType, _ErrorType],
    ) -> 'RequiresContextIOResult[_ValueType, _ErrorType, NoDeps]':
        """
        Creates new container with ``IOResult`` as a unit value.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess, IOFailure
          >>> deps = RequiresContextIOResult.empty

          >>> assert RequiresContextIOResult.from_ioresult(
          ...    IOSuccess(1),
          ... )(deps) == IOSuccess(1)

          >>> assert RequiresContextIOResult.from_ioresult(
          ...    IOFailure(1),
          ... )(deps) == IOFailure(1)

        """
        return RequiresContextIOResult(lambda _: inner_value)

    @classmethod
    def from_typecast(
        cls,
        inner_value:
            'RequiresContext[IOResult[_NewValueType, _NewErrorType], _EnvType]',
    ) -> 'RequiresContextIOResult[_NewValueType, _NewErrorType, _EnvType]':
        """
        You might end up with ``RequiresContext[IOResult]`` as a value.

        This method is designed to turn it into ``RequiresContextIOResult``.
        It will save all the typing information.

        It is just more useful!

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert RequiresContextIOResult.from_typecast(
          ...     RequiresContext.from_value(IOSuccess(1)),
          ... )(RequiresContextIOResult.empty) == IOSuccess(1)

          >>> assert RequiresContextIOResult.from_typecast(
          ...     RequiresContext.from_value(IOFailure(1)),
          ... )(RequiresContextIOResult.empty) == IOFailure(1)

        """
        return RequiresContextIOResult(inner_value)

    @classmethod
    def from_context(
        cls, inner_value: 'RequiresContext[_FirstType, _EnvType]',
    ) -> 'RequiresContextIOResult[_FirstType, Any, _EnvType]':
        """
        Creates new container from ``RequiresContext`` as a success unit.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> from returns.io import IOSuccess

          >>> assert RequiresContextIOResult.from_context(
          ...     RequiresContext.from_value(1),
          ... )(...) == IOSuccess(1)

        """
        return RequiresContextIOResult(
            lambda deps: IOSuccess(inner_value(deps)),
        )

    @classmethod
    def from_failed_context(
        cls, inner_value: 'RequiresContext[_FirstType, _EnvType]',
    ) -> 'RequiresContextIOResult[Any, _FirstType, _EnvType]':
        """
        Creates new container from ``RequiresContext`` as a failure unit.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> from returns.io import IOFailure

          >>> assert RequiresContextIOResult.from_failed_context(
          ...     RequiresContext.from_value(1),
          ... )(...) == IOFailure(1)

        """
        return RequiresContextIOResult(
            lambda deps: IOFailure(inner_value(deps)),
        )

    @classmethod
    def from_result_context(
        cls,
        inner_value: 'RequiresContextResult[_ValueType, _ErrorType, _EnvType]',
    ) -> 'RequiresContextIOResult[_ValueType, _ErrorType, _EnvType]':
        """
        Creates new container from ``RequiresContextResult`` as a unit value.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert RequiresContextIOResult.from_result_context(
          ...     RequiresContextResult.from_value(1),
          ... )(...) == IOSuccess(1)

          >>> assert RequiresContextIOResult.from_result_context(
          ...     RequiresContextResult.from_failure(1),
          ... )(...) == IOFailure(1)

        """
        return RequiresContextIOResult(
            lambda deps: IOResult.from_result(inner_value(deps)),
        )

    @classmethod
    def from_value(
        cls,
        inner_value: _FirstType,
    ) -> 'RequiresContextIOResult[_FirstType, Any, NoDeps]':
        """
        Creates new container with ``IOSuccess(inner_value)`` as a unit value.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess

          >>> assert RequiresContextIOResult.from_value(1)(
          ...    RequiresContextIOResult.empty,
          ... ) == IOSuccess(1)

        """
        return RequiresContextIOResult(lambda _: IOSuccess(inner_value))

    @classmethod
    def from_failure(
        cls,
        inner_value: _FirstType,
    ) -> 'RequiresContextIOResult[Any, _FirstType, NoDeps]':
        """
        Creates new container with ``IOFailure(inner_value)`` as a unit value.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOFailure

          >>> assert RequiresContextIOResult.from_failure(1)(
          ...     RequiresContextIOResult.empty,
          ... ) == IOFailure(1)

        """
        return RequiresContextIOResult(lambda _: IOFailure(inner_value))

    @classmethod
    def from_iterable(
        cls,
        inner_value:
            Iterable[
                Kind3[
                    'RequiresContextIOResult',
                    _ValueType,
                    _ErrorType,
                    _EnvType,
                ],
            ],
    ) -> 'RequiresContextIOResult[Sequence[_ValueType], _ErrorType, _EnvType]':
        """
        Transforms an iterable of ``RequiresContextIOResult`` containers.

        Returns a single container with multiple elements inside.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert RequiresContextIOResult.from_iterable([
          ...    RequiresContextIOResult.from_value(1),
          ...    RequiresContextIOResult.from_value(2),
          ... ])(...) == IOSuccess((1, 2))

          >>> assert RequiresContextIOResult.from_iterable([
          ...    RequiresContextIOResult.from_value(1),
          ...    RequiresContextIOResult.from_failure('a'),
          ... ])(...) == IOFailure('a')

          >>> assert RequiresContextIOResult.from_iterable([
          ...    RequiresContextIOResult.from_failure('a'),
          ...    RequiresContextIOResult.from_value(1),
          ... ])(...) == IOFailure('a')

        """
        return dekind(iterable_kind(cls, inner_value))


@final
class ContextIOResult(Immutable, Generic[_EnvType], metaclass=ABCMeta):
    """
    Helpers that can be used to work with ``RequiresContextIOResult`` container.

    Related to :class:`returns.context.requires_context.Context`
    and :class:`returns.context.requires_context_result.ContextResult`,
    refer there for the docs.
    """

    __slots__ = ()

    @classmethod
    def ask(cls) -> RequiresContextIOResult[_EnvType, Any, _EnvType]:
        """
        Is used to get the current dependencies inside the call stack.

        Similar to :meth:`returns.context.requires_context.Context.ask`,
        but returns ``IOResult`` instead of a regular value.

        Please, refer to the docs there to learn how to use it.

        One important note that is worth duplicating here:
        you might need to provide ``_EnvType`` explicitly,
        so ``mypy`` will know about it statically.

        .. code:: python

          >>> from returns.context import ContextIOResult
          >>> from returns.io import IOSuccess
          >>> assert ContextIOResult[int].ask().map(str)(1) == IOSuccess('1')

        """
        return RequiresContextIOResult(IOSuccess)


# Aliases:

#: Alias for a popular case when ``Result`` has ``Exception`` as error type.
RequiresContextIOResultE = RequiresContextIOResult[
    _ValueType, Exception, _EnvType,
]

#: Alias to save you some typing. Uses original name from Haskell.
ReaderIOResult = RequiresContextIOResult

#: Alias to save you some typing. Uses ``Exception`` as error type.
ReaderIOResultE = RequiresContextIOResult[_ValueType, Exception, _EnvType]
