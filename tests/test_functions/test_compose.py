from returns.functions import compose


def _first(argument: int) -> str:
    return str(argument)


def _second(argument: str) -> bool:
    return bool(argument)


def test_function_composition():
    """Ensures that functions can be composed and return type is correct."""
    second_after_first = compose(_first, _second)

    assert second_after_first(1) is True
    assert second_after_first(0) is True
