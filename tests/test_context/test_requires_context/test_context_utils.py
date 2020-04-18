from returns.context import Context, RequiresContext


def test_context_ask():
    """Ensures that ``ask`` method works correctly."""
    assert Context[int].ask()(1) == 1
    assert Context[str].ask()('a') == 'a'


def test_requires_context_from_value():
    """Ensures that ``from_value`` method works correctly."""
    assert RequiresContext.from_value(1)(RequiresContext.empty) == 1
    assert RequiresContext.from_value(2)(1) == 2
