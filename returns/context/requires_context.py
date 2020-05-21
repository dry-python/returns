from typing import TYPE_CHECKING, Any, Callable, ClassVar, Generic, TypeVar

from typing_extensions import final

from returns.functions import identity
from returns.primitives.container import BaseContainer
from returns.primitives.types import Immutable

if TYPE_CHECKING:
    # We need this condition to make sure Python can solve cycle imports.
    # But, since we only use these values in types, it is not important.
    from returns.context.requires_context_ioresult import (
        RequiresContextIOResult,
    )
    from returns.context.requires_context_result import RequiresContextResult
    from returns.io import IOResult
    from returns.result import Result

# Context:
_EnvType = TypeVar('_EnvType', contravariant=True)
_ReturnType = TypeVar('_ReturnType', covariant=True)
_NewReturnType = TypeVar('_NewReturnType')

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')

# Helpers:
_FirstType = TypeVar('_FirstType')

# Type Aliases:
#: Sometimes ``RequiresContext`` and other similar types might be used with
#: no explicit dependencies so we need to have this type alias for Any.
NoDeps = Any


@final
class RequiresContext(
    BaseContainer,
    Generic[_EnvType, _ReturnType],
):
    """
    The ``RequiresContext`` container.

    It's main purpose is to wrap some specific function
    and to provide tools to compose other functions around it
    without actually calling it.

    The ``RequiresContext`` container passes the state
    you want to share between functions.
    Functions may read that state, but can't change it.
    The ``RequiresContext`` container
    lets us access shared immutable state within a specific context.

    It can be used for lazy evaluation and typed dependency injection.

    ``RequiresContext`` is used with functions that never fail.
    If you want to use ``RequiresContext`` with returns ``Result``
    then consider using ``RequiresContextResult`` instead.

    Note:
        This container does not wrap ANY value. It wraps only functions.
        You won't be able to supply arbitrary types!

    See also:
        https://dev.to/gcanti/getting-started-with-fp-ts-reader-1ie5
        https://en.wikipedia.org/wiki/Lazy_evaluation
        https://bit.ly/2R8l4WK

    """

    #: This field has an extra 'RequiresContext' just because `mypy` needs it.
    _inner_value: Callable[['RequiresContext', _EnvType], _ReturnType]

    #: A convinient placeholder to call methods created by `.from_value()`:
    empty: ClassVar[NoDeps] = object()

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

          >>> instance = first(False)  # creating `RequiresContext` instance
          >>> assert instance(3.5) == -3.5 # calling it with `__call__`

          >>> # Example with another logic:
          >>> assert first(True)(3.5) == 3.5

        In other things, it is a regular python magic method.
        """
        return self._inner_value(deps)

    def map(  # noqa: WPS125
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

          >>> assert first(True).map(lambda number: number * 10)(2.5) == 25.0
          >>> assert first(False).map(lambda number: number * 10)(0.1) -1.0

        """
        return RequiresContext(lambda deps: function(self(deps)))

    def apply(
        self,
        container: 'Reader[_EnvType, Callable[[_ReturnType], _NewReturnType]]',
    ) -> 'RequiresContext[_EnvType, _NewReturnType]':
        """
        Calls a wrapped function in a container on this container.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> assert RequiresContext.from_value('a').apply(
          ...    RequiresContext.from_value(lambda inner: inner + 'b')
          ... )(...) == 'ab'

        """
        return RequiresContext(lambda deps: self.map(container(deps))(deps))

    def bind(
        self,
        function: Callable[
            [_ReturnType],
            'RequiresContext[_EnvType, _NewReturnType]',
        ],
    ) -> 'RequiresContext[_EnvType, _NewReturnType]':
        """
        Composes a container with a function returning another container.

        This is useful when you do several computations that rely on the
        same context.

        .. code:: python

          >>> from returns.context import RequiresContext

          >>> def first(lg: bool) -> RequiresContext[float, int]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContext(
          ...         lambda deps: deps if lg else -deps,
          ...     )

          >>> def second(number: int) -> RequiresContext[float, str]:
          ...     # `deps` has `float` type here:
          ...     return RequiresContext(
          ...         lambda deps: '>=' if number >= deps else '<',
          ...     )

          >>> assert first(True).bind(second)(1) == '>='
          >>> assert first(False).bind(second)(2) == '<'

        """
        return RequiresContext(lambda deps: function(self(deps))(deps))

    @classmethod
    def from_value(
        cls, inner_value: _FirstType,
    ) -> 'RequiresContext[Any, _FirstType]':
        """
        Used to return some specific value from the container.

        Consider this method as some kind of factory.
        Passed value will be a return type.
        Make sure to use :attr:`~RequiresContext.empty`
        for getting the unit value.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> unit = RequiresContext.from_value(5)
          >>> assert unit(RequiresContext.empty) == 5

        Might be used with or without direct type hint.

        Part of the :class:`returns.primitives.interfaces.Applicative`
        protocol.
        """
        return RequiresContext(lambda _: inner_value)

    @classmethod
    def from_requires_context_result(
        cls,
        container: 'RequiresContextResult[_EnvType, _ValueType, _ErrorType]',
    ) -> 'RequiresContext[_EnvType, Result[_ValueType, _ErrorType]]':
        """
        Typecasts ``RequiresContextResult`` to ``RequiresContext`` instance.

        Breaks ``RequiresContextResult[e, a, b]``
        into ``RequiresContext[e, Result[a, b]]``.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> from returns.context import RequiresContextResult
          >>> from returns.result import Success
          >>> assert RequiresContext.from_requires_context_result(
          ...    RequiresContextResult.from_value(1),
          ... )(...) == Success(1)

        Can be reverted with ``RequiresContextResult.from_typecast``.

        """
        return RequiresContext(container)

    @classmethod
    def from_requires_context_ioresult(
        cls,
        container: 'RequiresContextIOResult[_EnvType, _ValueType, _ErrorType]',
    ) -> 'RequiresContext[_EnvType, IOResult[_ValueType, _ErrorType]]':
        """
        Typecasts ``RequiresContextIOResult`` to ``RequiresContext`` instance.

        Breaks ``RequiresContextIOResult[e, a, b]``
        into ``RequiresContext[e, IOResult[a, b]]``.

        .. code:: python

          >>> from returns.context import RequiresContext
          >>> from returns.context import RequiresContextIOResult
          >>> from returns.io import IOSuccess
          >>> assert RequiresContext.from_requires_context_ioresult(
          ...    RequiresContextIOResult.from_value(1),
          ... )(...) == IOSuccess(1)

        Can be reverted with ``RequiresContextIOResult.from_typecast``.

        """
        return RequiresContext(container)


