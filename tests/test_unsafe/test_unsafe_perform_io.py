from returns.io import IO
from returns.unsafe import unsafe_perform_io


def test_unsafe_perform_io():
    """Ensures that unsafe_perform_io returns the object itself."""
    id_object = object()
    assert unsafe_perform_io(IO(id_object)) is id_object
