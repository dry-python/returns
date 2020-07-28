from typing import NoReturn, TypeVar

from returns.interfaces import bindable
from returns.interfaces.aliases.applicative_mappable import ApplicativeMappableN

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')


class ContainerN(
    ApplicativeMappableN[_FirstType, _SecondType, _ThirdType],
    bindable.BindableN[_FirstType, _SecondType, _ThirdType],
):
    """
    Handy alias for types with ``.bind``, ``.map``, and ``.apply`` methods.

    Should be a base class for almost any containers you write.

    See also:
        https://bit.ly/2CTEVov

    """


#: Type alias for kinds with one type argument.
Container1 = ContainerN[_FirstType, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
Container2 = ContainerN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
Container3 = ContainerN[_FirstType, _SecondType, _ThirdType]
