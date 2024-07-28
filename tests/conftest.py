import sys
from pathlib import Path
from types import MappingProxyType
from typing import Final, Optional

import pytest

PYTHON_VERSION: Final = (sys.version_info.major, sys.version_info.minor)
ENABLE_SINCE: Final = MappingProxyType({
    (3, 10): frozenset((
        Path('tests/test_examples/test_result/test_result_pattern_matching.py'),
        Path('tests/test_examples/test_maybe/test_maybe_pattern_matching.py'),
        Path('tests/test_examples/test_io/test_ioresult_container/test_ioresult_pattern_matching.py'),  # noqa: E501
        Path('tests/test_pattern_matching.py'),
    )),
})
PATHS_TO_IGNORE_NOW: Final = frozenset(
    path.absolute()
    for since_python, to_ignore in ENABLE_SINCE.items()
    for path in to_ignore
    if PYTHON_VERSION < since_python
)


def pytest_ignore_collect(
    collection_path: Path,
    config: pytest.Config,
) -> Optional[bool]:
    """
    Return True to prevent considering this path for collection.

    This hook is consulted for all files and directories prior to calling
    more specific hooks. Stops at first non-None result.
    """
    return collection_path in PATHS_TO_IGNORE_NOW
