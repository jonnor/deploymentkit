"""Utilities for use in tests."""

import os.path

# FIXME: make lookup independent of current working directory
def get_testdata_file(basename):
    """Return the path to the test data file with basename."""
    path = os.path.join('tests/data', basename)
    return path
