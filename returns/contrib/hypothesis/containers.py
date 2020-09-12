from typing import TYPE_CHECKING, Any, Callable, List, Type

from hypothesis import strategies as st

if TYPE_CHECKING:
    from returns.primitives.laws import Lawful


def strategy_from_container(
    container_type: Type['Lawful'],
    *,
    use_init: bool = False,
) -> Callable[[type], st.SearchStrategy]:
    """
    Creates a strategy from a container type.

    Basically, containers should not support ``__init__``
    even when they have one.
    Because, that can be very complex: for example ``FutureResult`` requires
    ``Awaitable[Result[a, b]]`` as an ``__init__`` value.

    But, custom containers pass ``use_init``
    if they are not an instance of ``ApplicativeN``
    and do not have a working ``.from_value`` method.

    For example, pure ``MappableN`` can do that.
    """
    from returns.interfaces.applicative import ApplicativeN
    from returns.interfaces.specific import maybe, result

    def factory(type_: type) -> st.SearchStrategy:
        strategies: List[st.SearchStrategy[Any]] = []
        if use_init and getattr(container_type, '__init__', None):
            strategies.append(st.builds(container_type))
        if issubclass(container_type, ApplicativeN):
            strategies.append(st.builds(container_type.from_value))
        if issubclass(container_type, result.ResultLikeN):
            strategies.append(st.builds(container_type.from_failure))
        if issubclass(container_type, maybe.MaybeLikeN):
            strategies.append(st.builds(container_type.from_optional))
        return st.one_of(*strategies)
    return factory
