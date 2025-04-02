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


def test_base_container_replace_direct_call_invalid_args():
    """Test direct call with invalid arguments."""
    container = BaseContainer(1)  # Create instance directly
    # Direct call with no args should fail
    with pytest.raises(TypeError):
        container.__replace__()  # noqa: PLC2801

    # Direct call with keyword args matching the name is allowed by Python,
    # even with /.
    # If uncommented, it should pass as Python allows this.
    # Removing commented test case for
    # `container.__replace__(inner_value='new')`

    # Direct call with extra positional args should fail
    with pytest.raises(TypeError):
        container.__replace__('new', 'extra')  # noqa: PLC2801

    # Direct call with unexpected keyword args should fail
    with pytest.raises(TypeError):
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
def test_base_container_replace_via_copy_no_changes(container_value):
    """Test copy.replace with no actual change in value."""
    container = BaseContainer(container_value)

    # Test with no changes is not directly possible via copy.replace with this
    # __replace__ implementation.
    # The copy.replace function itself handles the no-change case if the
    # object supports it, but our __replace__ requires a value.
    # If copy.replace is called with the same value, it should work.
    new_container = copy.replace(container, inner_value=container_value)

    assert new_container is not container  # A new instance should be created


@pytest.mark.skipif(
    sys.version_info < (3, 13),
    reason='copy.replace requires Python 3.13+',
)
def test_base_container_replace_via_copy_invalid_args(container):
    """Test copy.replace with invalid arguments."""
    # copy.replace converts the keyword 'inner_value' to a positional arg
    # for __replace__(self, /, inner_value), so this is valid.
    # Removing commented out test case for copy.replace with inner_value kwarg

    # However, passing other keyword arguments will fail because __replace__
    # doesn't accept them.
    with pytest.raises(TypeError):
        copy.replace(container, other_kwarg='value')  # type: ignore[attr-defined]

    # copy.replace should raise TypeError if extra positional arguments
    # are passed.
    with pytest.raises(TypeError):
        copy.replace(container, 'new', 'extra')  # type: ignore[attr-defined]

    # copy.replace should raise TypeError if no value is passed
    # (our __replace__ requires one).
    with pytest.raises(TypeError):
        copy.replace(container)  # type: ignore[attr-defined]
