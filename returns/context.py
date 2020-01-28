# -*- coding: utf-8 -*-

from abc import ABCMeta
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    NoReturn,
    Type,
    TypeVar,
    Union,
)

from typing_extensions import final

from returns.functions import identity
from returns.primitives.container import BaseContainer
from returns.result import Failure, Result, Success

# Context:
_EnvType = TypeVar('_EnvType', contravariant=True)
_ReturnType = TypeVar('_ReturnType', covariant=True)
_NewReturnType = TypeVar('_NewReturnType')

# Result:
_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType', covariant=True)
_NewErrorType = TypeVar('_NewErrorType')

# Helpers:
_FirstType = TypeVar('_FirstType')


@final
class RequiresContext(
    BaseContainer,
    Generic[_EnvType, _ReturnType],
):
    """
    The ``RequiresContext`` container.

    It's main purpose is to wrap some specific function
    and give tools to compose other functions around it
    without the actual calling it.

    The ``RequiresContext`` container pass the state
    you want to share between functions.
    Functions may read that state, but can't change it.
    The ``RequiresContext`` container
    lets us access shared immutable state within a specific context.

    It can be used for lazy evaluation and typed dependency injection.

    ``RequiresContext`` is used with functions that never fails.
    If you want to use ``RequiresContext`` with returns ``Result``
    than consider using ``RequiresContextResult`` instead.

    Note:
        This container does not wrap ANY value. It wraps only functions.
        You won't be able to supply arbitarry types!

    See also:
        https://dev.to/gcanti/getting-started-with-fp-ts-reader-1ie5
        https://en.wikipedia.org/wiki/Lazy_evaluation
        https://bit.ly/2R8l4WK

    """

    #: This field has an extra 'RequiresContext' just because `mypy` needs it.
    _inner_value: Callable[['RequiresContext', _EnvType], _ReturnType]

    #: A convinient placeholder to call methods created by `.from_value()`:
    empty: ClassVar[Any] = object()

    def __init__(
        self, inner_value: Callable[[_EnvType], _ReturnType],
    ) -> None:
        """
        Public constructor for this type. Also required for typing.

        Only allows functions of kind ``* -> *``.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> str(RequiresContext(lambda deps: deps + 1))
          '<RequiresContext: <function <lambda> at ...>>'

        """
        super().__init__(inner_value)

    def __call__(self, deps: _EnvType) -> _ReturnType:
        """
        Evaluates the wrapped function.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> def first(lg: bool) -> RequiresContext[float, int]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContext(
          ...         lambda deps: deps if lg else -deps,
          ...     )
          ...
          >>> instance = first(False)  # creating `RequiresContext` instance
          >>> instance(3.5)  # calling it with `__call__`
          -3.5

        In other things, it is a regular python magic method.
        """
        return self._inner_value(deps)

    def map(  # noqa: A003
        self, function: Callable[[_ReturnType], _NewReturnType],
    ) -> 'RequiresContext[_EnvType, _NewReturnType]':
        """
        Allows to compose functions inside the wrapped container.

        Here's how it works:

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> def first(lg: bool) -> RequiresContext[float, int]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContext(
          ...         lambda deps: deps if lg else -deps,
          ...     )
          ...
          >>> first(True).map(lambda number: number * 10)(2.5)
          25.0
          >>> first(False).map(lambda number: number * 10)(0.1)
          -1.0

        """
        return RequiresContext(lambda deps: function(self(deps)))

    def bind(
        self,
        function: Callable[
            [_ReturnType],
            'RequiresContext[_EnvType, _NewReturnType]',
        ],
    ) -> 'RequiresContext[_EnvType, _NewReturnType]':
        """
        Composes a container with a function returning another container.

        This is useful when you do several computations
        that relies on the same context.

        .. code:: python

          >>> from returns.context import RequiresContext

          >>> def first(lg: bool) -> RequiresContext[float, int]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContext(
          ...         lambda deps: deps if lg else -deps,
          ...     )
          ...

          >>> def second(number: int) -> RequiresContext[float, str]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContext(
          ...         lambda deps: '>=' if number >= deps else '<',
          ...     )
          ...

          >>> first(True).bind(second)(1)
          '>='
          >>> first(False).bind(second)(2)
          '<'

        """
        return RequiresContext(lambda deps: function(self(deps))(deps))

    @classmethod
    def lift(
        cls,
        function: Callable[[_ReturnType], _NewReturnType],
    ) -> Callable[
        ['RequiresContext[_EnvType, _ReturnType]'],
        'RequiresContext[_EnvType, _NewReturnType]',
    ]:
        """
        Lifts function to be wrapped in a container for better composition.

        In other words, it modifies the function's
        signature from: ``a -> b`` to:
        ``RequiresContext[env, a] -> RequiresContext[env, b]``

        Works similar to :meth:`~RequiresContext.map`,
        but has inverse semantics.

        This is how it should be used:

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> def example(argument: int) -> float:
          ...     return argument / 2
          ...

          >>> container = RequiresContext.lift(example)(
          ...     RequiresContext.from_value(2),
          ... )
          >>> container(RequiresContext.empty)
          1.0

        See also:
            - https://wiki.haskell.org/Lifting
            - https://github.com/witchcrafters/witchcraft
            - https://en.wikipedia.org/wiki/Natural_transformation

        """
        return lambda container: container.map(function)

    @classmethod
    def from_value(
        cls, inner_value: _FirstType,
    ) -> 'RequiresContext[Any, _FirstType]':
        """
        Used to return some specific value from the container.

        Consider this method as a some kind of factory.
        Passed value will be a return type.
        Make sure to use :attr:`~RequiresContext.empty`
        for getting the unit value.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> unit = RequiresContext.from_value(5)
          >>> assert unit(RequiresContext.empty) == 5

        Might be used with or without direct type hint.

        """
        return RequiresContext(lambda _: inner_value)


