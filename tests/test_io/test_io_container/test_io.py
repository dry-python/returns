import pytest

from returns.io import IO, IOFailure, IOResult, IOSuccess
from returns.primitives.interfaces import Applicative, Bindable, Mappable


@pytest.mark.parametrize('container', [
    IO(''),
])
@pytest.mark.parametrize('protocol', [
    Bindable,
    Mappable,
    Applicative,
])
def test_protocols(container, protocol):
    """Ensures that IO has all the right protocols."""
    assert isinstance(container, protocol)


def test_io_map():
    """Ensures that IO container supports ``.map()`` method."""
    io: IO[float] = IO(1).map(
        lambda number: number / 2,
    )

    assert io == IO(0.5)


def test_io_bind():
    """Ensures that IO container supports ``.bind()`` method."""
    io: IO[int] = IO('1').bind(
        lambda number: IO(int(number)),
    )

    assert io == IO(1)


def test_io_str():
    """Ensures that IO container supports str cast."""
    assert str(IO([])) == '<IO: []>'


@pytest.mark.parametrize('container', [
    IOSuccess(1),
    IOFailure(1),
])
def test_io_typecast_reverse(container):
    """Ensures that IO can be casted to IOResult and back."""
    assert IO.from_ioresult(container) == IO.from_ioresult(
        IOResult.from_typecast(IO.from_ioresult(container)),
    )
