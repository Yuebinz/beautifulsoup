# Milestone-2

Everything for this milestone lives in three places:

| What | Where |
|---|---|
| New API (`SoupReplacer`, `replacer=` argument) | `bs4/filter.py`, `bs4/__init__.py` (+ two small supporting edits, see Part 3) |
| New tests | `bs4/tests/test_soupreplacer.py` |
| Application programs | `apps/m2/` (`task2.py`, `task3.py`, `task4.py`, `task6.py`, `make_large_html.py`) |
| Build script | `build.sh` (repository root) |

## How to build, test and run

```bash
./build.sh                  # venv + dependencies + editable install + pytest + sdist/wheel
./build.sh --no-package     # same, without building dist/
source .venv/bin/activate

# a large test file (about 20 MB; use --mb 4 for a quick run)
python apps/m2/make_large_html.py /tmp/large.html --mb 20

python apps/m2/task2.py /tmp/large.html --compare   # SoupStrainer: all <a> tags
python apps/m2/task3.py /tmp/large.html --compare   # SoupStrainer: all tag names
python apps/m2/task4.py /tmp/large.html --compare   # SoupStrainer: tags with an id
python apps/m2/task6.py /tmp/large.html out.html --compare   # SoupReplacer: <b> -> <blockquote>
```

Each app prints its results and its parse time; `--compare` also runs the Milestone-1 style
"parse everything, then search/rename" version and says whether the results are identical
(`--memory` adds peak memory, but slows parsing a lot). The generated file is not committed.

---

## Part 1 - SoupStrainer applications

These are the Milestone-1 tasks 2, 3 and 4, re-done with a `SoupStrainer`. They take the
input file as the first argument and print the same kind of output as the Milestone-1 scripts
(`.xml` files use the `xml` parser, with the same fallback to `html.parser` if lxml is missing).
`--compare` also runs the Milestone-1 way (parse everything, then `find_all`) and checks that the
results are identical.

| App | Milestone-1 task | Strainer | What survives parsing |
|---|---|---|---|
| `task2.py` | print every `<a>` | `SoupStrainer("a")` | only `<a>` elements |
| `task3.py` | print every tag name | `SoupStrainer(name=True)` | every tag (nothing can be skipped) |
| `task4.py` | print tags with an `id` | `SoupStrainer(id=True)` | only elements with an `id` (and their descendants) |

Measured on a generated 4 MB file with `html.parser` (`make_large_html.py`):

| App | with SoupStrainer | full parse + search |
|---|---|---|
| task2 | about 1.2 s | about 16 s |
| task3 | 13.3 s | 16.3 s |
| task4 | about 15 s | about 16 s |

Notes worth knowing:

* **Task 3 is the one a strainer cannot really speed up.** The task needs every tag, so the
  strainer must accept the root element and with it the whole document. The result is identical to a
  normal parse and the time is nearly the same. A strainer pays off when it can throw most of the
  document away (task2).
* **Task 4 gains little** because a strainer keeps the *entire subtree* of every matching
  element. Here each `<div id=...>` wraps most of the document, so most of it is kept.

## Part 2 - Where the API functions are defined in the original source

All line numbers refer to the **original, unmodified** source, i.e. the first commit
`repository initialization` (`git show <that commit>:bs4/element.py`, etc.). Lines in the working
tree have shifted since, because of Part 3.

### Functions used in Milestone 1 (tasks 1-8)

| API (where used) | Defined in | Line |
|---|---|---|
| `BeautifulSoup(markup, parser)` (all tasks) | `bs4/__init__.py`, `BeautifulSoup.__init__` | 209 |
| `FeatureNotFound` (raised by the constructor; caught in `load_soup`) | `bs4/exceptions.py`, class; raised in `bs4/__init__.py` | 10; 364 |
| `soup.prettify()` (task 1) | `bs4/element.py`, `Tag.prettify` | 2601 |
| `str(soup)` (tasks 6, 7) | `BeautifulSoup.decode` in `bs4/__init__.py`; `Tag.__str__` and `Tag.decode` in `bs4/element.py` | 1073; 2302, 2334 |
| `soup.find_all("a")`, `find_all(True)`, `find_all(id=True)`, `find_all("b")`, `find_all("p")` (tasks 2-7) | `bs4/element.py`, `Tag.find_all` (which calls `PageElement._find_all`) | 2715 (`_find_all` at 1079) |
| `tag["id"]` (task 4) | `bs4/element.py`, `Tag.__getitem__` | 2203 |
| `tag.get("id")` (task 5) | `bs4/element.py`, `Tag.get` | 2160 |
| `tag.name` (tasks 3, 4, 5, 8) and `b.name = "blockquote"` (task 6): a plain attribute | set in `Tag.__init__` (`self.name = name`) | 1618 (assignment at 1648) |
| `p["class"] = "test"` (task 7) | `bs4/element.py`, `Tag.__setitem__` | 2223 |
| `a.find_parent([...])` (task 5) | `bs4/element.py`, `PageElement.find_parent` (calls `find_parents`) | 992 (`find_parents` at 1022) |
| `a.get_text(strip=True)` (tasks 5, 8) | `bs4/element.py`, `PageElement.get_text` (uses `_all_strings`) | 524 (`_all_strings` at 504, `Tag._all_strings` at 1873) |
| `soup.title` (task 8) | `bs4/element.py`, `Tag.__getattr__` (looks up the first `<title>` tag) | 2249 |
| `soup.select("h1, h2, h3")` (task 8) | `bs4/element.py`, `Tag.select` | 2799 |
| `h.find_next_sibling()` (task 8) | `bs4/element.py`, `PageElement.find_next_sibling` | 803 |

