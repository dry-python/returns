import copy
import sys
from typing import TYPE_CHECKING, Any

import pytest
from hypothesis import example, given
from hypothesis import strategies as st

from returns.primitives.container import BaseContainer

# For Python < 3.13 compatibility: copy.replace doesn't exist in older Python
if TYPE_CHECKING:  # pragma: no cover
    # Defining a dummy replace function for type checking
    def _replace(container_instance: Any, /, inner_value: Any) -> Any:
        """Dummy replace function for type checking."""
        return container_instance

    # Assigning it to copy.replace for type checking
    if not hasattr(copy, 'replace'):
        copy.replace = _replace  # type: ignore


class _CustomClass:
    """A custom class for replace testing."""

    __slots__ = ('inner_value',)

    def __init__(self, inner_value: str) -> None:
        """Initialize instance."""
        self.inner_value = inner_value

    def __eq__(self, other: object) -> bool:
        """Compare with other."""
        if isinstance(other, _CustomClass):
            return self.inner_value == other.inner_value
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        """Not equal to other."""
        if isinstance(other, _CustomClass):
            return self.inner_value != other.inner_value
        return NotImplemented

    def __hash__(self) -> int:
        """Return hash of the inner value."""
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
def test_replace_method(container_value: Any) -> None:
    """Ensures __replace__ magic method works as expected."""
    container = BaseContainer(container_value)

    # Test with new inner_value returns a new container
    new_value = 'new_value'
    # Test direct call to __replace__
    new_container = container.__replace__(new_value)  # noqa: PLC2801

    assert new_container is not container
    assert new_container._inner_value == new_value  # noqa: SLF001
    assert isinstance(new_container, BaseContainer)
    assert type(new_container) is type(container)  # noqa: WPS516


def test_base_container_replace_direct_call():
    """Test direct call to the __replace__ method."""
    container = BaseContainer(1)  # Create instance directly
    new_value = 'new_value'
    # Test direct call to __replace__
    new_container = container.__replace__(new_value)  # noqa: PLC2801

    assert new_container is not container
    assert new_container._inner_value == new_value  # noqa: SLF001
    assert isinstance(new_container, BaseContainer)
    assert type(new_container) is type(container)  # noqa: WPS516


def test_replace_direct_call_invalid_args():
    """Ensures calling replace directly with invalid arguments raises error."""
    container = BaseContainer(1)  # Create instance directly
    with pytest.raises(TypeError, match='unexpected keyword argument'):
        container.__replace__(other_kwarg='value')  # type: ignore[attr-defined]


@pytest.mark.skipif(
    sys.version_info < (3, 13),
    reason='copy.replace requires Python 3.13+',
)
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
def test_copy_replace(container_value: Any) -> None:
    """Ensures copy.replace works with BaseContainer."""
    container = BaseContainer(container_value)

    # Test with no changes is not directly possible via copy.replace with this
    # __replace__ implementation.
    # The copy.replace function itself handles the no-change case if the
    # object supports it, but our __replace__ requires a value.

    # Test with new inner_value returns a new container using copy.replace
    new_value = 'new_value'
    # copy.replace calls __replace__ with the new value as a positional arg
    new_container = copy.replace(container, new_value)  # type: ignore[attr-defined]

    assert new_container is not container
    assert new_container._inner_value == new_value  # noqa: SLF001
    assert isinstance(new_container, BaseContainer)
    assert type(new_container) is type(container)  # noqa: WPS516


@pytest.mark.skipif(
    sys.version_info < (3, 13),
    reason='copy.replace requires Python 3.13+',
)
def test_replace_copy_no_changes(container_value):
    """
    Ensures calling copy.replace without changes yields a different container.

    With the same inner value.
    """
    container = BaseContainer(container_value)
    original_value = container._inner_value  # noqa: SLF001
    new_container = copy.replace(container, container_value)

    assert new_container is not container
    assert new_container._inner_value == original_value  # noqa: SLF001


@pytest.mark.skipif(
    sys.version_info < (3, 13),
    reason='copy.replace requires Python 3.13+',
)
def test_replace_copy_invalid_args(container):
    """Ensures calling copy.replace with invalid arguments raises error."""
    with pytest.raises(TypeError, match='unexpected keyword argument'):
        copy.replace(container, other_kwarg='value')  # type: ignore[attr-defined]

    # copy.replace should raise TypeError if extra positional arguments
    # are passed.
    with pytest.raises(TypeError):
        copy.replace(container, 'new', 'extra')  # type: ignore[attr-defined]

    # copy.replace should raise TypeError if no value is passed
    # (our __replace__ requires one).
    with pytest.raises(TypeError):
        copy.replace(container)  # type: ignore[attr-defined]
