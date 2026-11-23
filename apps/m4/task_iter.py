"""Milestone 4 application: walk a whole document with `for node in soup`.

Counts every kind of node, optionally prints them, and (--compare) checks the
iteration visits as many nodes as Milestone-1 style traversal
(soup.find_all(True) plus the strings), which builds lists.

Usage: python task_iter.py <input_file> [--print] [--compare] [--memory]
"""
import argparse
import collections
import os
import sys
import time
import tracemalloc

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from bs4 import BeautifulSoup, FeatureNotFound  # noqa: E402


def load(path):
    parser = "xml" if path.lower().endswith(".xml") else "html.parser"
    with open(path, encoding="utf-8", errors="replace") as f:
        try:
            return BeautifulSoup(f, parser)
        except FeatureNotFound:
            f.seek(0)
            return BeautifulSoup(f, "html.parser")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--print", action="store_true", help="print every node")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--memory", action="store_true", help="peak memory of the walk")
    args = ap.parse_args()

    soup = load(args.file)
    counts = collections.Counter()
    if args.memory:
        tracemalloc.start()
    start = time.perf_counter()
    for node in soup:  # the Milestone-4 API
        counts[type(node).__name__] += 1
        if args.print:
            print(repr(node)[:80])
    secs = time.perf_counter() - start
    peak = None
    if args.memory:
        peak = tracemalloc.get_traced_memory()[1] / 1024
        tracemalloc.stop()

    total = sum(counts.values())
    extra = f", peak extra memory {peak:.1f} KiB" if peak is not None else ""
    print(f"{total} nodes in {secs:.3f}s{extra}")
    for kind, n in counts.most_common():
        print(f"  {kind}: {n}")
    if args.compare:
        listed = soup.find_all(True) + soup.find_all(string=True)
        print("  tags + strings via find_all (builds a list):", len(listed))
        print("  same node count as iteration:", len(listed) == total)


if __name__ == "__main__":
    main()
