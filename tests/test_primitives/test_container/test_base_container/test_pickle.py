import pickle  # noqa: S403
from typing import Any

from hypothesis import example, given
from hypothesis import strategies as st

from returns.primitives.container import BaseContainer


class _CustomClass:
    def __init__(self, inner_value: Any) -> None:
        self.inner_value = inner_value

    def __eq__(self, other: object) -> bool:
        return (
            type(other) is type(self)  # noqa: WPS516
            and self.inner_value == other.inner_value  # type: ignore[attr-defined]
        )

    def __hash__(self) -> int:
        return hash(self.inner_value)


@given(
    st.one_of(
        st.integers(),
        st.floats(allow_nan=False),
        st.text(),
        st.booleans(),
        st.lists(st.text()),
        st.dictionaries(st.text(), st.integers()),
        st.builds(_CustomClass, st.text()),
    ),
)
@example(None)
def test_pickle(container_value: Any):
    """Ensures custom pickle protocol works as expected."""
    container = BaseContainer(container_value)
    assert pickle.loads(pickle.dumps(container)) == container  # noqa: S301
