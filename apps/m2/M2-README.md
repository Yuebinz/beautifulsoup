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

python apps/m2/task2.py /tmp/large.html     # SoupStrainer: all hyperlinks
python apps/m2/task3.py /tmp/large.html     # SoupStrainer: all text nodes
python apps/m2/task4.py /tmp/large.html     # SoupStrainer: all elements with an id
python apps/m2/task6.py /tmp/large.html     # SoupReplacer: <b> -> <blockquote>
```

Each app also runs the Milestone-1 style "parse everything, then search/rename"
version and prints whether both give identical results, plus timings
(`--memory` adds peak memory, `--no-baseline` skips the comparison,
`--parser lxml` switches parser). The generated file is not committed.

---

## Part 1 - SoupStrainer applications

| App | Strainer | What survives parsing |
|---|---|---|
| `task2.py` | `SoupStrainer("a", href=True)` | only `<a href>` elements |
| `task3.py` | `SoupStrainer(string=True)` | only text nodes (a flat list; every Tag is dropped) |
| `task4.py` | `SoupStrainer(id=True)` | only elements with an `id` (and their descendants) |

Measured on a generated 4 MB file with `html.parser` (the 20 MB file shows the same ratios;
the strainer runs finish in a few seconds, the full parses take minutes):

| App | with SoupStrainer | full parse + search |
|---|---|---|
| task2 | 1.2 s | 16.0 s |
| task3 | 1.8 s | 17.2 s |
| task4 | 15.3 s | 16.0 s |

Notes worth knowing:

* **Task 4 gains little** because a strainer keeps the *entire subtree* of every matching
  element. Here each `<div id=...>` wraps most of the document, so most of it is kept.
* **Task 3 caveat.** In a normal parse, text inside `<script>`/`<style>` and comments become the
  classes `Script`/`Stylesheet`/`Comment`, which `get_text()` skips. A strainer drops the enclosing
  `<script>` tag, so that text comes back as ordinary `NavigableString`s. The app therefore compares
  *all* text nodes (`find_all(string=True)`) instead of `get_text()`.

## Part 2 - Where the API functions are defined in the original source

All line numbers refer to the **original, unmodified** source, i.e. the commit
`repository initialization` (`git show <that commit>:bs4/element.py`, etc.). Lines in the working
tree have shifted since, because of Part 3.

### Functions used by the Milestone-2 programs

| API used | Defined in | Line |
|---|---|---|
| `BeautifulSoup(...)` constructor (`parse_only=`) | `bs4/__init__.py`, `BeautifulSoup.__init__` | 209 (parse_only handled at 323-331 and 437) |
| `SoupStrainer(...)` constructor | `bs4/filter.py`, `SoupStrainer.__init__` | 345 (class starts at 313) |
| `SoupStrainer.excludes_everything` | `bs4/filter.py` | 399 |
| `SoupStrainer.allow_tag_creation` (called while parsing) | `bs4/filter.py` | 580 |
| `SoupStrainer.allow_string_creation` (called while parsing) | `bs4/filter.py` | 621 |
| `Tag.find_all` | `bs4/element.py`, `Tag.find_all` | 2715 |
| `Tag.find` | `bs4/element.py`, `Tag.find` | 2684 |
| `ElementFilter.find_all` / `find` (used by the two above) | `bs4/filter.py` | 137 / 123 |
| `tag["href"]` | `bs4/element.py`, `Tag.__getitem__` | 2203 |
| `tag.name = ...` (plain attribute set in the constructor) | `bs4/element.py`, `Tag.__init__` | 1618 |
| `str(soup)` | `BeautifulSoup.decode` in `bs4/__init__.py` / `Tag.__str__` and `Tag.decode` in `bs4/element.py` | 1073 / 2302 / 2334 |
| `soup.prettify()` | `bs4/element.py`, `Tag.prettify` | 2601 |
| `soup.strings`, `get_text()` | `Tag._all_strings`, `PageElement.get_text` | 1873 / 524 |

### How the parser reaches them (where `parse_only` takes effect)

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

### Tree-editing functions (Milestone-1 tasks 5-7: add / replace nodes)

*Listed so the table covers the add/replace APIs; tick off the ones your Milestone-1 code actually calls.*

| API | Defined in | Line |
|---|---|---|
| `BeautifulSoup.new_tag` | `bs4/__init__.py` | 682 |
| `BeautifulSoup.new_string` | `bs4/__init__.py` | 757 |
| `Tag.append` / `Tag.extend` / `Tag.insert` | `bs4/element.py` | 2046 / 2056 / 1916 |
| `PageElement.insert_before` / `insert_after` | `bs4/element.py` | 689 / 716 |
| `PageElement.replace_with` | `bs4/element.py` | 552 |
| `PageElement.wrap` / `Tag.unwrap` | `bs4/element.py` | 577 / 2022 |
| `PageElement.extract` / `decompose` | `bs4/element.py` | 587 / 635 |
| `Tag.string` (getter / setter) | `bs4/element.py` | 1837 / 1861 |
| `Tag.select` / `select_one` | `bs4/element.py` | 2799 / 2782 |
| `Tag.children` / `Tag.descendants` | `bs4/element.py` | 2752 / 2764 |

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
