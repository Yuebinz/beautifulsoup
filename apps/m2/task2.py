"""Task 2 (SoupStrainer version): print all hyperlinks (<a> tags).

Same output as Milestone-1 task2, but a SoupStrainer makes the parser keep
only <a> elements, so nothing else is ever built into the tree.

Usage: python task2.py <input_file> [--compare] [--memory]
  --compare  also run the Milestone-1 way (full parse) and compare time/result
"""
import argparse

import _common
from bs4 import SoupStrainer


def get_links(path):
    soup = _common.load_soup(path, parse_only=SoupStrainer("a"))
    return soup.find_all("a")


def get_links_full_parse(path):  # Milestone-1 version, for --compare
    return _common.load_soup(path).find_all("a")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--memory", action="store_true", help="also report peak memory (slow)")
    args = ap.parse_args()
    _common.TRACK_MEMORY = args.memory

    links, secs, peak = _common.measure(lambda: get_links(args.file))
    for a in links:
        print(a)
    print(f"\nTotal <a> tags: {len(links)}")
    _common.report("SoupStrainer parse", secs, peak)
    if args.compare:
        base, bsecs, bpeak = _common.measure(lambda: get_links_full_parse(args.file))
        _common.report("full parse (Milestone 1)", bsecs, bpeak)
        print("  same links as full parse:", [str(x) for x in base] == [str(x) for x in links])


if __name__ == "__main__":
    main()
