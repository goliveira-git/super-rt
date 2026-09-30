"""Runs pytest on the test file given as the first argument; extra arguments go to pytest."""

import sys

import pytest

test_file, *extra = sys.argv[1:]
sys.exit(pytest.main([test_file, "-p", "no:cacheprovider", *extra]))
