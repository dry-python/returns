from typing import Iterable, List, Optional

from mypy.typeops import erase_to_bound
from mypy.types import (
    AnyType,
    CallableType,
    DeletedType,
    ErasedType,
    Instance,
    LiteralType,
    NoneType,
    Overloaded,
    PartialType,
    TupleType,
    Type,
    TypedDictType,
    TypeOfAny,
    TypeType,
    TypeVarType,
    UnboundType,
    UninhabitedType,
    UnionType,
    get_proper_type,
)

from returns.contrib.mypy._consts import TYPED_KINDN

# TODO: replace with real `TypeTranslator` in the next mypy release.
_LEAF_TYPES = (
    UnboundType,
    AnyType,
    NoneType,
    UninhabitedType,
    ErasedType,
    DeletedType,
    TypeVarType,
    PartialType,
)


def translate_kind_instance(typ: Type) -> Type:  # noqa: WPS, C901
    """
    We use this ugly hack to translate ``KindN[x, y]`` into ``x[y]``.

    This is required due to the fact that ``KindN``
    can be nested in other types, like: ``List[KindN[...]]``.

    We will refactor this code after ``TypeTranslator``
    is released in ``mypy@0.800`` version.
    """
    typ = get_proper_type(typ)

    if isinstance(typ, _LEAF_TYPES):  # noqa: WPS223
        return typ
    elif isinstance(typ, Instance):
        last_known_value: Optional[LiteralType] = None
        if typ.last_known_value is not None:
            raw_last_known_value = translate_kind_instance(typ.last_known_value)
            assert isinstance(raw_last_known_value, LiteralType)
            last_known_value = raw_last_known_value
        instance = Instance(
            typ=typ.type,
            args=_translate_types(typ.args),
            line=typ.line,
            column=typ.column,
            last_known_value=last_known_value,
        )
        if typ.type.fullname == TYPED_KINDN:  # That's where we do the change
            return _process_kinded_type(instance)
        return instance

    elif isinstance(typ, CallableType):
        return typ.copy_modified(
            arg_types=_translate_types(typ.arg_types),
            ret_type=translate_kind_instance(typ.ret_type),
        )
    elif isinstance(typ, TupleType):
        return TupleType(
            _translate_types(typ.items),
            translate_kind_instance(typ.partial_fallback),  # type: ignore
            typ.line,
            typ.column,
        )
    elif isinstance(typ, TypedDictType):
        dict_items = {
            item_name: translate_kind_instance(item_type)
            for item_name, item_type in typ.items.items()
        }
        return TypedDictType(
            dict_items,
            typ.required_keys,
            translate_kind_instance(typ.fallback),  # type: ignore
            typ.line,
            typ.column,
        )
    elif isinstance(typ, LiteralType):
        fallback = translate_kind_instance(typ.fallback)
        assert isinstance(fallback, Instance)
        return LiteralType(
            value=typ.value,
            fallback=fallback,
            line=typ.line,
            column=typ.column,
        )
    elif isinstance(typ, UnionType):
        return UnionType(_translate_types(typ.items), typ.line, typ.column)
    elif isinstance(typ, Overloaded):
        functions: List[CallableType] = []
        for func in typ.items:
            new = translate_kind_instance(func)
            assert isinstance(new, CallableType)
            functions.append(new)
        return Overloaded(items=functions)
    elif isinstance(typ, TypeType):
        return TypeType.make_normalized(
            translate_kind_instance(typ.item),
            line=typ.line,
            column=typ.column,
        )
    return typ


def _translate_types(types: Iterable[Type]) -> List[Type]:
    return [translate_kind_instance(typ) for typ in types]


def _process_kinded_type(kind: Instance) -> Type:
    """Recursively process all type arguments in a kind."""
    if not kind.args:
        return kind

    real_type = get_proper_type(kind.args[0])
    if isinstance(real_type, TypeVarType):
        return erase_to_bound(real_type)
    elif isinstance(real_type, Instance):
        return real_type.copy_modified(
            args=kind.args[1:len(real_type.args) + 1],
        )

    # This should never happen, probably can be an exception:
    return AnyType(TypeOfAny.implementation_artifact)
