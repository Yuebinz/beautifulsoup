"""Task 2 (SoupStrainer version): list every hyperlink in a large file.

The parse tree only ever contains <a href=...> elements, because everything
else is discarded by a SoupStrainer while the document is being parsed.

Usage: python apps/m2/task2.py FILE [--parser html.parser] [--limit 10] [--no-baseline] [--memory]
"""
import argparse

import _common
from bs4 import BeautifulSoup, SoupStrainer


def links_with_strainer(markup, parser):
    only_links = SoupStrainer("a", href=True)
    soup = BeautifulSoup(markup, parser, parse_only=only_links)
    return [a["href"] for a in soup.find_all("a")]


def links_full_parse(markup, parser):  # Milestone-1 style, used for comparison
    soup = BeautifulSoup(markup, parser)
    return [a["href"] for a in soup.find_all("a", href=True)]


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
    links, secs, peak = _common.measure(lambda: links_with_strainer(markup, args.parser))
    print(f"Task 2: {len(links)} hyperlinks found")
    _common.preview(links, args.limit)
    _common.report("SoupStrainer parse", secs, peak)
    if not args.no_baseline:
        base, bsecs, bpeak = _common.measure(lambda: links_full_parse(markup, args.parser))
        _common.report("full parse (baseline)", bsecs, bpeak)
        print("  results identical to full parse:", base == links)


if __name__ == "__main__":
    main()
