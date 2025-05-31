from hypothesis import HealthCheck
from hypothesis import strategies as st

from returns.contrib.hypothesis.laws import check_all_laws

from . import test_custom_type_applicative  # noqa: WPS300

container_type = test_custom_type_applicative._Wrapper  # noqa: SLF001

check_all_laws(
    container_type,
    container_strategy=st.builds(container_type, st.integers()),
    settings_kwargs={'suppress_health_check': [HealthCheck.too_slow]},
)
