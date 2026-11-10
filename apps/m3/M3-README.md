# Milestone 3

## What's here

- New API: `SoupReplacer(name_xformer=, attrs_xformer=, xformer=)` in `bs4/filter.py`, hooked into the parser in `bs4/__init__.py` (plus one small attribute in `bs4/element.py`).
- Tests: `bs4/tests/test_soupreplacer_m3.py` (6 tests).
- App: `apps/m3/task7.py`, which does Milestone-1 task 7 (add `class="test"` to every `<p>`) using `xformer`.
- Build: `./build.sh --no-package` now runs the M3 tests too.

## Run it

```bash
./build.sh --no-package
source .venv/bin/activate
python -m pytest bs4/tests/test_soupreplacer_m3.py -v

python apps/m2/make_large_html.py /tmp/large.html --mb 4
python apps/m3/task7.py /tmp/large.html out.html --compare
```

`--compare` also does it the Milestone-1 way (parse, then loop over `find_all("p")`) and checks the output is the same.

## How it works

Each transformer takes a tag. `name_xformer` returns the new name, `attrs_xformer` returns the new attributes, and `xformer` edits the tag and returns nothing. They run in `handle_starttag`, right after the `Tag` is created and before it goes into the tree. The old `SoupReplacer("b", "blockquote")` still works.

Two things changed compared to M2:

1. **The tag has to exist first.** In M2 the name was swapped before the `Tag` was built. A function that gets a tag needs the real object, so I build it, run the functions, and if the name changed, redo what depends on the name (void element or not, multi-valued attributes like `rel`, `<meta>` charset).
2. **End tags.** M2 turned `</b>` into `</blockquote>` with the same mapping. A function can't run on an end tag, so each open tag remembers the name the document used (`_source_name`) and `</b>` closes the most recent open tag with that source name.

Limits: a transformer only sees a start tag, so no children yet. If `xformer` sets `tag.name` directly, the name-based properties are not redone; use `name_xformer` for renames. html5lib ignores `replacer`.

## Tests

1. `name_xformer` b to blockquote, on html.parser and lxml, same result as renaming after parsing.
2. `attrs_xformer` replaces attributes; `class` still comes back as a list.
3. `xformer` side effects (delete `class`, add `target`).
4. End tags with many-to-one renames and bad nesting.
5. New name gets the new name's behavior (`br` to `span` is not void, `b` to `a` makes `rel` a list, `div` to `pre` keeps whitespace).
6. Call order, all three together, `parse_only`, and bad arguments.

## Technical brief: M2 vs M3

**M2** (`SoupReplacer("b", "blockquote")`) is small and safe. It's one string compare per tag, and since the name is swapped before the `Tag` exists, nothing derived from the name can be wrong. But it can only rename one tag to one other tag. Anything else (rename `b` and `i`, drop `class`, add `rel` to links) still needs a second pass over the tree, which is what we wanted to avoid.

**M3** handles those cases in one pass, and it covers M2 as a special case. The cost is more complexity: we have to fix up name-dependent state after the tag is created, and end tags need the source-name tracking. `xformer` is the risky one because it can do anything to the tag.

On speed, don't expect much. OOn a 4 MB generated file, `task7.py --compare` took about 5.6 s with the xformer vs 6.5 s for parse-then-modify (about 14% faster; it varies between runs). Parsing is the expensive part; the saved `find_all` loop is small. The transformer is also called for every start tag, changed or not. If someone wants a big speedup, `SoupStrainer` is the better tool because it avoids building most of the tree.

**Recommendation:** go with the M3 API, and keep the M2 pair as the simple form on top of the same code path. Document `name_xformer` and `attrs_xformer` as the normal way to use it, since they return values and the library controls how they're applied. Keep `xformer` as the escape hatch with a note not to rename tags in it. Be clear that this is a convenience, not a performance feature.
