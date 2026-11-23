# Milestone 4: iterable `BeautifulSoup`

## What's here

- New API: `BeautifulSoup.__iter__` in `bs4/__init__.py` (about 20 lines, no other file changed).
- Tests: `bs4/tests/test_soup_iter_m4.py` (5 tests).
- App: `apps/m4/task_iter.py` walks a file with `for node in soup`, counts the node types, and can compare against the old list-building way.
- Build: `./build.sh --no-package` now runs the M4 tests too.

## Run it

```bash
./build.sh --no-package
source .venv/bin/activate
python -m pytest bs4/tests/test_soup_iter_m4.py -v

python apps/m2/make_large_html.py /tmp/large.html --mb 4
python apps/m4/task_iter.py /tmp/large.html --compare --memory
```

```python
soup = BeautifulSoup(html_doc, "html.parser")
for node in soup:
    print(node)
```

## How it works

`soup` is still the object the constructor returns. `BeautifulSoup` is a subclass of `Tag`, and `Tag.__iter__` only walks the direct children, so I overrode `__iter__` on `BeautifulSoup`. It is a generator. It starts at the first node and follows each node's `next_element` link, which the parser already filled in. Each step is constant time and nothing is collected in a list, so memory stays flat however big the document is. The order is document order (parents before children), the same as `.descendants`, and every kind of node comes out: tags, strings, comments, doctype. The root `soup` itself is not yielded.

`Tag.descendants` was already lazy, so I could have written `return iter(self.descendants)`. I didn't, for one reason: `descendants` works out the last node of the tree first and stops there. That is fine for reading, but a loop that deletes nodes can break it. My version takes the previous node before it yields. If the loop body removed the node (`extract()` or `decompose()`), it continues from whatever is now linked after that previous node.

## Things to know

- **A `Tag` is unchanged.** `for child in tag` still gives the direct children only, so existing code that loops over a tag keeps working. Only the soup object goes deep. This is a little inconsistent, but the soup is the whole document and a tag is one element. Nothing inside `bs4` iterated over the soup object directly, and the old test-suite agrees (see below).
- **`list(soup)` and `len(soup)` now differ.** `list(soup)` has every node, while `len(soup)` is still the number of top-level children. Use `soup.contents` for the old behavior of iterating the top level.
- **Edits while looping.** Removing the current node is safe (tested with both `extract` and `decompose`). Adding nodes ahead of the current one means the loop will visit them too, like appending to a Python list while looping.
- **It sees the final tree.** With `SoupStrainer` or `SoupReplacer` the loop shows the filtered or replaced tree, since those run during parsing.

## Tests

1. Every node type, in document order, same objects as `.descendants`, on html.parser, lxml and xml.
2. It is a generator, yields one node at a time, and peak memory stays under 20 KiB for a 60,000 node tree (a list would be about 480 KB).
3. Soup is still a normal `BeautifulSoup`/`Tag`, a `Tag` still gives children only, and two loops over the same soup are independent.
4. Works with `SoupStrainer` and `SoupReplacer` documents.
5. Empty document, plain text, `break` early, and removing the current node (`decompose` and `extract`, including the first node).

On a 4 MB generated file, `task_iter.py` visited 338,824 nodes with about 8 KiB of extra memory, the same count `find_all` gives when it builds its lists.
