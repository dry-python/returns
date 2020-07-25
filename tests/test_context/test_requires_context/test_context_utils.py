from returns.context import RequiresContext


def test_context_ask():
    """Ensures that ``ask`` method works correctly."""
    assert RequiresContext[str, int].ask()(1) == 1
    assert RequiresContext[int, str].ask()('a') == 'a'


def test_requires_context_from_value():
    """Ensures that ``from_value`` method works correctly."""
    assert RequiresContext.from_value(1)(RequiresContext.empty) == 1
    assert RequiresContext.from_value(2)(1) == 2