### Functions used in Milestone 2, Part 1 and Part 3

| API | Defined in | Line |
|---|---|---|
| `BeautifulSoup(..., parse_only=...)` | `bs4/__init__.py`, `BeautifulSoup.__init__` (parse_only handled at 323-331 and 437) | 209 |
| `SoupStrainer(...)` constructor | `bs4/filter.py`, `SoupStrainer.__init__` (class starts at 313) | 345 |
| `SoupStrainer.excludes_everything` | `bs4/filter.py` | 399 |
| `SoupStrainer.allow_tag_creation` (called by the parser for each start tag) | `bs4/filter.py` | 580 |
| `SoupStrainer.allow_string_creation` (called by the parser for each text) | `bs4/filter.py` | 621 |
| `ElementFilter.find_all` / `find` | `bs4/filter.py` | 137 / 123 |
| `Tag.find` | `bs4/element.py` | 2684 |

### How the parser reaches them (where `parse_only` takes effect, and where SoupReplacer hooks in)

| Step | Defined in | Line |
|---|---|---|
| `BeautifulSoup._feed` (runs the tree builder over the markup) | `bs4/__init__.py` | 650 |
| `HTMLParserTreeBuilder.feed` | `bs4/builder/_htmlparser.py` | 449 |
| `BeautifulSoupHTMLParser.handle_starttag` / `handle_endtag` / `handle_data` | `bs4/builder/_htmlparser.py` | 142 / 204 / 222 |
| `BeautifulSoup.handle_starttag` (strainer check at 1021-1026) | `bs4/__init__.py` | 987 |
| `BeautifulSoup.handle_endtag` | `bs4/__init__.py` | 1053 |
| `BeautifulSoup.endData` (strainer check at 856-861) | `bs4/__init__.py` | 826 |
| `BeautifulSoup._popToTag` | `bs4/__init__.py` | 950 |
| `BeautifulSoup.pushTag` / `popTag` | `bs4/__init__.py` | 809 / 786 |

## Part 3 - SoupReplacer

```python
from bs4 import BeautifulSoup, SoupReplacer

b_to_blockquote = SoupReplacer("b", "blockquote")
print(BeautifulSoup(html_doc, replacer=b_to_blockquote).prettify())
```

### Changes to the library

| File | Change |
|---|---|
| `bs4/filter.py` | new class `SoupReplacer(og_tag, alt_tag)` with `replace(name)`; validates its arguments |
| `bs4/__init__.py` | import/export `SoupReplacer`; new `replacer=` constructor argument stored as `self.replacer`; `handle_starttag` renames the tag *before* the `Tag` object is created; `handle_endtag` maps the end-tag name the same way so it still matches the open tag |
| `bs4/builder/_htmlparser.py` | the "is this a void element, so close it now?" check uses the *source* tag name (`builder.can_be_empty_element(name)`) instead of `tag.is_empty_element`. Without a replacer the two are equivalent; with one, `<br>` -> `<span>` would otherwise leave the `<span>` open |
| `bs4/builder/_html5lib.py` | warns that `replacer` is ignored (html5lib builds its own tree, like it already does for `parse_only`) |

Works with `html.parser`, `lxml` and `lxml-xml`. If a `SoupStrainer` is also given, it sees the
original tag names (the strainer runs first, then the rename).

### Why doing it inside the library is better than outside

1. **No second traversal.** The after-the-fact version is `find_all(og)` over the whole tree plus a loop
   that renames; the in-parser version is one string comparison per start/end tag, on tags the
   parser is visiting anyway.
2. **The `Tag` is built with its final name,** so everything derived from the name is right.
   Example (see the test): renaming `<br>` to `<span>` afterwards leaves the tag marked as a
   void element and prints `<span/>`; replacing during parsing prints `<span></span>`.

Measured (`apps/m2/task6.py`, 4 MB file, `html.parser`): about 15.2 s during parsing vs 17.8 s for
parse-then-rename, with byte-identical output. Parsing dominates, so the saving is the avoided
traversal (roughly 15%).

### Tests (`bs4/tests/test_soupreplacer.py`)

* `test_b_to_blockquote_during_parsing` - the assignment's example, on `html.parser` and `lxml`;
  output equals rename-after-parsing.
* `test_replacement_gets_properties_of_new_name` - `<br>` -> `<span>` behaves like a normal element.
* Also: `replace()` unit test, constructor validation, `repr`, combination with `parse_only`,
  and "no replacer = unchanged behaviour".

```bash
python -m pytest bs4/tests/test_soupreplacer.py
```
