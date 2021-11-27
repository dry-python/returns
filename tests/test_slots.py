import importlib
import inspect
import pkgutil
from typing import Any, Iterator

import returns


def _classes_in_module(module: Any) -> Iterator[type]:
    yield from (
        klass
        for _, klass in inspect.getmembers(module, inspect.isclass)
        if klass.__module__.startswith(module.__name__)  # noqa: WPS609
    )
    try:
        module_path = module.__path__[0]  # noqa: WPS609
    except AttributeError:
        return  # it's not a package with submodules

    packages = pkgutil.walk_packages([module_path])
    for finder, name, _ in packages:
        if not getattr(finder, 'path', '').startswith(module_path):
            continue

        yield from _classes_in_module(
            importlib.import_module(
                '{0.__name__}.{1}'.format(module, name),
            ),
        )


def _has_slots(klass: type) -> bool:
    return '__slots__' in klass.__dict__ or klass is object  # noqa: WPS609


def test_slots_defined():
    """Ensures __slots__ isn't forgotten anywhere."""
    classes_without_slots = {
        klass
        for klass in _classes_in_module(returns)
        if not _has_slots(klass) and
        all(map(_has_slots, klass.__bases__)) and  # noqa: WPS609
        not klass.__module__.startswith('returns.contrib')  # noqa: WPS609
    }
    assert not classes_without_slots
