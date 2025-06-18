from returns.future import future_safe
from returns.pipeline import is_successful


@future_safe((Exception,), add_note_on_failure=True)
async def error_throwing_function() -> None:
    """Raises an exception."""
    raise ValueError('This is an error!')


@future_safe((Exception,), add_note_on_failure='A custom message')
async def error_throwing_function_with_message() -> None:
    """Raises an exception."""
    raise ValueError('This is an error!')


@future_safe((Exception,), add_note_on_failure='')
async def error_throwing_function_with_empty_str() -> None:
    """Raises an exception."""
    raise ValueError('This is an error!')


@future_safe
async def error_throwing_function_without_note() -> None:
    """Raises an exception."""
    raise ValueError('This is an error!')


async def test_add_note_safe() -> None:
    """Tests the add_note decorator with safe."""
    result = await error_throwing_function()

    print(result)
    print(result.failure()._inner_value.__notes__)
    print(result.failure())
    assert not is_successful(result)
    assert (
        'Exception occurred in error_throwing_function'
        in result.failure()._inner_value.__notes__[0]
    )


async def test_add_note_safe_with_message() -> None:
    """Tests the add_note decorator with safe."""
    result = await error_throwing_function_with_message()

    print(result)
    print(result.failure()._inner_value.__notes__)
    print(result.failure())
    assert not is_successful(result)
    assert 'A custom message' in result.failure()._inner_value.__notes__
    assert (
        'Exception occurred in error_throwing_function_with_message'
        in result.failure()._inner_value.__notes__[1]
    )


async def test_add_note_safe_with_empty_str() -> None:
    """Tests the add_note decorator with safe."""
    result = await error_throwing_function_with_empty_str()

    print(result)

    # Passing an empty string to add_note_on_failure should be treated as
    # passing False, so no note should be added
    assert not hasattr(result.failure()._inner_value, '__notes__')
    assert not is_successful(result)


async def test_add_note_safe_without_note() -> None:
    """Tests the vanilla functionality of the safe decortaor."""
    result = await error_throwing_function_without_note()

    print(result)

    # Make sure that the add_note_on_failure functionality does not break the
    # vanilla functionality of the safe decorator
    assert not hasattr(result.failure()._inner_value, '__notes__')
    assert not is_successful(result)