@final
class Context(Generic[_EnvType]):
    """
    Helpers that can be used to work with ``RequiresContext`` container.

    Some of them requires explicit type to be specified.

    This class contains methods that do require
    to explicitly set type annotations. Why?
    Because it is impossible to figure out type without them.

    So, here's how you should use them:

    .. code:: python

      Context[Dict[str, str]].ask()

    Otherwise, your ``.ask()`` method
    will return ``RequiresContext[<nothing>, <nothing>]``,
    which is unsable:

    .. code:: python

      env = Context.ask()
      env(some_deps)

    And ``mypy`` will warn you: ``error: Need type annotation for 'a'``

    """

    @classmethod
    def ask(cls) -> RequiresContext[_EnvType, _EnvType]:
        """
        Get current context to use the depedencies.

        It is a common scenarion when you need to use the environment.
        For example, you want to do some context-related computation,
        but you don't have the context instance at your disposal.
        That's where ``.ask()`` becomes useful!

        .. code:: python

          >>> from typing_extensions import TypedDict
          >>> class Deps(TypedDict):
          ...     message: str
          ...

          >>> def first(lg: bool) -> RequiresContext[Deps, int]:
          ...     # `deps` has `Deps` type here:
          ...     return RequiresContext(
          ...         lambda deps: deps['message'] if lg else 'error',
          ...     )
          ...

          >>> def second(text: str) -> RequiresContext[int, int]:
          ...     return first(len(text) > 3)
          ...

          >>> assert second('abc')({'message': 'ok'}) == 'error'
          >>> assert second('abcd')({'message': 'ok'}) == 'ok'

        And now imagine that you have to change this ``3`` limit.
        And you want to be able to set it via environment as well.
        Ok, let's fix it with the power of ``Context.ask()``!

        .. code:: python

          >>> from typing_extensions import TypedDict
          >>> class Deps(TypedDict):
          ...     message: str
          ...     limit: int   # note this new field!
          ...

          >>> def new_first(lg: bool) -> RequiresContext[Deps, int]:
          ...     # `deps` has `Deps` type here:
          ...     return RequiresContext(
          ...         lambda deps: deps['message'] if lg else 'error',
          ...     )
          ...

          >>> def new_second(text: str) -> RequiresContext[int, int]:
          ...     return Context[Deps].ask().bind(
          ...         lambda deps: new_first(len(text) > deps.get('limit', 3)),
          ...     )
          ...

          >>> assert new_second('abc')({'message': 'ok', 'limit': 2}) == 'ok'
          >>> assert new_second('abcd')({'message': 'ok'}) == 'ok'
          >>> new_second('abcd')({'message': 'ok', 'limit': 5})
          'error'

        That's how ``ask`` works and can be used.

        See also:
            https://dev.to/gcanti/getting-started-with-fp-ts-reader-1ie5

        """
        return RequiresContext(identity)


