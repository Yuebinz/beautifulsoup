"""Helpers shared by the Milestone-2 application programs.

Every app in this folder imports the *local* bs4 package in this repository
(not a copy from site-packages), so that it picks up the Milestone-2 changes.
"""
import os
import sys
import time
import tracemalloc

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DEFAULT_PARSER = "html.parser"


def read_markup(path):
    """Read the file once so that file I/O is not part of the timings."""
    with open(path, "rb") as f:
        return f.read()


TRACK_MEMORY = False  # set by --memory; tracemalloc slows parsing several-fold


def measure(fn):
    """Run fn() and return (result, seconds, peak_memory_in_MB or None)."""
    if TRACK_MEMORY:
        tracemalloc.start()
    start = time.perf_counter()
    result = fn()
    seconds = time.perf_counter() - start
    peak = None
    if TRACK_MEMORY:
        peak = tracemalloc.get_traced_memory()[1] / (1024 * 1024)
        tracemalloc.stop()
    return result, seconds, peak


def report(label, seconds, peak_mb):
    mem = "" if peak_mb is None else f"   peak {peak_mb:8.1f} MB"
    print(f"  {label:<28} {seconds:8.2f} s{mem}")


def preview(items, limit):
    """Print the first `limit` items (all of them if limit is 0)."""
    shown = items if not limit else items[:limit]
    for item in shown:
        print("   ", item)
    if limit and len(items) > limit:
        print(f"    ... ({len(items) - limit} more; use --limit 0 to print all)")
