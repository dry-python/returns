from returns.curry import partial


def foo(x, bar=None):
    """Add bar to x if bar is provided, otherwise return x."""
    return x + bar if bar else x


my_partial = partial(foo, bar=1)
# Type checking: reveal_type(my_partial)
