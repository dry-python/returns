from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Generic,
    TypeVar,
    Union,
)

from typing_extensions import final

from returns.context import NoDeps
from returns.primitives.container import BaseContainer
from returns.primitives.types import Immutable
from returns.result import Failure, Result, Success

if TYPE_CHECKING:
    from returns.context.requires_context import RequiresContext

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
class RequiresContextResult(
    BaseContainer,
    Generic[_EnvType, _ValueType, _ErrorType],
):
    """
    The ``RequiresContextResult`` combinator.

    See :class:`returns.context.requires_context.RequiresContext` for more docs.

    This is just a handy wrapper around ``RequiresContext[env, Result[a, b]]``
    which represents a context-dependent pure operation
    that might fail and return :class:`returns.result.Result`.

    It has several important differences from the regular ``Result`` classes.
    It does not have ``Success`` and ``Failure`` subclasses.
    Because, the computation is not yet performed.
    And we cannot know the type in advance.

    So, this is a thin wrapper, without any changes in logic.

    Why do we need this wrapper? That's just for better usability!

    .. code:: python

      >>> from returns.context import RequiresContext
      >>> from returns.result import Success, Result

      >>> def function(arg: int) -> Result[int, str]:
      ...      return Success(arg + 1)

      >>> # Without wrapper:
      >>> assert RequiresContext.from_value(Success(1)).map(
      ...     lambda result: result.bind(function),
      ... )(...) == Success(2)

      >>> # With wrapper:
      >>> assert RequiresContextResult.from_value(1).bind_result(
      ...     function,
      ... )(...) == Success(2)

    This way ``RequiresContextResult`` allows to simply work with:

    - raw values and pure functions
    - ``RequiresContext`` values and pure functions returning it
    - ``Result`` and functions returning it

    Important implementation detail:
    due it is meaning, ``RequiresContextResult``
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

    #: This field has an extra 'RequiresContext' just because `mypy` needs it.
    _inner_value: Callable[
        ['RequiresContextResult', _EnvType],
        Result[_ValueType, _ErrorType],
    ]

    #: A convinient placeholder to call methods created by `.from_value()`.
    empty: ClassVar[NoDeps] = object()

    def __init__(
        self,
        inner_value: Callable[[_EnvType], Result[_ValueType, _ErrorType]],
    ) -> None:
        """
        Public constructor for this type. Also required for typing.

        Only allows functions of kind ``* -> *``
        and returning :class:`returns.result.Result` instances.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success
          >>> str(RequiresContextResult(lambda deps: Success(deps + 1)))
          '<RequiresContextResult: <function <lambda> at ...>>'

        """
        super().__init__(inner_value)

    def __call__(self, deps: _EnvType) -> Result[_ValueType, _ErrorType]:
        """
        Evaluates the wrapped function.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success
          >>> def first(lg: bool) -> RequiresContextResult[float, int, str]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContextResult(
          ...         lambda deps: Success(deps if lg else -deps),
          ...     )

          >>> instance = first(False)
          >>> assert instance(3.5) == Success(-3.5)

        In other things, it is a regular Python magic method.

        """
        return self._inner_value(deps)

    def map(  # noqa: WPS125
        self, function: Callable[[_ValueType], _NewValueType],
    ) -> 'RequiresContextResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Composes successful container with a pure function.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success, Failure

          >>> assert RequiresContextResult.from_value(1).map(
          ...     lambda x: x + 1,
          ... )(...) == Success(2)

          >>> assert RequiresContextResult.from_failure(1).map(
          ...     lambda x: x + 1,
          ... )(...) == Failure(1)

        """
        return RequiresContextResult(lambda deps: self(deps).map(function))

    def apply(
        self,
        container: 'RequiresContextResult['
            '_EnvType, Callable[[_ValueType], _NewValueType], _ErrorType]',
    ) -> 'RequiresContextResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Calls a wrapped function in a container on this container.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success, Failure, Result

          >>> def transform(arg: str) -> str:
          ...     return arg + 'b'

          >>> assert RequiresContextResult.from_value('a').apply(
          ...    RequiresContextResult.from_value(transform),
          ... )(...) == Success('ab')

          >>> assert RequiresContextResult.from_failure('a').apply(
          ...    RequiresContextResult.from_value(transform),
          ... )(...) == Failure('a')

          >>> assert isinstance(RequiresContextResult.from_value('a').apply(
          ...    RequiresContextResult.from_failure(transform),
          ... )(...), Result.failure_type) is True

        """
        return RequiresContextResult(
            lambda deps: self(deps).apply(container(deps)),
        )

    def bind(
        self,
        function: Callable[
            [_ValueType],
            'RequiresContextResult[_EnvType, _NewValueType, _ErrorType]',
        ],
    ) -> 'RequiresContextResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Composes this container with a function returning the same type.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success, Failure

          >>> def first(lg: bool) -> RequiresContextResult[float, int, int]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContextResult(
          ...         lambda deps: Success(deps) if lg else Failure(-deps),
          ...     )

          >>> def second(
          ...     number: int,
          ... ) -> RequiresContextResult[float, str, int]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContextResult(
          ...         lambda deps: Success('>=' if number >= deps else '<'),
          ...     )

          >>> assert first(True).bind(second)(1) == Success('>=')
          >>> assert first(False).bind(second)(2) == Failure(-2)

        """
        return RequiresContextResult(
            lambda deps: self(deps).bind(
                lambda inner: function(inner)(deps),  # type: ignore
            ),
        )

    def bind_result(
        self,
        function: Callable[[_ValueType], Result[_NewValueType, _ErrorType]],
    ) -> 'RequiresContextResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Binds ``Result`` returning function to current container.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success, Failure, Result
          >>> def function(number: int) -> Result[int, str]:
          ...     if number > 0:
          ...         return Success(number + 1)
          ...     return Failure('<0')

          >>> assert RequiresContextResult.from_value(1).bind_result(
          ...     function,
          ... )(RequiresContextResult.empty) == Success(2)

          >>> assert RequiresContextResult.from_value(0).bind_result(
          ...     function,
          ... )(RequiresContextResult.empty) == Failure('<0')

          >>> assert RequiresContextResult.from_failure(':(').bind_result(
          ...     function,
          ... )(RequiresContextResult.empty) == Failure(':(')

        """
        return RequiresContextResult(lambda deps: self(deps).bind(function))

    def bind_context(
        self,
        function: Callable[
            [_ValueType],
            'RequiresContext[_EnvType, _NewValueType]',
        ],
    ) -> 'RequiresContextResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Binds ``RequiresContext`` returning function to current container.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> from returns.result import Success, Failure
          >>> def function(arg: int) -> RequiresContext[str, int]:
          ...     return RequiresContext(lambda deps: len(deps) + arg)

          >>> assert function(2)('abc') == 5

          >>> assert RequiresContextResult.from_value(2).bind_context(
          ...     function,
          ... )('abc') == Success(5)

          >>> assert RequiresContextResult.from_failure(2).bind_context(
          ...     function,
          ... )('abc') == Failure(2)

        """
        return RequiresContextResult(
            lambda deps: self(deps).map(
                lambda inner: function(inner)(deps),  # type: ignore
            ),
        )

    def fix(
        self, function: Callable[[_ErrorType], _NewValueType],
    ) -> 'RequiresContextResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Composes failed container with a pure function.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success

          >>> assert RequiresContextResult.from_value(1).fix(
          ...     lambda x: x + 1,
          ... )(...) == Success(1)

          >>> assert RequiresContextResult.from_failure(1).fix(
          ...     lambda x: x + 1,
          ... )(...) == Success(2)

        """
        return RequiresContextResult(lambda deps: self(deps).fix(function))

    def alt(
        self, function: Callable[[_ErrorType], _NewErrorType],
    ) -> 'RequiresContextResult[_EnvType, _ValueType, _NewErrorType]':
        """
        Composes failed container with a pure function.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success, Failure

          >>> assert RequiresContextResult.from_value(1).alt(
          ...     lambda x: x + 1,
          ... )(...) == Success(1)

          >>> assert RequiresContextResult.from_failure(1).alt(
          ...     lambda x: x + 1,
          ... )(...) == Failure(2)

        """
        return RequiresContextResult(lambda deps: self(deps).alt(function))

    def rescue(
        self,
        function: Callable[
            [_ErrorType],
            'RequiresContextResult[_EnvType, _ValueType, _NewErrorType]',
        ],
    ) -> 'RequiresContextResult[_EnvType, _ValueType, _NewErrorType]':
        """
        Composes this container with a function returning the same type.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success, Failure

          >>> def rescuable(arg: str) -> RequiresContextResult[str, str, str]:
          ...      if len(arg) > 1:
          ...          return RequiresContextResult(
          ...              lambda deps: Success(deps + arg),
          ...          )
          ...      return RequiresContextResult(
          ...          lambda deps: Failure(arg + deps),
          ...      )

          >>> assert RequiresContextResult.from_value('a').rescue(
          ...     rescuable,
          ... )('c') == Success('a')
          >>> assert RequiresContextResult.from_failure('a').rescue(
          ...     rescuable,
          ... )('c') == Failure('ac')
          >>> assert RequiresContextResult.from_failure('aa').rescue(
          ...     rescuable,
          ... )('b') == Success('baa')

        """
        return RequiresContextResult(
            lambda deps: self(deps).rescue(
                lambda inner: function(inner)(deps),  # type: ignore
            ),
        )

    def value_or(
        self, default_value: _FirstType,
    ) -> Callable[[_EnvType], Union[_ValueType, _FirstType]]:
        """
        Returns a callable that either returns a success or default value.

        .. code:: python

          >>> from returns.context import RequiresContextResult

          >>> assert RequiresContextResult.from_value(1).value_or(2)(
          ...     RequiresContextResult.empty,
          ... ) == 1

          >>> assert RequiresContextResult.from_failure(1).value_or(2)(
          ...     RequiresContextResult.empty,
          ... ) == 2

        """
        return lambda deps: self(deps).value_or(default_value)

    def unwrap(self) -> Callable[[_EnvType], _ValueType]:
        """
        Returns a callable that unwraps success value or raises exception.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success, Failure

          >>> assert RequiresContextResult(
          ...    lambda _: Success(1),
          ... ).unwrap()(RequiresContextResult.empty) == 1

        .. code::

          >>> RequiresContextResult(
          ...    lambda _: Failure(1),
          ... ).unwrap()(RequiresContextResult.empty)
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
        return lambda deps: self(deps).unwrap()

    def failure(self) -> Callable[[_EnvType], _ErrorType]:
        """
        Returns a callable that unwraps failure value or raises exception.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success, Failure

          >>> assert RequiresContextResult(
          ...    lambda _: Failure(1),
          ... ).failure()(RequiresContextResult.empty) == 1

        .. code::

          >>> RequiresContextResult(
          ...    lambda _: Success(1),
          ... ).failure()(RequiresContextResult.empty)
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
        return lambda deps: self(deps).failure()

    @classmethod
    def lift_context(
        cls,
        function: Callable[
            [_ValueType],
            'RequiresContext[_EnvType, _NewValueType]',
        ],
    ) -> Callable[
        ['RequiresContextResult[_EnvType, _ValueType, _ErrorType]'],
        'RequiresContextResult[_EnvType, _NewValueType, _ErrorType]',
    ]:
        """
        Lifts function from ``RequiresContext`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> RequiresContext[env, b]`` to:
        ``RequiresContextResult[env, a, c]``
        -> ``RequiresContextResult[env, b, c]``

        Similar to :meth:`~RequiresContextResult.lift`,
        but works with other type.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> from returns.result import Success, Failure

          >>> def function(arg: int) -> RequiresContext[str, int]:
          ...     return RequiresContext(lambda deps: len(deps) + arg)

          >>> assert RequiresContextResult.lift_context(function)(
          ...     RequiresContextResult.from_value(2),
          ... )('abc') == Success(5)

          >>> assert RequiresContextResult.lift_context(function)(
          ...     RequiresContextResult.from_failure(0),
          ... )('abc') == Failure(0)

        """
        return lambda container: container.bind_context(function)

    @classmethod
    def from_result(
        cls, inner_value: Result[_ValueType, _ErrorType],
    ) -> 'RequiresContextResult[Any, _ValueType, _ErrorType]':
        """
        Creates new container with ``Result`` as a unit value.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success, Failure
          >>> deps = RequiresContextResult.empty

          >>> assert RequiresContextResult.from_result(
          ...    Success(1),
          ... )(deps) == Success(1)

          >>> assert RequiresContextResult.from_result(
          ...    Failure(1),
          ... )(deps) == Failure(1)

        """
        return RequiresContextResult(lambda _: inner_value)

    @classmethod
    def from_typecast(
        cls,
        container:
            'RequiresContext[_EnvType, Result[_NewValueType, _NewErrorType]]',
    ) -> 'RequiresContextResult[_EnvType, _NewValueType, _NewErrorType]':
        """
        You might end up with ``RequiresContext[Result[...]]`` as a value.

        This method is designed to turn it into ``RequiresContextResult``.
        It will save all the typing information.

        It is just more useful!

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> from returns.result import Success, Failure

          >>> assert RequiresContextResult.from_typecast(
          ...     RequiresContext.from_value(Success(1)),
          ... )(RequiresContextResult.empty) == Success(1)

          >>> assert RequiresContextResult.from_typecast(
          ...     RequiresContext.from_value(Failure(1)),
          ... )(RequiresContextResult.empty) == Failure(1)

        """
        return RequiresContextResult(container)

    @classmethod
    def from_context(
        cls, inner_value: 'RequiresContext[_EnvType, _FirstType]',
    ) -> 'RequiresContextResult[_EnvType, _FirstType, Any]':
        """
        Creates new container from ``RequiresContext`` as a success unit.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> from returns.result import Success
          >>> assert RequiresContextResult.from_context(
          ...     RequiresContext.from_value(1),
          ... )(...) == Success(1)

        """
        return RequiresContextResult(lambda deps: Success(inner_value(deps)))

    @classmethod
    def from_failed_context(
        cls, inner_value: 'RequiresContext[_EnvType, _FirstType]',
    ) -> 'RequiresContextResult[_EnvType, Any, _FirstType]':
        """
        Creates new container from ``RequiresContext`` as a failure unit.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> from returns.result import Failure
          >>> assert RequiresContextResult.from_failed_context(
          ...     RequiresContext.from_value(1),
          ... )(...) == Failure(1)

        """
        return RequiresContextResult(lambda deps: Failure(inner_value(deps)))

    @classmethod
    def from_value(
        cls, inner_value: _FirstType,
    ) -> 'RequiresContextResult[Any, _FirstType, Any]':
        """
        Creates new container with ``Success(inner_value)`` as a unit value.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success
          >>> assert RequiresContextResult.from_value(1)(...) == Success(1)

        """
        return RequiresContextResult(lambda _: Success(inner_value))

    @classmethod
    def from_failure(
        cls, inner_value: _FirstType,
    ) -> 'RequiresContextResult[Any, Any, _FirstType]':
        """
        Creates new container with ``Failure(inner_value)`` as a unit value.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Failure
          >>> assert RequiresContextResult.from_failure(1)(...) == Failure(1)

        """
        return RequiresContextResult(lambda _: Failure(inner_value))


@final
class ContextResult(Immutable, Generic[_EnvType]):
    """
    Helpers that can be used to work with ``RequiresContextResult`` container.

    Related to :class:`returns.context.Context`, refer there for the docs.
    """

    @classmethod
    def ask(cls) -> RequiresContextResult[_EnvType, _EnvType, Any]:
        """
        Is used to get the current dependencies inside the call stack.

        Similar to :meth:`returns.context.Context.ask`,
        but returns ``Result`` instead of a regular value.

        Please, refer to the docs there to learn how to use it.

        One important note that is worth duplicating here:
        you might need to provide ``_EnvType`` explicitly,
        so ``mypy`` will know about it statically.

        .. code:: python

          >>> from returns.context import ContextResult
          >>> from returns.result import Success
          >>> assert ContextResult[int].ask().map(str)(1) == Success('1')

        """
        return RequiresContextResult(Success)


# Aliases:

#: Alias for a popular case when ``Result`` has ``Exception`` as error type.
RequiresContextResultE = RequiresContextResult[
    _EnvType, _ValueType, Exception,
]

#: Alias to save you some typing. Uses original name from Haskell.
ReaderResult = RequiresContextResult[_EnvType, _ValueType, _ErrorType]

#: Alias to save you some typing. Has ``Exception`` as error type.
ReaderResultE = RequiresContextResult[_EnvType, _ValueType, Exception]
