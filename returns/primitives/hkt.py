from typing import Callable, Generic, NoReturn, Tuple, TypeVar

from typing_extensions import Protocol

from returns.functions import identity

_InstanceType = TypeVar('_InstanceType', covariant=True)
_TypeArgType1 = TypeVar('_TypeArgType1', covariant=True)
_TypeArgType2 = TypeVar('_TypeArgType2', covariant=True)
_TypeArgType3 = TypeVar('_TypeArgType3', covariant=True)

_FunctionDefType = TypeVar(
    '_FunctionDefType',
    bound=Callable[..., 'KindN'],
    covariant=True,  # This is a must! Otherwise it would not work.
)
_FunctionType = TypeVar(
    '_FunctionType',
    bound=Callable[..., 'KindN'],
)

_UpdatedType = TypeVar('_UpdatedType')
_FirstKind = TypeVar('_FirstKind')
_SecondKind = TypeVar('_SecondKind')


class KindN(
    Generic[_InstanceType, _TypeArgType1, _TypeArgType2, _TypeArgType3],
):
    """
    Emulation support for Higher Kinded Types.

    Consider ``KindN`` to be an alias of ``Generic`` type.
    But with some extra goodies.

    ``KindN`` is the top-most type for other ``Kind`` types
    like ``Kind1``, ``Kind2``, ``Kind3``, etc.

    The only difference between them is how many type arguments they can hold.
    ``Kind1`` can hold just two type arguments: ``Kind1[IO, int]``
    which is almost equals to ``IO[int]``.
    ``Kind2`` can hold just two type arguments: ``Kind2[IOResult, int, str]``
    which is almost equals to ``IOResult[int, str]``.
    And so on.

    The idea behind ``KindN`` is that one cannot write this code:

    .. code:: python

      from typing import TypeVar

      T = TypeVar('T')
      V = TypeVar('V')

      def impossible(generic: T, value: V) -> T[V]:
          return generic(value)

    But, with ``KindN`` this becomes possible in a form of ``Kind1[T, V]``.

    .. note::
        To make sure it works correctly,
        your type has to be a subtype of ``KindN``.

    We use a custom ``mypy`` plugin to make sure types are correct.
    Otherwise, it is currently impossible to properly type this.

    We use "emulated Higher Kinded Types" concept.
    Read the whitepaper: https://bit.ly/2ABACx2

    ``KindN`` does not exist in runtime. It is used just for typing.
    There are (and must be) no instances of this type directly.

    Implementation details
    ~~~~~~~~~~~~~~~~~~~~~~

    We didn't use ``ABCMeta`` to disallow its creation,
    because we don't want to have
    a possible metaclass conflict with other metaclasses.
    Current API allows you to mix ``KindN`` anywhere.

    We allow ``_InstanceType`` of ``KindN``
    to be ``Instance`` type or ``TypeVarType`` with ``upper_bound``.
    To work with ``Instance`` types use ``dekind``.
    To work with ``TypeVarType`` types use ``debound``.

    See also:
        https://arrow-kt.io/docs/0.10/patterns/glossary/#higher-kinds
        https://github.com/gcanti/fp-ts/blob/master/docs/guides/HKT.md
        https://bow-swift.io/docs/fp-concepts/higher-kinded-types

    """

    __slots__ = ()


