from typing import NoReturn, TypeVar

from returns.interfaces import applicative, mappable

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')


class ApplicativeMappableN(
    applicative.ApplicativeN[_FirstType, _SecondType, _ThirdType],
    mappable.MappableN[_FirstType, _SecondType, _ThirdType],
):
    """
    Handy alias for types that do both ``.map`` and ``.apply``.

    See also:
        https://en.wikipedia.org/wiki/Applicative_functor

    """


#: Type alias for kinds with one type argument.
ApplicativeMappable1 = ApplicativeMappableN[_FirstType, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
ApplicativeMappable2 = ApplicativeMappableN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
ApplicativeMappable3 = ApplicativeMappableN[_FirstType, _SecondType, _ThirdType]
