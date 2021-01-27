from functools import wraps
from typing import TYPE_CHECKING, Callable, TypeVar

from typing_extensions import final

from returns.interfaces.specific import io
from returns.primitives.container import BaseContainer, container_equality
from returns.primitives.hkt import Kind1, SupportsKind1, dekind
from returns.io.io import IO

_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')

# Result related:
_ErrorType = TypeVar('_ErrorType', covariant=True)
_NewErrorType = TypeVar('_NewErrorType')

# Helpers:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')


@final
class LazyIO(
    BaseContainer,
    SupportsKind1['LazyIO', _ValueType],
    io.IOLike1[_ValueType],
):
    """


    """

    _inner_value: Callable[['LazyIO'], IO[_ValueType]]

    #: Typesafe equality comparison with other `Result` objects.
    equals = container_equality

    def __init__(self, inner_value: Callable[[], IO[_ValueType]]) -> None:
        """
        Public constructor for this type. Also required for typing.

        .. code:: python

          >>> from returns.io import LazyIO
          >>> assert LazyIO(lambda: 1)() == 1

        """
        super().__init__(inner_value)

    def __call__(self) -> IO[_ValueType]:
        """
        Executes the wrapped ``IO`` action.
        """
        return self._inner_value()

    def map(  # noqa: WPS125
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> 'LazyIO[_NewValueType]':
        return LazyIO(lambda: IO(function(self()._inner_value)))

    def apply(
        self,
        container: Kind1['LazyIO', Callable[[_ValueType], _NewValueType]],
    ) -> 'LazyIO[_NewValueType]':
        return self.map(dekind(container)()._inner_value)  # noqa: WPS437

    def bind(
        self,
        function: Callable[[_ValueType], Kind1['LazyIO', _NewValueType]],
    ) -> 'LazyIO[_NewValueType]':
        return function(self()._inner_value)



# Helper functions:

def impure_lazy(
    function: Callable[..., _NewValueType],
) -> Callable[..., LazyIO[_NewValueType]]:
    """

    """
    @wraps(function)
    def decorator(*args, **kwargs):
        return LazyIO(lambda: IO(function(*args, **kwargs)))
    return decorator
