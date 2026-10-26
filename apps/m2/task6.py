"""Task 6 (SoupReplacer version): change all <b> tags to <blockquote> and write the tree.

The rename happens *during parsing* (SoupReplacer("b", "blockquote")), so the
extra pass over the tree that Milestone-1 task6 needed (find_all + set .name)
is gone.

Usage: python task6.py <input_file> [output_file] [--compare] [--memory]
"""
import argparse

import _common
from bs4 import SoupReplacer


def replace_during_parsing(path):
    return _common.load_soup(path, replacer=SoupReplacer("b", "blockquote"))


def replace_after_parsing(path):  # Milestone-1 version, for --compare
    soup = _common.load_soup(path)
    for b in soup.find_all("b"):
        b.name = "blockquote"
    return soup


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("output", nargs="?", default="task6_out.html")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--memory", action="store_true", help="also report peak memory (slow)")
    args = ap.parse_args()
    _common.TRACK_MEMORY = args.memory

    soup, secs, peak = _common.measure(lambda: replace_during_parsing(args.file))
    n = len(soup.find_all("blockquote"))
    with open(args.output, "w", encoding="utf-8") as out:
        out.write(str(soup))
    print(f"Replaced <b> by <blockquote> while parsing ({n} <blockquote> in the tree). Wrote {args.output}")
    _common.report("SoupReplacer (in parse)", secs, peak)
    if args.compare:
        base, bsecs, bpeak = _common.measure(lambda: replace_after_parsing(args.file))
        _common.report("parse then rename (M1)", bsecs, bpeak)
        print("  output identical to Milestone-1 way:", str(base) == str(soup))


if __name__ == "__main__":
    main()
