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

import pytest
from markdown import Markdown
from mkdocs.structure.nav import Section
from mkdocs.structure.toc import TableOfContents

from mkdocs_autorefs import AUTOREF_RE, AutorefsExtension, AutorefsPlugin, Backlink, BacklinkCrumb
from mkdocs_autorefs._internal.references import _html_attrs_parser
from tests.helpers import create_anchor_link, create_page


def test_backlink_crumb_equality_and_hashing() -> None:
    """Check that matching titles and URLs identify the same crumb."""
    crumb = BacklinkCrumb("API", "api/")
    duplicate = BacklinkCrumb("API", "api/")

    assert crumb == duplicate
    assert hash(crumb) == hash(duplicate)
    assert len({crumb, duplicate}) == 1


def test_backlink_crumb_dictionary_keys() -> None:
    """Check that both the title and URL distinguish dictionary keys."""
    # Navigation sections have empty URLs but must remain separate tree branches.
    development = BacklinkCrumb("Development", "")
    examples = BacklinkCrumb("Examples", "")
    examples_page = BacklinkCrumb("Examples", "examples/")
    branches = {development: "development", examples: "examples", examples_page: "page"}

    assert development != examples
    assert examples != examples_page
    assert len(branches) == 3
    assert branches[BacklinkCrumb("Development", "")] == "development"
    assert branches[BacklinkCrumb("Examples", "")] == "examples"
    assert sorted(branches) == [development, examples, examples_page]


def test_backlink_crumb_comparisons_ignore_parent() -> None:
    """Check that parent metadata does not affect equality, hashing, or ordering."""
    parents = (None, BacklinkCrumb("Development", ""), BacklinkCrumb("Examples", ""))
    crumbs = [BacklinkCrumb("API", "api/", parent=parent) for parent in parents]

    # Comparing a root crumb with a nested crumb must not try to order their parents.
    for left, right in permutations(crumbs, 2):
        assert left == right
        assert hash(left) == hash(right)
        assert left <= right
        assert left >= right
        assert not left < right
        assert not left > right

    assert len(set(crumbs)) == 1


def test_backlinks_sort_consistently() -> None:
    """Check that different input orders produce the same backlink order."""
    # Unequal navigation depths exposed a comparison cycle between these backlinks.
    examples = Backlink((BacklinkCrumb("Examples", ""), BacklinkCrumb("Mid", "a/#mid")))
    guides = Backlink((BacklinkCrumb("Guides", ""), BacklinkCrumb("Zeta", ""), BacklinkCrumb("Alpha", "b/#alpha")))
    development = Backlink(
        (BacklinkCrumb("Development", ""), BacklinkCrumb("Beta", ""), BacklinkCrumb("Omega", "c/#omega")),
    )

    for backlinks in permutations((examples, guides, development)):
        ordered = sorted(backlinks, key=lambda backlink: backlink.crumbs)

        assert ordered == [development, examples, guides]


def test_backlink_crumb_page_and_first_heading() -> None:
    """Keep a page and its first heading distinct even when their titles match."""
    page = BacklinkCrumb("Guide", "guide/")
    heading = BacklinkCrumb("Guide", "guide/#guide")

    branches = {page: "page", heading: "heading"}

    assert page != heading
    assert len(branches) == 2
    assert branches[BacklinkCrumb("Guide", "guide/")] == "page"
    assert branches[BacklinkCrumb("Guide", "guide/#guide")] == "heading"
    assert sorted(branches) == [page, heading]


@pytest.mark.parametrize("heading_level", [1, 2])
@pytest.mark.parametrize("heading_title", ["Guide", "First heading"])
@pytest.mark.parametrize(("from_url", "prefix"), [("", ""), ("api/index.html", "../")])
def test_get_backlinks_with_page_and_heading_crumbs(
    heading_level: int,
    heading_title: str,
    from_url: str,
    prefix: str,
) -> None:
    """Preserve breadcrumb hierarchy and URLs with or without a top-level heading."""
    plugin = AutorefsPlugin()
    plugin.record_backlinks = True

    # An H1 replaces the page crumb; an H2 keeps the page as its parent.
    page = create_page("guides/guide.html")
    page.title = "Guide"  # ty:ignore[invalid-assignment]
    page.parent = Section("Guides", [page])
    heading = create_anchor_link(heading_title, "first", level=heading_level)
    child = create_anchor_link("Details", "details", level=3)
    heading.children.append(child)
    page.toc = TableOfContents([heading])
    plugin.on_page_content("", page)

    plugin.register_anchor(create_page("api.html"), "target", primary=True)
    plugin._record_backlink("target", "referenced-by", heading.id, page.url)
    plugin._record_backlink("target", "referenced-by", child.id, page.url)

    backlinks = plugin.get_backlinks("target", from_url=from_url)["referenced-by"]
    paths = {tuple((crumb.title, crumb.url) for crumb in backlink.crumbs) for backlink in backlinks}

    # Relative page URLs retain the existing empty fragment, while headings retain their IDs.
    ancestors = (("Guides", ""),)
    if heading_level != 1:
        ancestors += (("Guide", f"{prefix}guides/guide.html#"),)
    first_heading = (heading_title, f"{prefix}guides/guide.html#first")
    details = ("Details", f"{prefix}guides/guide.html#details")

    assert paths == {(*ancestors, first_heading), (*ancestors, first_heading, details)}


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
