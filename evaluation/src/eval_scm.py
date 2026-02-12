"""
Evaluates a generated Scheme program (.scm).
"""
import os
from pathlib import Path
from safe_subprocess import run
from re import search

def eval_script(path: Path):
    result = run(
        ["guile", "--no-auto-compile", str(path)],
        max_output_size=16384 # Guile has long errors. :)
    )
    if result.timeout:
        status = "Timeout"
    elif result.exit_code != 0:
        status = "Exception"
    elif search(r"# of unexpected failures +[1-9]+", result.stdout):
        status = "Exception"
    elif search(r"# of expected passes +[1-9]+", result.stdout):
        status = "OK"
    else:
        status = "Exception"
    return {
        "status": status,
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

if __name__ == "__main__":
    main()
