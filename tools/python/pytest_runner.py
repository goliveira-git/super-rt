"""Runs pytest on the test file given as the first argument, skipping hardware, gpu and cloud tests.

Extra arguments are forwarded to pytest; pass -m to override the default marker filter.
"""

import sys

import pytest

DEFAULT_MARKERS = "not hardware and not gpu and not cloud"

test_file, *extra = sys.argv[1:]
args = [test_file, *extra]
if "-m" not in extra:
    args += ["-m", DEFAULT_MARKERS]
sys.exit(pytest.main(args))
