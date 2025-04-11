from returns.result import safe
from returns.pipeline import is_successful


@safe((Exception,), add_note_on_failure=True)
def error_throwing_function() -> None:
    """Raises an exception."""
    raise ValueError("This is an error!")


@safe((Exception,), add_note_on_failure="A custom message")
def error_throwing_function_with_message() -> None:
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
        "Exception occurred in error_throwing_function"
        in result.failure().__notes__[0]
    )


def test_add_note_safe_with_message() -> None:
    """Tests the add_note decorator with safe."""

    result = error_throwing_function_with_message()

    print(result)
    print(result.failure().__notes__)
    print(result.failure())
    assert not is_successful(result)
    assert "A custom message" in result.failure().__notes__
    assert (
        "Exception occurred in error_throwing_function_with_message"
        in result.failure().__notes__[1]
    )
