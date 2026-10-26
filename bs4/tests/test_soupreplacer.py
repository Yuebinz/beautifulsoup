"""Tests for SoupReplacer (Milestone 2): tag replacement during parsing."""
import unittest

from bs4 import BeautifulSoup, SoupReplacer, SoupStrainer

DOC = (
    "<html><body><p>one <b>bold</b> and <b>more <i>bold</i></b></p>"
    "<div><b class='x'>third</b></div></body></html>"
)


def rename_after_parsing(markup, og, alt, parser):
    """The Milestone-1 way: parse first, then walk the tree and rename."""
    soup = BeautifulSoup(markup, parser)
    for tag in soup.find_all(og):
        tag.name = alt
    return soup


class TestSoupReplacerUnit(unittest.TestCase):
    def test_replace_maps_only_the_original_name(self):
        r = SoupReplacer("b", "blockquote")
        assert r.replace("b") == "blockquote"
        assert r.replace("i") == "i"
        assert r.replace("blockquote") == "blockquote"

    def test_constructor_rejects_bad_arguments(self):
        for bad in [("", "x"), ("x", ""), (None, "x"), ("x", 3)]:
            with self.assertRaises(ValueError):
                SoupReplacer(*bad)

    def test_repr(self):
        assert repr(SoupReplacer("b", "em")) == "SoupReplacer('b', 'em')"


class TestSoupReplacerParsing(unittest.TestCase):
    # Test case 1: the example from the assignment, on each supported parser.
    def test_b_to_blockquote_during_parsing(self):
        for parser in ("html.parser", "lxml"):
            replacer = SoupReplacer("b", "blockquote")
            soup = BeautifulSoup(DOC, parser, replacer=replacer)
            assert soup.find("b") is None
            assert len(soup.find_all("blockquote")) == 3
            assert soup.find("blockquote", class_="x").string == "third"
            # Identical to renaming afterwards, but done in one pass.
            expected = rename_after_parsing(DOC, "b", "blockquote", parser)
            assert soup.prettify() == expected.prettify()

    # Test case 2: the replacement name's own properties apply, and a
    # strainer combined with a replacer works on the *original* names.
    def test_replacement_gets_properties_of_new_name(self):
        # <br> is a void element; <span> is not. Renaming at parse time
        # means the Tag is created as a normal <span> element.
        soup = BeautifulSoup(
            "<p>a<br>b</p>", "html.parser", replacer=SoupReplacer("br", "span")
        )
        assert soup.find("br") is None
        assert soup.span is not None
        assert soup.span.can_be_empty_element is False
        assert str(soup.p) == "<p>a<span></span>b</p>"
        # Renaming afterwards keeps the old name's "void element" flag.
        late = rename_after_parsing("<p>a<br>b</p>", "br", "span", "html.parser")
        assert str(late.p) == "<p>a<span/>b</p>"

    def test_replacer_with_parse_only(self):
        replacer = SoupReplacer("b", "strong")
        only_b = SoupStrainer("b")
        soup = BeautifulSoup(DOC, "html.parser", parse_only=only_b, replacer=replacer)
        names = [t.name for t in soup.find_all(True)]
        assert "b" not in names and "p" not in names
        assert names.count("strong") == 3

    def test_no_replacer_is_unchanged(self):
        assert str(BeautifulSoup(DOC, "html.parser")) == str(
            BeautifulSoup(DOC, "html.parser", replacer=None)
        )
