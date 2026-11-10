"""Tests for the Milestone-3 SoupReplacer API:
SoupReplacer(name_xformer=..., attrs_xformer=..., xformer=...)."""
import unittest

from bs4 import BeautifulSoup, SoupReplacer, SoupStrainer

DOC = (
    "<html><body><p class='intro text' id='p1'>one <b>bold</b> and "
    "<b class='x'>more <i>bold</i></b></p>"
    "<div class='box'><a href='/a' rel='nofollow me'>link</a><br></div></body></html>"
)
PARSERS = ("html.parser", "lxml")


def b_to_blockquote_name(tag):
    return "blockquote" if tag.name == "b" else tag.name


def remove_class_attr(tag):
    if "class" in tag.attrs:
        del tag.attrs["class"]


class TestSoupReplacerTransformers(unittest.TestCase):
    # Test case 1: name_xformer - the example from the assignment, equal to
    # the Milestone-1 way (parse, then rename) on each supported parser.
    def test_name_xformer_b_to_blockquote(self):
        for parser in PARSERS:
            soup = BeautifulSoup(
                DOC, parser, replacer=SoupReplacer(name_xformer=b_to_blockquote_name)
            )
            assert soup.find("b") is None
            assert len(soup.find_all("blockquote")) == 2
            expected = BeautifulSoup(DOC, parser)
            for b in expected.find_all("b"):
                b.name = "blockquote"
            assert soup.prettify() == expected.prettify()

    # Test case 2: attrs_xformer returns the new attributes. Multi-valued
    # attributes (class) come back as lists, as in a normal parse.
    def test_attrs_xformer_replaces_attributes(self):
        def attrs(tag):
            new = dict(tag.attrs)
            if tag.name == "p":
                new["class"] = "changed twice"
                new["data-tag"] = "p"
            return new

        for parser in PARSERS:
            soup = BeautifulSoup(DOC, parser, replacer=SoupReplacer(attrs_xformer=attrs))
            p = soup.p
            assert p["class"] == ["changed", "twice"]
            assert p["data-tag"] == "p"
            assert p["id"] == "p1"
            assert soup.div["class"] == ["box"]  # untouched tags are unchanged
            assert soup.a["rel"] == ["nofollow", "me"]

    # Test case 3: xformer has side effects on the tag - the class_deleter
    # example from the assignment, plus adding an attribute.
    def test_xformer_side_effects(self):
        def xf(tag):
            remove_class_attr(tag)
            if tag.name == "a":
                tag["target"] = "_blank"

        for parser in PARSERS:
            soup = BeautifulSoup(DOC, parser, replacer=SoupReplacer(xformer=xf))
            assert not [t for t in soup.find_all(True) if "class" in t.attrs]
            assert soup.p["id"] == "p1"  # other attributes survive
            assert soup.a["target"] == "_blank"
            assert soup.a["href"] == "/a"

    # Test case 4: end tags are matched by the name the *document* used, even
    # when several different source names map to one new name, and when the
    # markup is badly nested.
    def test_end_tags_match_with_many_to_one_rename_and_bad_nesting(self):
        markup = "<p>1<b>2<i>3</b>4</i>5</p><div><b>6</b></div>"
        to_em = lambda tag: "em" if tag.name in ("b", "i") else tag.name
        soup = BeautifulSoup(
            markup, "html.parser", replacer=SoupReplacer(name_xformer=to_em)
        )
        expected = BeautifulSoup(markup, "html.parser")
        for t in expected.find_all(["b", "i"]):
            t.name = "em"
        assert str(soup) == str(expected)
        assert soup.find("b") is None and soup.find("i") is None
        assert soup.div.em.string == "6"

    # Test case 5: properties that depend on the tag name are computed for
    # the new name (void elements, multi-valued attributes, whitespace).
    def test_new_name_gets_properties_of_new_name(self):
        for parser in PARSERS:
            # <br> -> <span>: no longer a void element.
            soup = BeautifulSoup(
                "<p>a<br>b</p>",
                parser,
                replacer=SoupReplacer(
                    name_xformer=lambda t: "span" if t.name == "br" else t.name
                ),
            )
            assert str(soup.p) == "<p>a<span></span>b</p>"
            # <b> -> <a>: `rel` is a multi-valued attribute on <a> only.
            soup = BeautifulSoup(
                "<b rel='x y'>t</b>",
                parser,
                replacer=SoupReplacer(
                    name_xformer=lambda t: "a" if t.name == "b" else t.name
                ),
            )
            assert soup.a["rel"] == ["x", "y"]
        # <div> -> <pre>: whitespace is preserved inside the new <pre>.
        soup = BeautifulSoup(
            "<div>a\n  b</div>",
            "html.parser",
            replacer=SoupReplacer(
                name_xformer=lambda t: "pre" if t.name == "div" else t.name
            ),
        )
        assert soup.pre.prettify() == "<pre>a\n  b</pre>\n"

    # Test case 6: the callables see start tags in document order (with their
    # parent already in the tree), all three can be combined, they cooperate
    # with parse_only, and the constructor rejects bad arguments.
    def test_combination_order_parse_only_and_validation(self):
        seen = []

        def name(tag):
            seen.append((tag.name, tag.parent.name))
            return tag.name.upper() if tag.name == "b" else tag.name

        def attrs(tag):
            return {"was": tag.name}  # called with the tag as parsed

        def xf(tag):
            tag["now"] = tag.name  # sees the result of name/attrs xformers

        r = SoupReplacer(name_xformer=name, attrs_xformer=attrs, xformer=xf)
        soup = BeautifulSoup("<p><b>x</b></p>", "html.parser", replacer=r)
        assert seen == [("p", "[document]"), ("b", "p")]
        assert str(soup) == '<p now="p" was="p"><B now="B" was="b">x</B></p>'

        # parse_only sees the source names; the transformers see what is kept.
        soup = BeautifulSoup(
            DOC,
            "html.parser",
            parse_only=SoupStrainer("b"),
            replacer=SoupReplacer(name_xformer=b_to_blockquote_name),
        )
        assert [t.name for t in soup.find_all(True)] == ["blockquote", "blockquote", "i"]

        # An (og, alt) pair and transformers can be combined.
        soup = BeautifulSoup(
            "<b>x</b>",
            "html.parser",
            replacer=SoupReplacer("b", "strong", xformer=lambda t: t.attrs.update(k="v")),
        )
        assert str(soup) == '<strong k="v">x</strong>'

        with self.assertRaises(ValueError):
            SoupReplacer()
        with self.assertRaises(TypeError):
            SoupReplacer(xformer="not callable")
        with self.assertRaises(ValueError):
            BeautifulSoup(
                "<b>x</b>", "html.parser", replacer=SoupReplacer(name_xformer=lambda t: "")
            )


if __name__ == "__main__":
    unittest.main()