#: Type alias for kinds with one type argument.
Kind1 = KindN[_InstanceType, _TypeArgType1, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
Kind2 = KindN[_InstanceType, _TypeArgType1, _TypeArgType2, NoReturn]

#: Type alias for kinds with three type arguments.
Kind3 = KindN[_InstanceType, _TypeArgType1, _TypeArgType2, _TypeArgType3]


def dekind(
    kind: KindN[_InstanceType, _TypeArgType1, _TypeArgType2, _TypeArgType3],
) -> _InstanceType:
    """
    Turns ``Kind1[IO, int]`` type into real ``IO[int]`` type.

    Should be used when you are left with accidential ``Kind`` instance
    when you really want to have the real type.

    Works with type arguments of any length.

    We use a custom ``mypy`` plugin to make sure types are correct.
    Otherwise, it is currently impossible to properly type this.

    In runtime it just returns the passed argument, nothing really happens:

    .. code:: python

      >>> from returns.io import IO
      >>> from returns.primitives.hkt import Kind1

      >>> container: Kind1[IO, int] = IO(1)
      >>> assert dekind(container) is container

    However, please, do not use this function
    unless you know exactly what you are doing and why do you need it.
    """
    return kind  # type: ignore


# Utils to define kinded functions
# ================================

class Kinded(Protocol[_FunctionDefType]):  # type: ignore
    """
    Protocol that tracks kinded functions calls.

    We use a custom ``mypy`` plugin to make sure types are correct.
    Otherwise, it is currently impossible to properly type this.
    """

    __call__: _FunctionDefType


def kinded(function: _FunctionType) -> Kinded[_FunctionType]:
    """
    Decorator to be used when you want to dekind the function's return type.

    Does nothing in runtime, just returns its argument.

    We use a custom ``mypy`` plugin to make sure types are correct.
    Otherwise, it is currently impossible to properly type this.

    Here's an example of how it should be used:

    .. code:: python

      >>> from typing import TypeVar
      >>> from returns.primitives.hkt import KindN, kinded
      >>> from returns.interfaces.bindable import BindableN

      >>> _Binds = TypeVar('_Binds', bound=BindableN)  # just an example
      >>> _Type1 = TypeVar('_Type1')
      >>> _Type2 = TypeVar('_Type2')
      >>> _Type3 = TypeVar('_Type3')

      >>> @kinded
      ... def bindable_identity(
      ...    container: KindN[_Binds, _Type1, _Type2, _Type3],
      ... ) -> KindN[_Binds, _Type1, _Type2, _Type3]:
      ...     return container  # just do nothing

    As you can see, here we annotate our return type as
    ``-> KindN[_Binds, _Type1, _Type2, _Type3]``,
    it would be true without ``@kinded`` decorator.

    But, ``@kinded`` decorator dekinds the return type and infers
    the real type behind it:

    .. code:: python

      >>> from returns.io import IO, IOResult

      >>> assert bindable_identity(IO(1)) == IO(1)
      >>> # => Revealed type: 'IO[int]'

      >>> iores: IOResult[int, str] = IOResult.from_value(1)
      >>> assert bindable_identity(iores) == iores
      >>> # => Revealed type: 'IOResult[int, str]'

    The difference is very clear in ``methods`` modules, like:

    - Raw :func:`returns.methods.bind.internal_bind`
      that returns ``KindN`` instance
    - User-facing :func:`returns.methods.bind.bind`
      that returns the container type

    You must use this decorator for your own kinded functions as well.
    """
    return function  # type: ignore


def debound(
    instance: KindN[_FirstKind, _TypeArgType1, _TypeArgType2, _TypeArgType3],
) -> Tuple[
    _FirstKind,
    Callable[
        [KindN[_SecondKind, _UpdatedType, _TypeArgType2, _TypeArgType3]],
        KindN[_FirstKind, _UpdatedType, _TypeArgType2, _TypeArgType3],
    ],
]:
    """
    Helper function to simplify work with ``KindN`` inside the kinded context.

    Here's the problem:

    .. code:: python

      from typing import TypeVar
      from returns.primitives.hkt import KindN, kinded
      from returns.interfaces.mappable import MappableN

      _Maps = TypeVar('_Maps', bound=MappableN)

      @kinded
      def map_int(
          container: KindN[_Maps, _T1, _T2, _T3],
      ) -> KindN[_Maps, int, _T2, _T3]:
          return container.map(int)  # won't work!

    In this example, ``container.map(int)`` will fail with the type error,
    because ``KindN`` does not have ``.map`` method.

    But, ``_Maps`` type has! Because it is bound to ``MappableN`` typeclass.
    It means, that we have to debound ``container``
    to ``MappableN`` instead of ``KindN```:

    .. code:: python

      from returns.primitives.hkt import debound

      @kinded
      def map_int(
          container: KindN[_Maps, _T1, _T2, _T3],
      ) -> KindN[_Maps, int, _T2, _T3]:
          new_instance, _ = debound(container)
          reveal_type(new_instance)  # It is correct now!
          # => MappableN[_T1, _T2, _T3]

          # But this line won't work just yet:
          return new_instance.map(int)
          # Because it has type 'KindN[MappableN, int, _T2, _T3]'
          # But, expected type: 'KindN[_Maps, int, _T2, _T3]'

    We now need to somehow turn our type back to the initial one.
    This is where the second element of the tuple becomes useful:

    .. code:: python

      from returns.primitives.hkt import debound

      @kinded
      def map_int(
          container: KindN[_Maps, _T1, _T2, _T3],
      ) -> KindN[_Maps, int, _T2, _T3]:
          new_instance, rebound = debound(container)
          return rebound(new_instance.map(int))  # Now it works!
          # Turns the return type to: 'KindN[_Maps, int, _T2, _T3]'

    And this will work corretly both in runtime and typechecking.
    """
    return instance, identity  # type: ignore
