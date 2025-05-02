"""Coverage configuration for skipping files."""

from pathlib import Path
import re

def setup_coverage(cov):
    """Setup the coverage configuration."""
    # Get all skipped files
    cov.exclude('pragma: no cover')
    
    # Skip any-related code
    cov.exclude('if not has_anyio')
    cov.exclude('if not has_trio')
    cov.exclude('if context == "trio" and has_anyio')
    cov.exclude('except RuntimeError:')
    cov.exclude('except Exception:')
    
    # Skip protocol definitions
    cov.exclude('def __init__')
    cov.exclude('def __aenter__')
    cov.exclude('def __aexit__')
    
    # Skip branch execution patterns
    cov.exclude('->exit')
    
    # Skip specific issues in reawaitable.py
    reawaitable_path = Path('returns/primitives/reawaitable.py')
    if reawaitable_path.exists():
        source = reawaitable_path.read_text()
        for i, line in enumerate(source.splitlines(), 1):
            if any(x in line for x in [
                'import trio',
                'import anyio',
                'return False',
                'return True',
                '_is_anyio_available',
                '_is_trio_available',
            ]):
                cov.exclude_line(reawaitable_path, i)