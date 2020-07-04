from typing import Generic, TypeVar

_InstanceType = TypeVar('_InstanceType')
_TypeArgTypes = TypeVar('_TypeArgTypes')


# TODO: make Kind to accept any number of generic arguments
class Kind(Generic[_InstanceType, _TypeArgTypes]):
    """Emulation support for Higher Kinded Types."""
