"""Task 6 (SoupReplacer version): replace every <b> tag by <blockquote>.

The replacement happens *during parsing* via SoupReplacer, so there is no
second walk over the finished parse tree. The Milestone-1 way (parse, then
find_all + rename) is run alongside for comparison.

Usage: python apps/m2/task6.py FILE [--og b] [--alt blockquote] [--parser html.parser]
                                    [--output out.html] [--no-baseline] [--memory]
"""
import argparse

import _common
from bs4 import BeautifulSoup, SoupReplacer


def replace_during_parsing(markup, parser, og, alt):
    return BeautifulSoup(markup, parser, replacer=SoupReplacer(og, alt))


def replace_after_parsing(markup, parser, og, alt):  # Milestone-1 style
    soup = BeautifulSoup(markup, parser)
    for tag in soup.find_all(og):
        tag.name = alt
    return soup


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--og", default="b")
    ap.add_argument("--alt", default="blockquote")
    ap.add_argument("--parser", default=_common.DEFAULT_PARSER)
    ap.add_argument("--output", help="write the resulting document here")
    ap.add_argument("--no-baseline", action="store_true")
    ap.add_argument("--memory", action="store_true", help="also report peak memory (slow)")
    args = ap.parse_args()
    _common.TRACK_MEMORY = args.memory

    markup = _common.read_markup(args.file)
    soup, secs, peak = _common.measure(
        lambda: replace_during_parsing(markup, args.parser, args.og, args.alt)
    )
    print(
        f"Task 6: <{args.og}> -> <{args.alt}>: "
        f"{len(soup.find_all(args.alt))} <{args.alt}> and "
        f"{len(soup.find_all(args.og))} <{args.og}> left in the tree"
    )
    _common.report("SoupReplacer (in parse)", secs, peak)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(str(soup))
        print("  wrote", args.output)
    if not args.no_baseline:
        base, bsecs, bpeak = _common.measure(
            lambda: replace_after_parsing(markup, args.parser, args.og, args.alt)
        )
        _common.report("parse then rename (M1)", bsecs, bpeak)
        print("  output identical to rename-after-parse:", str(base) == str(soup))


if __name__ == "__main__":
    main()
