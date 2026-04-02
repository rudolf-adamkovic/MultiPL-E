"""
Evaluates a generated R7RS Scheme program using GNU Guile.

Loads all 36 SRFIs shipped with Guile via --use-srfi, making them
available at runtime without explicit imports in the source code.

- https://r7rs.org/
- https://www.gnu.org/software/guile/
"""

from pathlib import Path
from eval_scm import eval_script as _eval_script

_SRFIS = [
    1, 2, 4, 6, 8, 9, 10, 11, 13, 14, 16, 17, 18, 19, 26, 27, 28,
    31, 34, 35, 37, 38, 39, 41, 42, 43, 45, 60, 64, 67, 69, 71,
    88, 98, 111, 171,
]

_USE_SRFI = "--use-srfi=" + ",".join(str(n) for n in _SRFIS)

def eval_script(path: Path):
    return _eval_script(path, extra_flags=["--r7rs", _USE_SRFI])
