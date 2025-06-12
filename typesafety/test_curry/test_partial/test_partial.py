import pytest
from typing_extensions import reveal_type

from returns.curry import partial

TEST_STR = 'a'


def test_partial_fn(  # noqa: WPS221
    first_arg: int,
    optional_arg: str | None,
) -> tuple[int, str | None]:
    """Return arguments as a tuple."""
    return first_arg, optional_arg


def test_partial():
    """Ensures that ``partial`` works correctly."""
    bound = partial(test_partial_fn, 1)
    reveal_type(bound)  # noqa: WPS421 # R: Revealed type is 'def (*, optional_arg: Union[builtins.str, None] =) -> Tuple[builtins.int, Union[builtins.str, None]]'

    assert bound() == (1, None)
    assert bound(optional_arg=TEST_STR) == (1, TEST_STR)


def test_partial_with_decorator():
    """Ensures that ``partial`` works correctly with decorators."""

    @partial(first=1)
    def _decorated(first: int, second: str) -> float:  # noqa: WPS430
        return first / float(second)

    reveal_type(_decorated)  # noqa: WPS421 # R: Revealed type is 'def (second: builtins.str) -> builtins.float'

    assert _decorated(second='2') == pytest.approx(0.5)


def test_partial_keyword():
    """Ensures that ``partial`` works correctly with keyword args."""
    bound = partial(test_partial_fn, optional_arg=TEST_STR)
    reveal_type(bound)  # noqa: WPS421 # R: Revealed type is 'def (first_arg: builtins.int) -> Tuple[builtins.int, builtins.str]'

    assert bound(1) == (1, TEST_STR)


def test_partial_keyword_only():
    """Ensures that ``partial`` works with keyword only args."""

    def _target(*, arg: int) -> int:  # noqa: WPS430
        return arg

    bound = partial(_target, arg=1)
    reveal_type(bound)  # noqa: WPS421 # R: Revealed type is 'def () -> builtins.int'

    assert bound() == 1


def test_partial_keyword_mixed():
    """Ensures that ``partial`` works with keyword only args."""

    def _target(arg1: int, *, arg2: int) -> int:  # noqa: WPS430
        return arg1 + arg2

    bound = partial(_target, arg2=1)
    reveal_type(bound)  # noqa: WPS421 # R: Revealed type is 'def (arg1: builtins.int) -> builtins.int'

    assert bound(1) == 2


def test_partial_wrong_signature():
    """Ensures that ``partial`` returns ``Any`` for wrong signature."""
    reveal_type(partial(len, 1))  # noqa: WPS421 # R: Revealed type is 'Any'
    with pytest.raises(TypeError):
        partial(len, 1)()
