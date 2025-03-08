"""Tests for the backlinks module."""

from __future__ import annotations

from textwrap import dedent

from markdown import Markdown

from mkdocs_autorefs import AUTOREF_RE, AutorefsExtension, AutorefsPlugin, Backlink, BacklinkCrumb
from mkdocs_autorefs._internal.references import _html_attrs_parser
from tests.helpers import create_anchor_link, create_page


def test_record_backlinks() -> None:
    """Check that only useful backlinks are recorded."""
    plugin = AutorefsPlugin()
    plugin._record_backlink("foo", "referenced-by", "foo", "foo.html")
    assert "foo" not in plugin._backlinks

    plugin.register_anchor(identifier="foo", page=create_page("foo.html"), primary=True)
    plugin._record_backlink("foo", "referenced-by", "foo", "foo.html")
    assert "foo" in plugin._backlinks


def test_get_backlinks() -> None:
    """Check that backlinks can be retrieved."""
    plugin = AutorefsPlugin()
    plugin.record_backlinks = True
    plugin.map_urls(create_page("foo.html"), create_anchor_link("Foo", "foo"))
    plugin._primary_url_map["bar"] = ["bar.html#bar"]
    plugin._record_backlink("bar", "referenced-by", "foo", "foo.html")
    assert plugin.get_backlinks("bar", from_url="") == {
        "referenced-by": {Backlink(crumbs=(BacklinkCrumb(title="Foo", url="foo.html#foo", parent=None),))},
    }


def test_backlinks_treeprocessor() -> None:
    """Check that the backlinks treeprocessor works."""
    plugin = AutorefsPlugin()
    plugin.record_backlinks = True
    plugin.current_page = create_page("foo.html")
    md = Markdown(extensions=["attr_list", "toc", AutorefsExtension(plugin)])
    html = md.convert(
        dedent(
            """
            [](){#alias}
            ## Heading

            [Foo][foo]
            """,
        ),
    )
    match = AUTOREF_RE.search(html)
    assert match
    attrs = _html_attrs_parser.parse(f"<a {match['attrs']}>")
    assert "backlink-type" in attrs
    assert "backlink-anchor" in attrs
