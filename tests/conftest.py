import sys
from pathlib import Path
from types import MappingProxyType
from typing import Optional

from _pytest.config import Config
from py import path as pypath
from typing_extensions import Final

# See https://github.com/HypothesisWorks/hypothesis/pull/2567
pytest_plugins = ['hypothesis.extra.pytestplugin']

PYTHON_VERSION: Final = (sys.version_info.major, sys.version_info.minor)
PATHS_TO_IGNORE: Final = MappingProxyType({
    (3, 7): frozenset((
        Path('tests/test_examples/test_result/test_pattern_matching.py'),
        Path('tests/test_examples/test_maybe/test_pattern_matching.py'),
    )),
    (3, 8): frozenset((
        Path('tests/test_examples/test_result/test_pattern_matching.py'),
        Path('tests/test_examples/test_maybe/test_pattern_matching.py'),
    )),
    (3, 9): frozenset((
        Path('tests/test_examples/test_result/test_pattern_matching.py'),
        Path('tests/test_examples/test_maybe/test_pattern_matching.py'),
    )),
    (3, 10): frozenset((
        Path('tests/test_examples/test_result/test_pattern_matching.py'),
        Path('tests/test_examples/test_maybe/test_pattern_matching.py'),
    )),
})
PATHS_TO_IGNORE_NOW: Final = frozenset(
    path.absolute() for path in PATHS_TO_IGNORE.get(PYTHON_VERSION, frozenset())
)


def pytest_ignore_collect(
    path: pypath.local,
    config: Config,
) -> Optional[bool]:
    """
    Return True to prevent considering this path for collection.

    This hook is consulted for all files and directories prior to calling
    more specific hooks. Stops at first non-None result.
    """
    return Path(path) in PATHS_TO_IGNORE_NOW
