from functools import reduce
from typing import Iterable


def _reducer(acc, current):
    return acc.bind(
        lambda inner_acc: current.map(
            lambda inner_current: inner_acc + (inner_current,),  # noqa: WPS430
        ),
    )


def iterable(cls, sequence: Iterable):
    """
    Evaluate container actions from iterable, collecting results.

    This function should not be used directly.
    Use ``.from_iterable`` container methods instead.
    """
    return reduce(_reducer, sequence, cls.from_value(()))
