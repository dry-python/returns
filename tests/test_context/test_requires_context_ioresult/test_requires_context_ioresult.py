from returns.context import RequiresContextIOResultE
from returns.io import IOSuccess


def test_regression394():
    """
    It used to raise ``ImmutableStateError`` for type aliases.

    Here we use the minimal reproduction sample.

    .. code:: python

      Traceback (most recent call last):
        File "ex.py", line 18, in <module>
            get_ip_addr("https://google.com")
        File "ex.py", line 13, in get_ip_addr
            return RequiresContextIOResultE(lambda _: IOSuccess(1))
        File "../3.7.7/lib/python3.7/typing.py", line 677, in __call__
            result.__orig_class__ = self
        File "../returns/returns/primitives/types.py", line 42, in __setattr__
            raise ImmutableStateError()
        returns.primitives.exceptions.ImmutableStateError

    See: https://github.com/dry-python/returns/issues/394

    """
    RequiresContextIOResultE(lambda _: IOSuccess(1))