class RequiresContextResult(
    BaseContainer,
    Generic[_EnvType, _ValueType, _ErrorType],
):
    """

    See also:
        https://bit.ly/2RwP4fp

    """

    #: This field has an extra 'RequiresContext' just because `mypy` needs it.
    _inner_value: Callable[
        ['RequiresContextResult', _EnvType],
        Result[_ValueType, _ErrorType],
    ]

#: A convinient placeholder to call methods created by `.from_value()`:
    empty: ClassVar[Any] = object()

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
          >>> def first(lg: bool) -> RequiresContextResult[float, int, str]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContext(
          ...         lambda deps: deps if lg else -deps,
          ...     )
          ...
          >>> instance = first(False)  # creating `RequiresContext` instance
          >>> assert instance(3.5) == -3.5  # calling it with `__call__`

        In other things, it is a regular python magic method.
        """
        return self._inner_value(deps)

    def map(
        self, function: Callable[[_ValueType], _NewValueType],
    ) -> 'RequiresContextResult[_EnvType, _NewValueType, _ErrorType]':
        return RequiresContextResult(lambda deps: self(deps).map(function))

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
          ...

          >>> def second(
          ...     number: int,
          ... ) -> RequiresContextResult[float, str, int]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContextResult(
          ...         lambda deps: Success('>=' if number >= deps else '<'),
          ...     )
          ...

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
          ...

          >>> assert RequiresContextResult.from_success(1).bind_result(
          ...     function,
          ... )(RequiresContextResult.empty) == Success(2)

          >>> assert RequiresContextResult.from_success(0).bind_result(
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
            RequiresContext[_EnvType, _NewValueType],
        ],
    ) -> 'RequiresContextResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Binds ``RequiresContext`` returning function to current container.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> from returns.result import Success, Failure, Result
          >>> def function(arg: int) -> RequiresContext[str, int]:
          ...     return RequiresContext(lambda deps: len(deps) + arg)
          ...
          >>> assert function(2)('abc') == 5

          >>> assert RequiresContextResult.from_success(2).bind_context(
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
        return RequiresContextResult(lambda deps: self(deps).fix(function))

    def alt(
        self, function: Callable[[_ErrorType], _NewErrorType],
    ) -> 'RequiresContextResult[_EnvType, _ValueType, _NewErrorType]':
        return RequiresContextResult(lambda deps: self(deps).alt(function))

    def rescue(
        self,
        function: Callable[
            [_ErrorType],
            'RequiresContextResult[_EnvType, _ValueType, _NewErrorType]',
        ],
    ):
        """Composes this container with a function returning the same type."""
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
          >>> from returns.result import Success, Failure

          >>> assert RequiresContextResult(
          ...    lambda _: Success(1),
          ... ).value_or(2)(RequiresContextResult.empty) == 1

          >>> assert RequiresContextResult(
          ...    lambda _: Failure(1),
          ... ).value_or(2)(RequiresContextResult.empty) == 2

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
    def lift(
        cls,
        function: Callable[[_ValueType], _NewValueType],
    ) -> Callable[
        ['RequiresContextResult[_EnvType, _ValueType, _ErrorType]'],
        'RequiresContextResult[_EnvType, _NewValueType, _ErrorType]',
    ]:
        """
        Lifts function to be wrapped in a conatiner for better composition.

        In other words, it modifies the function's
        signature from: ``a -> b`` to:
        ``RequiresContextResult[env, a, err]``
        -> ``RequiresContextResult[env, b, err]``

        Works similar to :meth:`~RequiresContextResult.map`,
        but has inverse semantics.

        This is how it should be used:

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success

          >>> def function(arg: int) -> str:
          ...     return str(arg) + '!'
          ...
          >>> unit = RequiresContextResult.from_success(1)
          >>> deps = RequiresContextResult.empty
          >>> assert RequiresContextResult.lift(function)(
          ...     unit,
          ... )(deps) == Success('1!')

        See also:
            - https://wiki.haskell.org/Lifting
            - https://github.com/witchcrafters/witchcraft
            - https://en.wikipedia.org/wiki/Natural_transformation

        """
        return lambda container: container.map(function)

    @classmethod
    def lift_result(
        cls,
        function: Callable[[_ValueType], Result[_NewValueType, _ErrorType]],
    ) -> Callable[
        ['RequiresContextResult[_EnvType, _ValueType, _ErrorType]'],
        'RequiresContextResult[_EnvType, _NewValueType, _ErrorType]',
    ]:
        """
        Lifts function from ``Result`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> Result[b, c]`` to:
        ``RequiresContextResult[env, a, c]``
        -> ``RequiresContextResult[env, b, c]``

        Similar to :meth:`~RequiresContextResult.lift`,
        but works with other type.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success, Failure, Result

          >>> def function(arg: int) -> Result[str, int]:
          ...     if arg > 0:
          ...         return Success(str(arg) + '!')
          ...     return Failure(arg)
          ...
          >>> deps = RequiresContextResult.empty

          >>> assert RequiresContextResult.lift_result(function)(
          ...     RequiresContextResult.from_success(1),
          ... )(deps) == Success('1!')

          >>> assert RequiresContextResult.lift_result(function)(
          ...     RequiresContextResult.from_success(0),
          ... )(deps) == Failure(0)

          >>> assert RequiresContextResult.lift_result(function)(
          ...     RequiresContextResult.from_failure('nope'),
          ... )(deps) == Failure('nope')

        """
        return lambda container: container.bind_result(function)

    @classmethod
    def lift_context(
        cls,
        function: Callable[
            [_ValueType],
            RequiresContext[_EnvType, _NewValueType],
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
          ...

          >>> assert RequiresContextResult.lift_context(function)(
          ...     RequiresContextResult.from_success(2),
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
        cls, container: RequiresContext[
            _EnvType, Result[_NewValueType, _NewErrorType],
        ],
    ) -> 'RequiresContextResult[_EnvType, _NewValueType, _NewErrorType]':
        """
        You might end up with ``RequiresContext[Result]`` as a value.

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
        return RequiresContextResult(lambda deps: container(deps))

    @classmethod
    def from_successful_context(
        cls, inner_value: RequiresContext[_EnvType, _ReturnType],
    ) -> 'RequiresContextResult[_EnvType, _ReturnType, Any]':
        """
        Creates new container from ``RequiresContext`` as a success unit.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> from returns.result import Success
          >>> assert RequiresContextResult.from_successful_context(
          ...     RequiresContext.from_value(1),
          ... )(...) == Success(1)

        """
        return RequiresContextResult(lambda deps: Success(inner_value(deps)))

    @classmethod
    def from_failed_context(
        cls, inner_value: RequiresContext[_EnvType, _ReturnType],
    ) -> 'RequiresContextResult[_EnvType, Any, _ReturnType]':
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
    def from_success(
        cls, inner_value: _FirstType,
    ) -> 'RequiresContextResult[Any, _FirstType, Any]':
        """
        Creates new container with ``Success(inner_value)`` as a unit value.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success
          >>> assert RequiresContextResult.from_success(1)(...) == Success(1)

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
class ContextResult(Generic[_EnvType]):
    @classmethod
    def ask(cls) -> RequiresContextResult[_EnvType, _EnvType, Any]:
        return RequiresContextResult(Success)


# Aliases:

#: Alias for a popular case when ``Result`` has ``Exception`` as error type.
RequiresContextResultE = RequiresContextResult[
    _EnvType, _ValueType, Exception,
]
