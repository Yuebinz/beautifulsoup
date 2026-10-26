"""Task 3 (SoupStrainer version): print the name of every tag.

Honest result: this is the task where SoupStrainer helps least. Every tag has
to be kept, so the strainer (name=True, "match any tag") accepts the root
element and with it the whole document. The tree has the same tags as a plain
parse, and the time is almost the same (on a 4 MB file: 13.3 s vs 16.3 s). A
strainer only saves a lot when it can *reject* big parts of the document,
as in task2.

Usage: python task3.py <input_file> [--compare] [--memory]
"""
import argparse

import _common
from bs4 import SoupStrainer


def get_tags(path):
    soup = _common.load_soup(path, parse_only=SoupStrainer(name=True))
    return soup.find_all(True)


def get_tags_full_parse(path):  # Milestone-1 version, for --compare
    return _common.load_soup(path).find_all(True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--memory", action="store_true", help="also report peak memory (slow)")
    args = ap.parse_args()
    _common.TRACK_MEMORY = args.memory

    tags, secs, peak = _common.measure(lambda: get_tags(args.file))
    for tag in tags:
        print(tag.name)
    print(f"\nTotal tags: {len(tags)}")
    _common.report("SoupStrainer parse", secs, peak)
    if args.compare:
        base, bsecs, bpeak = _common.measure(lambda: get_tags_full_parse(args.file))
        _common.report("full parse (Milestone 1)", bsecs, bpeak)
        print("  same tags as full parse:", [t.name for t in base] == [t.name for t in tags])


if __name__ == "__main__":
    main()
