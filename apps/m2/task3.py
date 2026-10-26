"""Task 3 (SoupStrainer version): collect every text node of a large file.

SoupStrainer(string=True) accepts text nodes and (since no tag restriction
is given) lets the parser throw every Tag away, so the "tree" is just a flat
list of strings.

Caveat worth knowing: with a normal parse, text inside <script>/<style> and
comments become the special classes Script / Stylesheet / Comment. A strainer
discards the enclosing <script>/<style> tag, so those strings come back as
plain NavigableStrings. That is why both versions here compare *all* text
nodes (``string=True``) rather than ``get_text()``, which skips those classes.

Usage: python apps/m2/task3.py FILE [--parser html.parser] [--limit 10] [--no-baseline] [--memory]
"""
import argparse

import _common
from bs4 import BeautifulSoup, SoupStrainer


def text_with_strainer(markup, parser):
    only_text = SoupStrainer(string=True)
    soup = BeautifulSoup(markup, parser, parse_only=only_text)
    return [str(s) for s in soup.find_all(string=True)]


def text_full_parse(markup, parser):  # Milestone-1 style, used for comparison
    soup = BeautifulSoup(markup, parser)
    return [str(s) for s in soup.find_all(string=True)]


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
    texts, secs, peak = _common.measure(lambda: text_with_strainer(markup, args.parser))
    print(f"Task 3: {len(texts)} text nodes found")
    _common.preview([t.strip()[:70] for t in texts if t.strip()], args.limit)
    _common.report("SoupStrainer parse", secs, peak)
    if not args.no_baseline:
        base, bsecs, bpeak = _common.measure(lambda: text_full_parse(markup, args.parser))
        _common.report("full parse (baseline)", bsecs, bpeak)
        print("  results identical to full parse:", base == texts)


if __name__ == "__main__":
    main()