@final
class Context(Immutable, Generic[_EnvType]):
    """
    Helpers that can be used to work with ``RequiresContext`` container.

    Some of them require an explicit type to be specified.

    This class contains methods that require
    to explicitly set type annotations. Why?
    Because it is impossible to figure out the type without them.

    So, here's how you should use them:

    .. code:: python

      Context[Dict[str, str]].ask()

    Otherwise, your ``.ask()`` method
    will return ``RequiresContext[<nothing>, <nothing>]``,
    which is unusable:

    .. code:: python

      env = Context.ask()
      env(some_deps)

    And ``mypy`` will warn you: ``error: Need type annotation for 'a'``

    """

    @classmethod
    def ask(cls) -> RequiresContext[_EnvType, _EnvType]:
        """
        Get current context to use the dependencies.

        It is a common scenario when you need to use the environment.
        For example, you want to do some context-related computation,
        but you don't have the context instance at your disposal.
        That's where ``.ask()`` becomes useful!

        .. code:: python

          >>> from typing_extensions import TypedDict
          >>> class Deps(TypedDict):
          ...     message: str

          >>> def first(lg: bool) -> RequiresContext[Deps, int]:
          ...     # `deps` has `Deps` type here:
          ...     return RequiresContext(
          ...         lambda deps: deps['message'] if lg else 'error',
          ...     )

          >>> def second(text: str) -> RequiresContext[int, int]:
          ...     return first(len(text) > 3)

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

          >>> def new_first(lg: bool) -> RequiresContext[Deps, int]:
          ...     # `deps` has `Deps` type here:
          ...     return RequiresContext(
          ...         lambda deps: deps['message'] if lg else 'err',
          ...     )

          >>> def new_second(text: str) -> RequiresContext[int, int]:
          ...     return Context[Deps].ask().bind(
          ...         lambda deps: new_first(len(text) > deps.get('limit', 3)),
          ...     )

          >>> assert new_second('abc')({'message': 'ok', 'limit': 2}) == 'ok'
          >>> assert new_second('abcd')({'message': 'ok'}) == 'ok'
          >>> assert new_second('abcd')({'message': 'ok', 'limit': 5}) == 'err'

        That's how ``ask`` works.

        See also:
            https://dev.to/gcanti/getting-started-with-fp-ts-reader-1ie5

        """
        return RequiresContext(identity)


# Aliases

#: Sometimes `RequiresContext` is too long to type.
Reader = RequiresContext
