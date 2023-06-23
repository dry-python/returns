import pickle  # noqa: S403

from returns.primitives.container import BaseContainer


def test_pickle_backward_deserialization():
    """Test that BaseContainer can be deserialized from 0.19.0 and earlier."""
    # BaseContainer(1) serialized as of 0.19.0
    serialized_container = (
        b'\x80\x04\x958\x00\x00\x00\x00\x00\x00\x00\x8c\x1c' +
        b'returns.primitives.container\x94\x8c\rBaseContainer' +
        b'\x94\x93\x94)\x81\x94K\x01b.'
    )
    assert pickle.loads(serialized_container) == BaseContainer(1)  # noqa: S301
