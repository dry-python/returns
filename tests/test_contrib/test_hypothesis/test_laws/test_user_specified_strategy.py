from hypothesis import strategies as st
from test_hypothesis.test_laws import test_custom_type_applicative

from returns.contrib.hypothesis.laws import check_all_laws

container_type = test_custom_type_applicative._Wrapper  # noqa: SLF001

check_all_laws(
    container_type,
    container_strategy=st.builds(container_type, st.integers()),
)
