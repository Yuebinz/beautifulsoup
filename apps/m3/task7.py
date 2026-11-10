"""Task 7 (SoupReplacer, Milestone-3 API): give every <p> tag class="test".

Milestone-1 task7 parsed the document, looped over find_all("p") and did
p["class"] = "test". Here the same change happens *while parsing*, through the
xformer argument of SoupReplacer, so there is no second pass over the tree.

Usage: python task7.py <input_file> [output_file] [--compare] [--memory]
"""
import argparse

import _common
from bs4 import SoupReplacer


def add_test_class(tag):
    """xformer: runs on every start tag as the parser creates it."""
    if tag.name == "p":
        tag["class"] = "test"


def modify_during_parsing(path):
    return _common.load_soup(path, replacer=SoupReplacer(xformer=add_test_class))


def modify_after_parsing(path):  # Milestone-1 version, for --compare
    soup = _common.load_soup(path)
    for p in soup.find_all("p"):
        p["class"] = "test"
    return soup


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("output", nargs="?", default="task7_out.html")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--memory", action="store_true", help="also report peak memory (slow)")
    args = ap.parse_args()
    _common.TRACK_MEMORY = args.memory

    soup, secs, peak = _common.measure(lambda: modify_during_parsing(args.file))
    n = len(soup.find_all("p", class_="test"))
    with open(args.output, "w", encoding="utf-8") as out:
        out.write(str(soup))
    print(f'Set class="test" on {n} <p> tags while parsing. Wrote {args.output}')
    _common.report("SoupReplacer xformer", secs, peak)
    if args.compare:
        base, bsecs, bpeak = _common.measure(lambda: modify_after_parsing(args.file))
        _common.report("parse then modify (M1)", bsecs, bpeak)
        print("  output identical to Milestone-1 way:", str(base) == str(soup))


if __name__ == "__main__":
    main()
