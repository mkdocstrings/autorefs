# SPDX-License-Identifier: ISC
#
# ISC License
#
# Copyright (c) 2019, Timothée Mazzucotelli, Oleh Prypin and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Tests for the backlinks module."""

from __future__ import annotations

from itertools import permutations
from textwrap import dedent

from markdown import Markdown

from mkdocs_autorefs import AUTOREF_RE, AutorefsExtension, AutorefsPlugin, Backlink, BacklinkCrumb
from mkdocs_autorefs._internal.references import _html_attrs_parser
from tests.helpers import create_anchor_link, create_page


def test_backlink_crumb_equality_matches_hash_and_order() -> None:
    """Section titles distinguish crumbs, while parent links only provide traversal context."""
    first = BacklinkCrumb("Examples", "")
    second = BacklinkCrumb("Guides", "")
    assert first != second
    assert first < second
    assert first != object()

    other_parent = BacklinkCrumb("Examples", "", parent=BacklinkCrumb("Parent", ""))
    assert first == other_parent
    assert hash(first) == hash(other_parent)
    assert {first, other_parent} == {first}
    assert not first < other_parent
    assert not other_parent < first


def test_backlink_sorting_is_independent_of_input_order() -> None:
    """Mixed navigation depths must not create a cycle in tuple comparisons."""
    examples = Backlink((BacklinkCrumb("Examples", ""), BacklinkCrumb("Mid", "a/#mid")))
    guides = Backlink(
        (BacklinkCrumb("Guides", ""), BacklinkCrumb("Zeta", ""), BacklinkCrumb("Alpha", "b/#alpha")),
    )
    development = Backlink(
        (BacklinkCrumb("Development", ""), BacklinkCrumb("Beta", ""), BacklinkCrumb("Omega", "c/#omega")),
    )
    for backlinks in permutations((examples, guides, development)):
        assert sorted(backlinks, key=lambda backlink: backlink.crumbs) == [development, examples, guides]


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
    page = create_page("foo.html")
    anchor = create_anchor_link("Foo", "foo")
    plugin.register_anchor(page, anchor.id, title=anchor.title, primary=True)
    plugin._register_breadcrumbs(page, anchor)
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
