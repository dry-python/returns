import pytest

from returns.io import IO
from returns.primitives.interfaces import Bindable, Instanceable, Mappable


@pytest.mark.parametrize('container', [
    IO(''),
])
@pytest.mark.parametrize('protocol', [
    Bindable,
    Mappable,
    Instanceable,
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
