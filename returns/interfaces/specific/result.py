from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, Generic, NoReturn, Type, TypeVar

from returns.primitives.hkt import KindN

if TYPE_CHECKING:
    from returns.result import Result  # noqa: WPS433

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')
_ResultBasedType = TypeVar('_ResultBasedType', bound='ResultBasedN')


class ResultBasedN(Generic[_FirstType, _SecondType, _ThirdType]):
    """
    Allows to create unit containers from raw values and to apply wrapped funcs.

    See also:
        https://en.wikipedia.org/wiki/ResultBased_functor
        http://learnyouahaskell.com/functors-ResultBased-functors-and-monoids

    """

    @abstractmethod
    def bind_result(
        self: _ResultBasedType,
        function: Callable[[_FirstType], 'Result[_UpdatedType, _SecondType]'],
    ) -> KindN[_ResultBasedType, _UpdatedType, _SecondType, _ThirdType]:
        """Allows to apply a wrapped function over a container."""

    @classmethod
    @abstractmethod
    def from_result(
        cls: Type[_ResultBasedType],  # noqa: N805
        inner_value: 'Result[_FirstType, _SecondType]',
    ) -> KindN[_ResultBasedType, _FirstType, _SecondType, _ThirdType]:
        """Unit method to create new containers from any raw value."""

    @classmethod
    @abstractmethod
    def from_failure(
        cls: Type[_ResultBasedType],  # noqa: N805
        inner_value: _SecondType,
    ) -> KindN[_ResultBasedType, _FirstType, _SecondType, _ThirdType]:
        """Unit method to create new containers from any raw value."""


#: Type alias for kinds with one type argument.
ResultBased1 = ResultBasedN[_FirstType, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
ResultBased2 = ResultBasedN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
ResultBased3 = ResultBasedN[_FirstType, _SecondType, _ThirdType]
