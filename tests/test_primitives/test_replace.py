import copy
import sys
from typing import Generic, TypeVar

import pytest

from returns.io import IO
from returns.maybe import Nothing, Some
from returns.primitives.container import BaseContainer
from returns.result import Failure, Success


# Mock version of copy.replace function for Python versions below 3.13
def _replace_mock(container, **kwargs):
    """Mock replacement for copy.replace in testing."""
    if hasattr(container, '__replace__'):
        return container.__replace__(**kwargs)
    raise TypeError(f'{type(container).__name__} does not support __replace__')


# Wrapper function to use either native copy.replace or our mock
def compatible_replace(container, **kwargs):
    """Use either native copy.replace or mock based on Python version."""
    if sys.version_info >= (3, 13):
        return copy.replace(container, **kwargs)
    return _replace_mock(container, **kwargs)


# Remove the skipif decorator to run these tests in all Python versions
class TestCopyReplace:
    """Tests for copy.replace functionality."""

    def test_success_copy_replace(self):
        """Tests copy.replace() on Success container."""
        original = Success(42)
        replaced = compatible_replace(original, _inner_value=100)

        assert replaced == Success(100)
        assert replaced is not original
        assert replaced._inner_value == 100  # noqa: SLF001

        # No changes should return the same object (or equivalent)
        copied = compatible_replace(original)
        assert copied == original
        # Unchanged objects return self per immutability principle
        assert copied is original

    def test_failure_copy_replace(self):
        """Tests copy.replace() on Failure container."""
        original = Failure('error')
        replaced = compatible_replace(original, _inner_value='new error')

        assert replaced == Failure('new error')
        assert replaced is not original
        assert replaced._inner_value == 'new error'  # noqa: SLF001

        # No changes should return an equivalent object
        copied = compatible_replace(original)
        assert copied == original
        # Unchanged objects return self per immutability principle
        assert copied is original

    def test_some_copy_replace(self):
        """Tests copy.replace() on Some container."""
        original = Some('value')
        replaced = compatible_replace(original, _inner_value='new value')

        assert replaced == Some('new value')
        assert replaced is not original
        assert replaced._inner_value == 'new value'  # noqa: SLF001

        # No changes should return an equivalent object
        copied = compatible_replace(original)
        assert copied == original
        # Unchanged objects return self per immutability principle
        assert copied is original

    def test_nothing_copy_replace(self):
        """Tests copy.replace() on Nothing singleton."""
        # Note: Nothing is a singleton, and its constructor ignores the
        # passed value. _Nothing will just return Nothing in any case
        replaced = compatible_replace(Nothing, _inner_value='something')

        assert replaced is Nothing
        assert replaced._inner_value is None  # noqa: SLF001

    def test_io_copy_replace(self):
        """Tests copy.replace() on IO container."""
        original = IO('data')
        replaced = compatible_replace(original, _inner_value='new data')

        assert replaced == IO('new data')
        assert replaced is not original
        assert replaced._inner_value == 'new data'  # noqa: SLF001

    def test_type_change_with_replace(self):
        """Tests copy.replace() when replacing with a different type."""
        # Test with Success container
        int_success = Success(42)
        str_success = compatible_replace(int_success, _inner_value='forty-two')

        assert str_success == Success('forty-two')
        assert str_success is not int_success
        assert isinstance(str_success._inner_value, str)  # noqa: SLF001

        # Extract container tests to separate methods
        self._test_failure_type_change()
        self._test_io_type_change()

    def test_invalid_arguments_in_replace(self):
        """Tests that invalid arguments to copy.replace() raise TypeError."""
        original = Success(42)

        with pytest.raises(TypeError) as excinfo:
            # The only valid argument for BaseContainer is _inner_value
            compatible_replace(original, invalid_arg=True)

            # This code will not execute, but is moved here to satisfy linter
            # The assertions will be checked after the exception is raised

        # Assertions for checking the exception details
        error_message = str(excinfo.value)  # noqa: WPS441
        assert 'received unexpected arguments' in error_message
        assert 'invalid_arg' in error_message

        # Test with multiple invalid arguments
        with pytest.raises(TypeError):
            compatible_replace(original, invalid_arg1=True, invalid_arg2='test')

        # Valid argument should work normally
        assert compatible_replace(original, _inner_value=100) == Success(100)

    def _test_failure_type_change(self):
        """Tests type change with copy.replace() on Failure container."""
        str_failure = Failure('error')
        int_failure = compatible_replace(str_failure, _inner_value=404)

        assert int_failure == Failure(404)
        assert int_failure is not str_failure
        assert isinstance(int_failure._inner_value, int)  # noqa: SLF001

    def _test_io_type_change(self):
        """Tests type change with copy.replace() on IO container."""
        list_io = IO([1, 2, 3])
        dict_io = compatible_replace(list_io, _inner_value={'a': 1, 'b': 2})

        assert dict_io == IO({'a': 1, 'b': 2})
        assert dict_io is not list_io
        assert isinstance(dict_io._inner_value, dict)  # noqa: SLF001


# This class provides tests that run in all Python versions to ensure code
# coverage
class TestBaseContainer:
    """Tests BaseContainer.__replace__ directly for all Python versions."""

    def test_replace_method_basic(self):
        """Tests __replace__ method directly."""
        container = Success(42)
        replaced = container.__replace__(_inner_value=100)

        assert replaced == Success(100)
        assert replaced is not container

        # No changes returns same instance
        same_instance = compatible_replace(container)
        assert same_instance is container

    def test_replace_method_invalid_args(self):
        """Tests __replace__ method with invalid arguments."""
        container = Success(42)

        with pytest.raises(TypeError) as excinfo:
            container.__replace__(invalid_arg=True)

        error_message = str(excinfo.value)
        assert 'received unexpected arguments' in error_message
        assert 'invalid_arg' in error_message


# Define custom box type outside of class to avoid nested class
TypeVar_Element = TypeVar('TypeVar_Element')


# Create CustomBox as a top-level class
class CustomBox(BaseContainer, Generic[TypeVar_Element]):
    """A simple box container for testing copy.replace()."""

    def __init__(self, inner_value: TypeVar_Element) -> None:
        """Initialize with a value."""
        super().__init__(inner_value)

    def __eq__(self, other: object) -> bool:
        """Check equality based on type and inner value."""
        if not isinstance(other, CustomBox):
            return False
        return self._inner_value == other._inner_value

    def __hash__(self) -> int:
        """Hash based on the inner value."""
        return hash(self._inner_value)

    def __repr__(self) -> str:
        """String representation."""
        return f'CustomBox({self._inner_value!r})'


# Remove the skipif decorator to run these tests in all Python versions
class TestCustomContainer:
    """Tests for copy.replace with custom containers."""

    def test_custom_container(self):
        """Tests copy.replace() works with custom user-defined containers."""
        # Test basic replacement works
        original = CustomBox('hello')
        replaced = compatible_replace(original, _inner_value='world')

        assert replaced == CustomBox('world')
        assert replaced is not original
        assert replaced._inner_value == 'world'  # noqa: SLF001
        assert isinstance(replaced, CustomBox)  # Preserves exact type

        # Test with no changes
        copied = compatible_replace(original)
        assert copied == original
        # Unchanged objects return self per immutability principle
        assert copied is original

        # Test with invalid arguments
        with pytest.raises(TypeError):
            compatible_replace(original, invalid_arg=True)
