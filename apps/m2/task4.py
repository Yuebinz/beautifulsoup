"""Task 4 (SoupStrainer version): find every element that has an id attribute.

Only elements carrying an ``id`` are kept while parsing.

Usage: python apps/m2/task4.py FILE [--parser html.parser] [--limit 10] [--no-baseline] [--memory]
"""
import argparse

import _common
from bs4 import BeautifulSoup, SoupStrainer


def ids_with_strainer(markup, parser):
    only_ids = SoupStrainer(id=True)
    soup = BeautifulSoup(markup, parser, parse_only=only_ids)
    return [(t.name, t["id"]) for t in soup.find_all(id=True)]


def ids_full_parse(markup, parser):  # Milestone-1 style, used for comparison
    soup = BeautifulSoup(markup, parser)
    return [(t.name, t["id"]) for t in soup.find_all(id=True)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--parser", default=_common.DEFAULT_PARSER)
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--no-baseline", action="store_true")
    ap.add_argument("--memory", action="store_true", help="also report peak memory (slow)")
    args = ap.parse_args()
    _common.TRACK_MEMORY = args.memory

    markup = _common.read_markup(args.file)
    found, secs, peak = _common.measure(lambda: ids_with_strainer(markup, args.parser))
    print(f"Task 4: {len(found)} elements with an id")
    _common.preview([f"<{n} id={i!r}>" for n, i in found], args.limit)
    _common.report("SoupStrainer parse", secs, peak)
    if not args.no_baseline:
        base, bsecs, bpeak = _common.measure(lambda: ids_full_parse(markup, args.parser))
        _common.report("full parse (baseline)", bsecs, bpeak)
        print("  results identical to full parse:", base == found)


if __name__ == "__main__":
    main()
