"""Tests for Milestone 4: a BeautifulSoup object is iterable over every node
of the tree, one node at a time (it never collects the nodes into a list)."""
import inspect
import tracemalloc
import unittest

from bs4 import BeautifulSoup, SoupReplacer, SoupStrainer
from bs4.element import Comment, Doctype, NavigableString, Tag

DOC = (
    "<!DOCTYPE html><html><head><title>T</title></head><body>"
    "<p class='a'>one <b>bold</b><!-- note --> two</p>"
    "<div><ul><li>x</li><li>y<i>z</i></li></ul><br></div>tail</body></html>"
)


class TestSoupIteration(unittest.TestCase):
    # Test 1: all node types, document order, root excluded - and the same
    # nodes (identical objects) as .descendants, on each parser.
    def test_visits_every_node_in_document_order(self):
        for parser in ("html.parser", "lxml", "xml"):
            soup = BeautifulSoup(DOC, parser)
            nodes = [n for n in soup]
            expected = list(soup.descendants)
            self.assertTrue(nodes)
            self.assertEqual(len(nodes), len(expected))
            self.assertTrue(all(a is b for a, b in zip(nodes, expected)), parser)
            self.assertNotIn(soup, nodes)
        soup = BeautifulSoup(DOC, "html.parser")
        kinds = {type(n) for n in soup}
        self.assertTrue({Tag, NavigableString, Comment, Doctype} <= kinds)
        names = [n.name for n in soup if isinstance(n, Tag)]
        self.assertEqual(
            names, ["html", "head", "title", "body", "p", "b", "div", "ul", "li", "li", "i", "br"]
        )

    # Test 2: it is lazy. iter(soup) is a generator, the nodes are produced
    # one at a time, and iterating a big tree does not allocate memory in
    # proportion to its size (a list of N nodes would).
    def test_is_lazy_generator_with_flat_memory(self):
        soup = BeautifulSoup("<p>a</p><p>b</p>", "html.parser")
        it = iter(soup)
        self.assertTrue(inspect.isgenerator(it))
        self.assertEqual(next(it).name, "p")
        self.assertEqual(next(it), "a")

        big = BeautifulSoup("<ul>" + "<li>item</li>" * 30000 + "</ul>", "html.parser")
        tracemalloc.start()
        count = 0
        for _ in big:
            count += 1
        peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        self.assertEqual(count, 1 + 2 * 30000)
        self.assertLess(peak, 20 * 1024)  # 60k-element list would be ~480 KB

    # Test 3: soup is still the normal soup object, a Tag still iterates only
    # its direct children, and each `for` starts a fresh, independent walk.
    def test_soup_still_normal_and_tag_unchanged(self):
        soup = BeautifulSoup(DOC, "html.parser")
        self.assertIsInstance(soup, BeautifulSoup)
        self.assertIsInstance(soup, Tag)
        self.assertEqual(soup.find("b").string, "bold")
        self.assertEqual(len(soup.contents), 2)  # doctype + html: unchanged
        div = soup.find("div")
        self.assertEqual([c.name for c in div], ["ul", "br"])  # children only
        self.assertEqual(list(soup), list(soup))  # repeatable
        outer = iter(soup)
        next(outer)
        self.assertEqual(sum(1 for _ in soup), len(list(soup.descendants)))
        self.assertIsNotNone(next(outer))  # the first walk was not disturbed

    # Test 4: documents built with SoupStrainer or SoupReplacer iterate too,
    # and the iteration sees the replaced / filtered tree.
    def test_with_parse_only_and_replacer(self):
        strained = BeautifulSoup(DOC, "html.parser", parse_only=SoupStrainer("li"))
        self.assertEqual([n.name for n in strained if isinstance(n, Tag)], ["li", "li", "i"])
        replaced = BeautifulSoup(
            DOC, "html.parser", replacer=SoupReplacer("b", "blockquote")
        )
        tags = [n.name for n in replaced if isinstance(n, Tag)]
        self.assertIn("blockquote", tags)
        self.assertNotIn("b", tags)

    # Test 5: edge cases - empty document, break early, and removing the node
    # just yielded while iterating.
    def test_empty_early_exit_and_mutation(self):
        self.assertEqual(list(BeautifulSoup("", "html.parser")), [])
        self.assertEqual(list(BeautifulSoup("just text", "html.parser")), ["just text"])

        soup = BeautifulSoup(DOC, "html.parser")
        for node in soup:
            if isinstance(node, Tag) and node.name == "head":
                break
        self.assertEqual(node.name, "head")

        soup = BeautifulSoup("<div><i>1</i><b>2</b><i>3</i></div>", "html.parser")
        for node in soup:
            if isinstance(node, Tag) and node.name == "i":
                node.decompose()
        self.assertEqual(str(soup), "<div><b>2</b></div>")

        soup = BeautifulSoup("<i>0</i><p>a<i>1</i></p><i>2</i>", "html.parser")
        seen = []
        for node in soup:
            if isinstance(node, Tag):
                seen.append(node.name)
                if node.name == "i":
                    node.extract()  # also the first node: nothing before it
        self.assertEqual(seen, ["i", "p", "i", "i"])
        self.assertEqual(str(soup), "<p>a</p>")


if __name__ == "__main__":
    unittest.main()
