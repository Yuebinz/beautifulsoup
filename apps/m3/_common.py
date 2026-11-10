"""Helpers for the Milestone-3 application programs.

They are the Milestone-2 helpers (apps/m2/_common.py): the local bs4 package is
put on sys.path, and load_soup / measure / report are shared. The file is loaded
by path because both folders have a module called `_common`.
"""
import importlib.util
import os

_M2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "m2", "_common.py")
_spec = importlib.util.spec_from_file_location("_m2_common", _M2)
_m2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m2)

load_soup = _m2.load_soup
report = _m2.report


def measure(fn):
    _m2.TRACK_MEMORY = TRACK_MEMORY
    return _m2.measure(fn)


TRACK_MEMORY = False  # set by --memory
