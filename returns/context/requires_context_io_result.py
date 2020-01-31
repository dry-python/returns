# -*- coding: utf-8 -*-

from typing import Any, Callable, ClassVar, Generic, TypeVar, Union

from typing_extensions import final

from returns.context.requires_context import RequiresContext
from returns.context.requires_context_result import RequiresContextResult
from returns.io import IO, IOFailure, IOResult, IOSuccess
from returns.primitives.container import BaseContainer
from returns.primitives.types import Immutable
from returns.result import Result

# Context:
_EnvType = TypeVar('_EnvType', contravariant=True)

# Result:
_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType', covariant=True)
_NewErrorType = TypeVar('_NewErrorType')

# Helpers:
_FirstType = TypeVar('_FirstType')


class RequiresContextIOResult(
    BaseContainer,
    Generic[_EnvType, _ValueType, _ErrorType],
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
      >>> assert RequiresContextIOResult.from_success(1).bind_ioresult(
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

    Imporatant implementation detail:
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

    #: This field has an extra 'RequiresContext' just because `mypy` needs it.
    _inner_value: Callable[
        ['RequiresContextIOResult', _EnvType],
        IOResult[_ValueType, _ErrorType],
    ]

    #: A convinient placeholder to call methods created by `.from_value()`.
    empty: ClassVar[Any] = object()

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
          >>> def first(lg: bool) -> RequiresContextIOResult[float, int, str]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContext(
          ...         lambda deps: IOSuccess(deps if lg else -deps),
          ...     )
          ...
          >>> instance = first(False)
          >>> assert instance(3.5) == IOSuccess(-3.5)

        In other things, it is a regular python magic method.

        """
        return self._inner_value(deps)

    def map(  # noqa: A003
        self, function: Callable[[_ValueType], _NewValueType],
    ) -> 'RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Composes successful container with a pure function.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert RequiresContextIOResult.from_success(1).map(
          ...     lambda x: x + 1,
          ... )(...) == IOSuccess(2)

          >>> assert RequiresContextIOResult.from_failure(1).map(
          ...     lambda x: x + 1,
          ... )(...) == IOFailure(1)

        """
        return RequiresContextIOResult(lambda deps: self(deps).map(function))

    def bind(
        self,
        function: Callable[
            [_ValueType],
            'RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]',
        ],
    ) -> 'RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Composes this container with a function returning the same type.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> def first(lg: bool) -> RequiresContextIOResult[float, int, int]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContextIOResult(
          ...         lambda deps: IOSuccess(deps) if lg else IOFailure(-deps),
          ...     )
          ...

          >>> def second(
          ...     number: int,
          ... ) -> RequiresContextIOResult[float, str, int]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContextIOResult(
          ...         lambda deps: IOSuccess('>=' if number >= deps else '<'),
          ...     )
          ...

          >>> assert first(True).bind(second)(1) == IOSuccess('>=')
          >>> assert first(False).bind(second)(2) == IOFailure(-2)

        """
        return RequiresContextIOResult(
            lambda deps: self(deps).bind(
                lambda inner: function(inner)(deps),  # type: ignore
            ),
        )

    def bind_result(
        self,
        function: Callable[[_ValueType], Result[_NewValueType, _ErrorType]],
    ) -> 'RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Binds ``Result`` returning function to the current container.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.result import Success, Failure, Result
          >>> from returns.io import IOSuccess, IOFailure
          >>> def function(number: int) -> Result[int, str]:
          ...     if number > 0:
          ...         return Success(number + 1)
          ...     return Failure('<0')
          ...

          >>> assert RequiresContextIOResult.from_success(1).bind_result(
          ...     function,
          ... )(RequiresContextIOResult.empty) == IOSuccess(2)

          >>> assert RequiresContextIOResult.from_success(0).bind_result(
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
            RequiresContext[_EnvType, _NewValueType],
        ],
    ) -> 'RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Binds ``RequiresContext`` returning function to current container.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> from returns.io import IOSuccess, IOFailure

          >>> def function(arg: int) -> RequiresContext[str, int]:
          ...     return RequiresContext(lambda deps: len(deps) + arg)
          ...
          >>> assert function(2)('abc') == 5

          >>> assert RequiresContextIOResult.from_success(2).bind_context(
          ...     function,
          ... )('abc') == IOSuccess(5)

          >>> assert RequiresContextIOResult.from_failure(2).bind_context(
          ...     function,
          ... )('abc') == IOFailure(2)

        """
        return RequiresContextIOResult(
            lambda deps: self(deps).map(
                lambda inner: function(inner)(deps),  # type: ignore
            ),
        )

    def bind_context_result(
        self,
        function: Callable[
            [_ValueType],
            RequiresContextResult[_EnvType, _NewValueType, _ErrorType],
        ],
    ) -> 'RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Binds ``RequiresContextResult`` returning function to the current one.

        .. code:: python

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
          ...
          >>> assert function(2)('abc') == Success(5)
          >>> assert function(-1)('abc') == Failure(2)

          >>> assert RequiresContextIOResult.from_success(
          ...    2,
          ... ).bind_context_result(
          ...     function,
          ... )('abc') == IOSuccess(5)

          >>> assert RequiresContextIOResult.from_success(
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
                lambda inner: function(inner)(deps),  # type: ignore
            ),
        )

    def bind_ioresult(
        self,
        function: Callable[[_ValueType], IOResult[_NewValueType, _ErrorType]],
    ) -> 'RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Binds ``IOResult`` returning function to the current container.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> def function(number: int) -> IOResult[int, str]:
          ...     if number > 0:
          ...         return IOSuccess(number + 1)
          ...     return IOFailure('<0')
          ...

          >>> assert RequiresContextIOResult.from_success(1).bind_ioresult(
          ...     function,
          ... )(RequiresContextIOResult.empty) == IOSuccess(2)

          >>> assert RequiresContextIOResult.from_success(0).bind_ioresult(
          ...     function,
          ... )(RequiresContextIOResult.empty) == IOFailure('<0')

          >>> assert RequiresContextIOResult.from_failure(':(').bind_ioresult(
          ...     function,
          ... )(RequiresContextIOResult.empty) == IOFailure(':(')

        """
        return RequiresContextIOResult(
            lambda deps: self(deps).bind(function),
        )

    def fix(
        self, function: Callable[[_ErrorType], _NewValueType],
    ) -> 'RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]':
        """
        Composes failed container with a pure function.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess

          >>> assert RequiresContextIOResult.from_success(1).fix(
          ...     lambda x: x + 1,
          ... )(...) == IOSuccess(1)

          >>> assert RequiresContextIOResult.from_failure(1).fix(
          ...     lambda x: x + 1,
          ... )(...) == IOSuccess(2)

        """
        return RequiresContextIOResult(lambda deps: self(deps).fix(function))

    def alt(
        self, function: Callable[[_ErrorType], _NewErrorType],
    ) -> 'RequiresContextIOResult[_EnvType, _ValueType, _NewErrorType]':
        """
        Composes failed container with a pure function.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert RequiresContextIOResult.from_success(1).alt(
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
            'RequiresContextIOResult[_EnvType, _ValueType, _NewErrorType]',
        ],
    ):
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
          ...

          >>> assert RequiresContextIOResult.from_success('a').rescue(
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

    def value_or(
        self, default_value: _FirstType,
    ) -> Callable[[_EnvType], IO[Union[_ValueType, _FirstType]]]:
        """
        Returns a callable that either returns a success or default value.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IO

          >>> assert RequiresContextIOResult.from_success(1).value_or(2)(
          ...     RequiresContextIOResult.empty,
          ... ) == IO(1)

          >>> assert RequiresContextIOResult.from_failure(1).value_or(2)(
          ...     RequiresContextIOResult.empty,
          ... ) == IO(2)

        """
        return lambda deps: self(deps).value_or(default_value)

    def unwrap(self) -> Callable[[_EnvType], IO[_ValueType]]:
        """
        Returns a callable that unwraps success value or raises exception.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IO

          >>> assert RequiresContextIOResult.from_success(1).unwrap()(
          ...     RequiresContextIOResult.empty,
          ... ) == IO(1)

        .. code::

          >>> RequiresContextIOResult.from_failure(1).unwrap()(
          ...     RequiresContextIOResult.empty,
          ... )
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
        return lambda deps: self(deps).unwrap()

    def failure(self) -> Callable[[_EnvType], IO[_ErrorType]]:
        """
        Returns a callable that unwraps failure value or raises exception.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IO

          >>> assert RequiresContextIOResult.from_failure(1).failure()(
          ...     RequiresContextIOResult.empty,
          ... ) == IO(1)

        .. code::

          >>> RequiresContextIOResult.from_success(1).failure()(
          ...    RequiresContextIOResult.empty,
          ... )
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
        ['RequiresContextIOResult[_EnvType, _ValueType, _ErrorType]'],
        'RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]',
    ]:
        """
        Lifts function to be wrapped in a conatiner for better composition.

        In other words, it modifies the function's
        signature from: ``a -> b`` to:
        ``RequiresContextIOResult[env, a, err]``
        -> ``RequiresContextIOResult[env, b, err]``

        Works similar to :meth:`~RequiresContextIOResult.map`,
        but has inverse semantics.

        This is how it should be used:

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess

          >>> def function(arg: int) -> str:
          ...     return str(arg) + '!'
          ...
          >>> unit = RequiresContextIOResult.from_success(1)
          >>> deps = RequiresContextIOResult.empty
          >>> assert RequiresContextIOResult.lift(function)(
          ...     unit,
          ... )(deps) == IOSuccess('1!')

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
        ['RequiresContextIOResult[_EnvType, _ValueType, _ErrorType]'],
        'RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]',
    ]:
        """
        Lifts function from ``Result`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> Result[b, c]`` to:
        ``RequiresContextIOResult[env, a, c]``
        -> ``RequiresContextIOResult[env, b, c]``

        Similar to :meth:`~RequiresContextIOResult.lift`,
        but works with other type.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.result import Success, Failure, Result
          >>> from returns.io import IOSuccess, IOFailure

          >>> def function(arg: int) -> Result[str, int]:
          ...     if arg > 0:
          ...         return Success(str(arg) + '!')
          ...     return Failure(arg)
          ...
          >>> deps = RequiresContextIOResult.empty

          >>> assert RequiresContextIOResult.lift_result(function)(
          ...     RequiresContextIOResult.from_success(1),
          ... )(deps) == IOSuccess('1!')

          >>> assert RequiresContextIOResult.lift_result(function)(
          ...     RequiresContextIOResult.from_success(0),
          ... )(deps) == IOFailure(0)

          >>> assert RequiresContextIOResult.lift_result(function)(
          ...     RequiresContextIOResult.from_failure('nope'),
          ... )(deps) == IOFailure('nope')

        """
        return lambda container: container.bind_result(function)

    @classmethod
    def lift_ioresult(
        cls,
        function: Callable[[_ValueType], IOResult[_NewValueType, _ErrorType]],
    ) -> Callable[
        ['RequiresContextIOResult[_EnvType, _ValueType, _ErrorType]'],
        'RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]',
    ]:
        """
        Lifts function from ``IOResult`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> IOResult[b, c]`` to:
        ``RequiresContextIOResult[env, a, c]``
        -> ``RequiresContextIOResult[env, b, c]``

        Similar to :meth:`~RequiresContextIOResult.lift`,
        but works with other type.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess, IOFailure, IOResult

          >>> def function(arg: int) -> IOResult[str, int]:
          ...     if arg > 0:
          ...         return IOSuccess(str(arg) + '!')
          ...     return IOFailure(arg)
          ...
          >>> deps = RequiresContextIOResult.empty

          >>> assert RequiresContextIOResult.lift_ioresult(function)(
          ...     RequiresContextIOResult.from_success(1),
          ... )(deps) == IOSuccess('1!')

          >>> assert RequiresContextIOResult.lift_ioresult(function)(
          ...     RequiresContextIOResult.from_success(0),
          ... )(deps) == IOFailure(0)

          >>> assert RequiresContextIOResult.lift_ioresult(function)(
          ...     RequiresContextIOResult.from_failure('nope'),
          ... )(deps) == IOFailure('nope')

        """
        return lambda container: container.bind_ioresult(function)

    @classmethod
    def lift_context(
        cls,
        function: Callable[
            [_ValueType],
            RequiresContext[_EnvType, _NewValueType],
        ],
    ) -> Callable[
        ['RequiresContextIOResult[_EnvType, _ValueType, _ErrorType]'],
        'RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]',
    ]:
        """
        Lifts function from ``RequiresContext`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> RequiresContext[env, b]`` to:
        ``RequiresContextIOResult[env, a, c]``
        -> ``RequiresContextIOResult[env, b, c]``

        Similar to :meth:`~RequiresContextIOResult.lift`,
        but works with other type.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> from returns.io import IOSuccess, IOFailure

          >>> def function(arg: int) -> RequiresContext[str, int]:
          ...     return RequiresContext(lambda deps: len(deps) + arg)
          ...

          >>> assert RequiresContextIOResult.lift_context(function)(
          ...     RequiresContextIOResult.from_success(2),
          ... )('abc') == IOSuccess(5)

          >>> assert RequiresContextIOResult.lift_context(function)(
          ...     RequiresContextIOResult.from_failure(0),
          ... )('abc') == IOFailure(0)

        """
        return lambda container: container.bind_context(function)

    @classmethod
    def lift_context_result(
        cls,
        function: Callable[
            [_ValueType],
            RequiresContextResult[_EnvType, _NewValueType, _ErrorType],
        ],
    ) -> Callable[
        ['RequiresContextIOResult[_EnvType, _ValueType, _ErrorType]'],
        'RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]',
    ]:
        """
        Lifts function from ``RequiresContextResult`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> RequiresContextResult[env, b, c]`` to:
        ``RequiresContextIOResult[env, a, c]``
        -> ``RequiresContextIOResult[env, b, c]``

        Similar to :meth:`~RequiresContextIOResult.lift`,
        but works with other type.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.io import IOSuccess, IOFailure
          >>> from returns.result import Success

          >>> def function(arg: int) -> RequiresContextResult[str, int, str]:
          ...     return RequiresContextResult(
          ...         lambda deps: Success(len(deps) + arg),
          ...     )
          ...

          >>> assert RequiresContextIOResult.lift_context_result(function)(
          ...     RequiresContextIOResult.from_success(2),
          ... )('abc') == IOSuccess(5)

          >>> assert RequiresContextIOResult.lift_context_result(function)(
          ...     RequiresContextIOResult.from_failure(0),
          ... )('abc') == IOFailure(0)

        """
        return lambda container: container.bind_context_result(function)

    @classmethod
    def from_result(
        cls, inner_value: Result[_ValueType, _ErrorType],
    ) -> 'RequiresContextIOResult[Any, _ValueType, _ErrorType]':
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
    def from_ioresult(
        cls, inner_value: IOResult[_ValueType, _ErrorType],
    ) -> 'RequiresContextIOResult[Any, _ValueType, _ErrorType]':
        """
        Creates new container with ``Result`` as a unit value.

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
        cls, container: RequiresContext[
            _EnvType, IOResult[_NewValueType, _NewErrorType],
        ],
    ) -> 'RequiresContextIOResult[_EnvType, _NewValueType, _NewErrorType]':
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
        return RequiresContextIOResult(container)

    @classmethod
    def from_successful_context(
        cls, inner_value: RequiresContext[_EnvType, _FirstType],
    ) -> 'RequiresContextIOResult[_EnvType, _FirstType, Any]':
        """
        Creates new container from ``RequiresContext`` as a success unit.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> from returns.io import IOSuccess

          >>> assert RequiresContextIOResult.from_successful_context(
          ...     RequiresContext.from_value(1),
          ... )(...) == IOSuccess(1)

        """
        return RequiresContextIOResult(
            lambda deps: IOSuccess(inner_value(deps)),
        )

    @classmethod
    def from_failed_context(
        cls, inner_value: RequiresContext[_EnvType, _FirstType],
    ) -> 'RequiresContextIOResult[_EnvType, Any, _FirstType]':
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
        cls, inner_value: RequiresContextResult[
            _EnvType, _ValueType, _ErrorType,
        ],
    ) -> 'RequiresContextIOResult[_EnvType, _ValueType, _ErrorType]':
        """
        Creates new container from ``RequiresContextResult`` as a unit value.

        .. code:: python

          >>> from returns.context import RequiresContextResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> assert RequiresContextIOResult.from_result_context(
          ...     RequiresContextResult.from_success(1),
          ... )(...) == IOSuccess(1)

          >>> assert RequiresContextIOResult.from_result_context(
          ...     RequiresContextResult.from_failure(1),
          ... )(...) == IOFailure(1)

        """
        return RequiresContextIOResult(
            lambda deps: IOResult.from_result(inner_value(deps)),
        )

    @classmethod
    def from_success(
        cls, inner_value: _FirstType,
    ) -> 'RequiresContextIOResult[Any, _FirstType, Any]':
        """
        Creates new container with ``IOSuccess(inner_value)`` as a unit value.

        .. code:: python

          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess

          >>> assert RequiresContextIOResult.from_success(1)(
          ...    RequiresContextIOResult.empty,
          ... ) == IOSuccess(1)

        """
        return RequiresContextIOResult(lambda _: IOSuccess(inner_value))

    @classmethod
    def from_failure(
        cls, inner_value: _FirstType,
    ) -> 'RequiresContextIOResult[Any, Any, _FirstType]':
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

    # TODO: support from_successful_result_context
    # TODO: support from_failed_result_context


@final
class ContextIOResult(Immutable, Generic[_EnvType]):
    """
    Helpers that can be used to work with ``RequiresContextIOResult`` container.

    Related to :class:`returns.context.requires_context.Context`
    and :class:`returns.context.requires_context_result.ContextResult`,
    refer there for the docs.
    """

    @classmethod
    def ask(cls) -> RequiresContextIOResult[_EnvType, _EnvType, Any]:
        """
        Is used to get the current dependencies inside the call stack.

        Similar to :meth:`returns.context.requires_context.Context.ask`,
        but returns ``IOResult`` instead of a regular value.

        Please, refer to the docs there to know how to use it.

        One important note that is worth doublicating here:
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
    _EnvType, _ValueType, Exception,
]

#: Alias to save you some typing. Uses original name from Haskell.
ReaderIOResult = RequiresContextIOResult[_EnvType, _ValueType, _ErrorType]

#: Alias to save you some typing. Uses ``Exception`` as error type.
ReaderIOResultE = RequiresContextIOResult[_EnvType, _ValueType, Exception]
