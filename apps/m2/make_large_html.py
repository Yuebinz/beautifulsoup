"""Generate a large, deterministic HTML file for testing the Milestone-2 apps.

Usage: python apps/m2/make_large_html.py OUT.html [--mb 20]

The file mixes links, ids, <b>/<i> text, scripts, styles, comments, tables and
void elements, so every app has something to find and plenty to throw away.
"""
import argparse
import random


def block(i, rnd):
    words = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta"]
    text = " ".join(rnd.choice(words) for _ in range(12))
    return (
        f'<div class="section" id="sec{i}">\n'
        f"  <h2>Section {i}</h2>\n"
        f"  <p>{text} <b>bold {i}</b> and <i>italic {i}</i>"
        f' <a href="http://example.com/page/{i}" class="link">link {i}</a>.<br>'
        f' More <b>bold <i>nested {i}</i></b> text.</p>\n'
        f"  <!-- comment {i} -->\n"
        f'  <table><tr><td id="cell{i}">{i}</td><td>{text[:20]}</td></tr></table>\n'
        f"  <script>var x{i} = {i};</script>\n"
        f"  <style>.s{i} {{ color: red; }}</style>\n"
        f'  <img src="img{i}.png" alt="img {i}">\n'
        f"</div>\n"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--mb", type=float, default=20)
    args = ap.parse_args()
    rnd = random.Random(2026)
    target = int(args.mb * 1024 * 1024)
    written = 0
    with open(args.out, "w", encoding="utf-8") as f:
        head = "<!DOCTYPE html>\n<html><head><title>Large test file</title></head>\n<body>\n"
        f.write(head)
        written += len(head)
        i = 0
        while written < target:
            chunk = block(i, rnd)
            f.write(chunk)
            written += len(chunk)
            i += 1
        f.write("</body></html>\n")
    print(f"wrote {args.out}: {i} sections, ~{written / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
