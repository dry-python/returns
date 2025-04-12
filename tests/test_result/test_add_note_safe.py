from returns.pipeline import is_successful
from returns.result import safe


@safe((Exception,), add_note_on_failure=True)
def error_throwing_function() -> None:
    """Raises an exception."""
    raise ValueError('This is an error!')


@safe((Exception,), add_note_on_failure='A custom message')
def error_throwing_function_with_message() -> None:
    """Raises an exception."""
    raise ValueError('This is an error!')


@safe((Exception,), add_note_on_failure="")
def error_throwing_function_with_empty_str() -> None:
    """Raises an exception."""
    raise ValueError("This is an error!")


@safe
def error_throwing_function_without_note() -> None:
    """Raises an exception."""
    raise ValueError("This is an error!")


def test_add_note_safe() -> None:
    """Tests the add_note decorator with safe."""
    result = error_throwing_function()

    print(result)
    print(result.failure().__notes__)
    print(result.failure())
    assert not is_successful(result)
    assert (
        'Exception occurred in error_throwing_function'
        in result.failure().__notes__[0]
    )


def test_add_note_safe_with_message() -> None:
    """Tests the add_note decorator with safe."""
    result = error_throwing_function_with_message()

    print(result)
    print(result.failure().__notes__)
    print(result.failure())
    assert not is_successful(result)
    assert 'A custom message' in result.failure().__notes__
    assert (
        'Exception occurred in error_throwing_function_with_message'
        in result.failure().__notes__[1]
    )


def test_add_note_safe_with_empty_str() -> None:
    """Tests the add_note decorator with safe."""

    result = error_throwing_function_with_empty_str()

    print(result)

    # Passing an empty string to add_note_on_failure should be treated as
    # passing False, so no note should be added
    assert not hasattr(result.failure(), "__notes__")
    assert not is_successful(result)


def test_add_note_safe_without_note() -> None:
    """Tests the vanilla functionality of the safe decortaor."""

    result = error_throwing_function_without_note()

    print(result)

    # Make sure that the add_note_on_failure functionality does not break the
    # vanilla functionality of the safe decorator
    assert not hasattr(result.failure(), "__notes__")
    assert not is_successful(result)
