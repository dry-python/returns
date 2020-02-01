# -*- coding: utf-8 -*-

from typing import Any, Callable, ClassVar, Generic, TypeVar

from typing_extensions import final

from returns.functions import identity
from returns.primitives.container import BaseContainer
from returns.primitives.types import Immutable

# Context:
_EnvType = TypeVar('_EnvType', contravariant=True)
_ReturnType = TypeVar('_ReturnType', covariant=True)
_NewReturnType = TypeVar('_NewReturnType')

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

        Part of the :class:`returns.primitives.interfaces.Instanceable`
        protocol.
        """
        return RequiresContext(lambda _: inner_value)


@final
class Context(Immutable, Generic[_EnvType]):
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
