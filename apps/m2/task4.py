"""Task 4 (SoupStrainer version): print all tags that have an id attribute.

Usage: python task4.py <input_file> [--compare] [--memory]
"""
import argparse

import _common
from bs4 import SoupStrainer


def get_tags_with_id(path):
    soup = _common.load_soup(path, parse_only=SoupStrainer(id=True))
    return soup.find_all(id=True)


def get_tags_with_id_full_parse(path):  # Milestone-1 version, for --compare
    return _common.load_soup(path).find_all(id=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--memory", action="store_true", help="also report peak memory (slow)")
    args = ap.parse_args()
    _common.TRACK_MEMORY = args.memory

    tags, secs, peak = _common.measure(lambda: get_tags_with_id(args.file))
    for tag in tags:
        print(f"<{tag.name}> id={tag['id']!r}")
    print(f"\nTotal tags with id: {len(tags)}")
    _common.report("SoupStrainer parse", secs, peak)
    if args.compare:
        base, bsecs, bpeak = _common.measure(lambda: get_tags_with_id_full_parse(args.file))
        _common.report("full parse (Milestone 1)", bsecs, bpeak)
        print("  same tags as full parse:", [(t.name, t["id"]) for t in base] == [(t.name, t["id"]) for t in tags])


if __name__ == "__main__":
    main()
