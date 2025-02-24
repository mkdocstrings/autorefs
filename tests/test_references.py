"""Tests for the references module."""

from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING, Any

import markdown
import pytest

from mkdocs_autorefs import AutorefsExtension, AutorefsHookInterface, AutorefsPlugin, fix_refs, relative_url
from tests.helpers import create_page

if TYPE_CHECKING:
    from collections.abc import Mapping


@pytest.mark.parametrize(
    ("current_url", "to_url", "href_url"),
    [
        ("a/", "a#b", "#b"),
        ("a/", "a/b#c", "b#c"),
        ("a/b/", "a/b#c", "#c"),
        ("a/b/", "a/c#d", "../c#d"),
        ("a/b/", "a#c", "..#c"),
        ("a/b/c/", "d#e", "../../../d#e"),
        ("a/b/", "c/d/#e", "../../c/d/#e"),
        ("a/index.html", "a/index.html#b", "#b"),
        ("a/index.html", "a/b.html#c", "b.html#c"),
        ("a/b.html", "a/b.html#c", "#c"),
        ("a/b.html", "a/c.html#d", "c.html#d"),
        ("a/b.html", "a/index.html#c", "index.html#c"),
        ("a/b/c.html", "d.html#e", "../../d.html#e"),
        ("a/b.html", "c/d.html#e", "../c/d.html#e"),
        ("a/b/index.html", "a/b/c/d.html#e", "c/d.html#e"),
        ("", "#x", "#x"),
        ("a/", "#x", "../#x"),
        ("a/b.html", "#x", "../#x"),
        ("", "a/#x", "a/#x"),
        ("", "a/b.html#x", "a/b.html#x"),
    ],
)
def test_relative_url(current_url: str, to_url: str, href_url: str) -> None:
    """Compute relative URLs correctly."""
    assert relative_url(current_url, to_url) == href_url


def run_references_test(
    url_map: Mapping[str, str],
    source: str,
    output: str,
    unmapped: list[tuple[str, AutorefsHookInterface.Context | None]] | None = None,
    from_url: str = "page.html",
    extensions: Mapping[str, Mapping[str, Any]] | None = None,
    title_map: Mapping[str, str] | None = None,
    *,
    strip_tags: bool = True,
) -> None:
    """Help running tests about references.

    Arguments:
        url_map: The URL mapping.
        source: The source text.
        output: The expected output.
        unmapped: The expected unmapped list.
        from_url: The source page URL.
    """
    extensions = extensions or {}
    md = markdown.Markdown(extensions=[AutorefsExtension(), *extensions], extension_configs=extensions)
    content = md.convert(source)
    title_map = title_map or {}

    def url_mapper(identifier: str) -> tuple[str, str | None]:
        return relative_url(from_url, url_map[identifier]), title_map.get(identifier, None)

    actual_output, actual_unmapped = fix_refs(content, url_mapper, strip_title_tags=strip_tags)
    assert actual_output == output
    assert actual_unmapped == (unmapped or [])


def test_reference_implicit() -> None:
    """Check implicit references (identifier only)."""
    run_references_test(
        url_map={"Foo": "foo.html#Foo"},
        source="This [Foo][].",
        output='<p>This <a class="autorefs autorefs-internal" href="foo.html#Foo">Foo</a>.</p>',
    )


def test_reference_explicit_with_markdown_text() -> None:
    """Check explicit references with Markdown formatting."""
    run_references_test(
        url_map={"Foo": "foo.html#Foo"},
        source="This [**Foo**][Foo].",
        output='<p>This <a class="autorefs autorefs-internal" href="foo.html#Foo"><strong>Foo</strong></a>.</p>',
    )


def test_reference_implicit_with_code() -> None:
    """Check implicit references (identifier only, wrapped in backticks)."""
    run_references_test(
        url_map={"Foo": "foo.html#Foo"},
        source="This [`Foo`][].",
        output='<p>This <a class="autorefs autorefs-internal" href="foo.html#Foo"><code>Foo</code></a>.</p>',
    )


def test_reference_implicit_with_code_inlinehilite_plain() -> None:
    """Check implicit references (identifier in backticks, wrapped by inlinehilite)."""
    run_references_test(
        extensions={"pymdownx.inlinehilite": {}},
        url_map={"pathlib.Path": "pathlib.html#Path"},
        source="This [`pathlib.Path`][].",
        output='<p>This <a class="autorefs autorefs-internal" href="pathlib.html#Path"><code>pathlib.Path</code></a>.</p>',
    )


def test_reference_implicit_with_code_inlinehilite_python() -> None:
    """Check implicit references (identifier in backticks, syntax-highlighted by inlinehilite)."""
    run_references_test(
        extensions={"pymdownx.inlinehilite": {"style_plain_text": "python"}, "pymdownx.highlight": {}},
        url_map={"pathlib.Path": "pathlib.html#Path"},
        source="This [`pathlib.Path`][].",
        output='<p>This <a class="autorefs autorefs-internal" href="pathlib.html#Path"><code class="highlight">pathlib.Path</code></a>.</p>',
    )


def test_reference_with_punctuation() -> None:
    """Check references with punctuation."""
    run_references_test(
        url_map={'Foo&"bar': 'foo.html#Foo&"bar'},
        source='This [Foo&"bar][].',
        output='<p>This <a class="autorefs autorefs-internal" href="foo.html#Foo&amp;&quot;bar">Foo&amp;"bar</a>.</p>',
    )


def test_reference_to_relative_path() -> None:
    """Check references from a page at a nested path."""
    run_references_test(
        from_url="sub/sub/page.html",
        url_map={"zz": "foo.html#zz"},
        source="This [zz][].",
        output='<p>This <a class="autorefs autorefs-internal" href="../../foo.html#zz">zz</a>.</p>',
    )


def test_multiline_links() -> None:
    """Check that links with multiline text are recognized."""
    run_references_test(
        url_map={"foo-bar": "foo.html#bar"},
        source="This [Foo\nbar][foo-bar].",
        output='<p>This <a class="autorefs autorefs-internal" href="foo.html#bar">Foo\nbar</a>.</p>',
    )


def test_no_reference_with_space() -> None:
    """Check that references with spaces are fixed."""
    run_references_test(
        url_map={"Foo bar": "foo.html#bar"},
        source="This [Foo bar][].",
        output='<p>This <a class="autorefs autorefs-internal" href="foo.html#bar">Foo bar</a>.</p>',
    )


def test_no_reference_inside_markdown() -> None:
    """Check that references inside code are not fixed."""
    run_references_test(
        url_map={"Foo": "foo.html#Foo"},
        source="This `[Foo][]`.",
        output="<p>This <code>[Foo][]</code>.</p>",
    )


def test_missing_reference() -> None:
    """Check that implicit references are correctly seen as unmapped."""
    run_references_test(
        url_map={"NotFoo": "foo.html#NotFoo"},
        source="[Foo][]",
        output="<p>[Foo][]</p>",
        unmapped=[("Foo", None)],
    )


def test_missing_reference_with_markdown_text() -> None:
    """Check unmapped explicit references."""
    run_references_test(
        url_map={"NotFoo": "foo.html#NotFoo"},
        source="[`Foo`][Foo]",
        output="<p>[<code>Foo</code>][]</p>",
        unmapped=[("Foo", None)],
    )


def test_missing_reference_with_markdown_id() -> None:
    """Check unmapped explicit references with Markdown in the identifier."""
    run_references_test(
        url_map={"Foo": "foo.html#Foo", "NotFoo": "foo.html#NotFoo"},
        source="[Foo][*NotFoo*]",
        output="<p>[Foo][*NotFoo*]</p>",
        unmapped=[("*NotFoo*", None)],
    )


def test_missing_reference_with_markdown_implicit() -> None:
    """Check that implicit references are not fixed when the identifier is not the exact one."""
    run_references_test(
        url_map={"Foo-bar": "foo.html#Foo-bar"},
        source="[*Foo-bar*][] and [`Foo`-bar][]",
        output="<p>[<em>Foo-bar</em>][*Foo-bar*] and [<code>Foo</code>-bar][`Foo`-bar]</p>",
        unmapped=[("*Foo-bar*", None), ("`Foo`-bar", None)],
    )


def test_reference_with_markup() -> None:
    """Check that references with markup are resolved (and need escaping to prevent rendering)."""
    run_references_test(
        url_map={"*a b*": "foo.html#Foo"},
        source="This [*a b*][].",
        output='<p>This <a class="autorefs autorefs-internal" href="foo.html#Foo"><em>a b</em></a>.</p>',
    )
    run_references_test(
        url_map={"*a/b*": "foo.html#Foo"},
        source="This [`*a/b*`][].",
        output='<p>This <a class="autorefs autorefs-internal" href="foo.html#Foo"><code>*a/b*</code></a>.</p>',
    )


# YORE: Bump 2: Remove block.
def test_legacy_custom_required_reference() -> None:
    """Check that external HTML-based references are expanded or reported missing."""
    with pytest.warns(DeprecationWarning, match="`span` elements are deprecated"):
        run_references_test(
            url_map={"ok": "ok.html#ok"},
            source="<span data-autorefs-identifier=bar>foo</span> <span data-autorefs-identifier=ok>ok</span>",
            output='<p>[foo][bar] <a class="autorefs autorefs-internal" href="ok.html#ok">ok</a></p>',
            unmapped=[("bar", None)],
        )


def test_custom_required_reference() -> None:
    """Check that external HTML-based references are expanded or reported missing."""
    run_references_test(
        url_map={"ok": "ok.html#ok"},
        source="<autoref identifier=bar>foo</autoref> <autoref identifier=ok>ok</autoref>",
        output='<p>[foo][bar] <a class="autorefs autorefs-internal" href="ok.html#ok">ok</a></p>',
        unmapped=[("bar", None)],
    )


# YORE: Bump 2: Remove block.
def test_legacy_custom_optional_reference() -> None:
    """Check that optional HTML-based references are expanded and never reported missing."""
    with pytest.warns(DeprecationWarning, match="`span` elements are deprecated"):
        run_references_test(
            url_map={"ok": "ok.html#ok"},
            source='<span data-autorefs-optional="bar">foo</span> <span data-autorefs-optional=ok>ok</span>',
            output='<p>foo <a class="autorefs autorefs-internal" href="ok.html#ok">ok</a></p>',
        )


def test_custom_optional_reference() -> None:
    """Check that optional HTML-based references are expanded and never reported missing."""
    run_references_test(
        url_map={"ok": "ok.html#ok"},
        source='<autoref optional identifier="foo">bar</autoref> <autoref optional identifier="ok">ok</autoref>',
        output='<p><span title="foo">bar</span> <a class="autorefs autorefs-internal" href="ok.html#ok">ok</a></p>',
    )


# YORE: Bump 2: Remove block.
def test_legacy_custom_optional_hover_reference() -> None:
    """Check that optional-hover HTML-based references are expanded and never reported missing."""
    with pytest.warns(DeprecationWarning, match="`span` elements are deprecated"):
        run_references_test(
            url_map={"ok": "ok.html#ok"},
            source='<span data-autorefs-optional-hover="bar">foo</span> <span data-autorefs-optional-hover=ok>ok</span>',
            output='<p><span title="bar">foo</span> <a class="autorefs autorefs-internal" title="ok" href="ok.html#ok">ok</a></p>',
        )


# YORE: Bump 2: Remove block.
def test_legacy_external_references() -> None:
    """Check that external references are marked as such."""
    with pytest.warns(DeprecationWarning, match="`span` elements are deprecated"):
        run_references_test(
            url_map={"example": "https://example.com/#example"},
            source='<span data-autorefs-optional="example">example</span>',
            output='<p><a class="autorefs autorefs-external" href="https://example.com/#example">example</a></p>',
        )


def test_external_references() -> None:
    """Check that external references are marked as such."""
    run_references_test(
        url_map={"example": "https://example.com/#example"},
        source='<autoref optional identifier="example">example</autoref>',
        output='<p><a class="autorefs autorefs-external" href="https://example.com/#example">example</a></p>',
    )


def test_register_markdown_anchors() -> None:
    """Check that Markdown anchors are registered when enabled."""
    plugin = AutorefsPlugin()
    md = markdown.Markdown(extensions=["attr_list", "toc", AutorefsExtension(plugin)])
    plugin.current_page = create_page("page")
    md.convert(
        dedent(
            """
            [](){#foo}
            ## Heading foo

            Paragraph 1.

            [](){#bar}
            Paragraph 2.

            [](){#alias1}
            [](){#alias2}
            ## Heading bar

            [](){#alias3}
            Text.
            [](){#alias4}
            ## Heading baz

            [](){#alias5}
            [](){#alias6}
            Decoy.
            ## Heading more1

            [](){#alias7}
            [decoy](){#alias8}
            [](){#alias9}
            ## Heading more2 {#heading-custom2}

            [](){#aliasSame}
            ## Same heading 1
            [](){#aliasSame}
            ## Same heading 2

            [](){#alias10}
            """,
        ),
    )
    assert plugin._primary_url_map == {
        "foo": ["page#heading-foo"],
        "bar": ["page#bar"],
        "alias1": ["page#heading-bar"],
        "alias2": ["page#heading-bar"],
        "alias3": ["page#alias3"],
        "alias4": ["page#heading-baz"],
        "alias5": ["page#alias5"],
        "alias6": ["page#alias6"],
        "alias7": ["page#alias7"],
        "alias8": ["page#alias8"],
        "alias9": ["page#heading-custom2"],
        "alias10": ["page#alias10"],
        "aliasSame": ["page#same-heading-1", "page#same-heading-2"],
    }


def test_register_markdown_anchors_with_admonition() -> None:
    """Check that Markdown anchors are registered inside a nested admonition element."""
    plugin = AutorefsPlugin()
    md = markdown.Markdown(extensions=["attr_list", "toc", "admonition", AutorefsExtension(plugin)])
    plugin.current_page = create_page("page")
    md.convert(
        dedent(
            """
            [](){#alias1}
            !!! note
                ## Heading foo

                [](){#alias2}
                ## Heading bar

                [](){#alias3}
            ## Heading baz
            """,
        ),
    )
    assert plugin._primary_url_map == {
        "alias1": ["page#alias1"],
        "alias2": ["page#heading-bar"],
        "alias3": ["page#alias3"],
    }


# YORE: Bump 2: Remove block.
def test_legacy_keep_data_attributes() -> None:
    """Keep HTML data attributes from autorefs spans."""
    with pytest.warns(DeprecationWarning, match="`span` elements are deprecated"):
        run_references_test(
            url_map={"example": "https://e.com/#example"},
            source='<span data-autorefs-optional="example" class="hi ho" data-foo data-bar="0">e</span>',
            output='<p><a class="autorefs autorefs-external hi ho" href="https://e.com/#example" data-foo data-bar="0">e</a></p>',
        )


def test_keep_data_attributes() -> None:
    """Keep HTML data attributes from autorefs spans."""
    run_references_test(
        url_map={"example": "https://e.com#a"},
        source='<autoref optional identifier="example" class="hi ho" data-foo data-bar="0">example</autoref>',
        output='<p><a class="autorefs autorefs-external hi ho" href="https://e.com#a" data-foo data-bar="0">example</a></p>',
    )


@pytest.mark.parametrize(
    ("markdown_ref", "exact_expected"),
    [
        ("[Foo][]", False),
        ("[\\`Foo][]", False),
        ("[\\`\\`Foo][]", False),
        ("[\\`\\`Foo\\`][]", False),
        ("[Foo\\`][]", False),
        ("[Foo\\`\\`][]", False),
        ("[\\`Foo\\`\\`][]", False),
        ("[`Foo` `Bar`][]", False),
        ("[Foo][Foo]", True),
        ("[`Foo`][]", True),
        ("[`Foo``Bar`][]", True),
        ("[`Foo```Bar`][]", True),
        ("[``Foo```Bar``][]", True),
        ("[``Foo`Bar``][]", True),
        ("[```Foo``Bar```][]", True),
    ],
)
def test_mark_identifiers_as_exact(markdown_ref: str, exact_expected: bool) -> None:
    """Mark code and explicit identifiers as exact (no `slug` attribute in autoref elements)."""
    plugin = AutorefsPlugin()
    md = markdown.Markdown(extensions=["attr_list", "toc", AutorefsExtension(plugin)])
    plugin.current_page = create_page("page")
    output = md.convert(markdown_ref)
    if exact_expected:
        assert "slug=" not in output
    else:
        assert "slug=" in output


def test_slugified_identifier_fallback() -> None:
    """Fallback to the slugified identifier when no URL is found."""
    run_references_test(
        url_map={"hello-world": "https://e.com#a"},
        source='<autoref identifier="Hello World" slug="hello-world">Hello World</autoref>',
        output='<p><a class="autorefs autorefs-external" href="https://e.com#a">Hello World</a></p>',
    )
    run_references_test(
        url_map={"foo-bar": "https://e.com#a"},
        source="[*Foo*-bar][]",
        output='<p><a class="autorefs autorefs-external" href="https://e.com#a"><em>Foo</em>-bar</a></p>',
    )
    run_references_test(
        url_map={"foo-bar": "https://e.com#a"},
        source="[`Foo`-bar][]",
        output='<p><a class="autorefs autorefs-external" href="https://e.com#a"><code>Foo</code>-bar</a></p>',
    )


def test_no_fallback_for_exact_identifiers() -> None:
    """Do not fallback to the slugified identifier for exact identifiers."""
    run_references_test(
        url_map={"hello-world": "https://e.com"},
        source='<autoref identifier="Hello World"><code>Hello World</code></autoref>',
        output="<p>[<code>Hello World</code>][]</p>",
        unmapped=[("Hello World", None)],
    )

    run_references_test(
        url_map={"hello-world": "https://e.com"},
        source='<autoref identifier="Hello World">Hello World</autoref>',
        output="<p>[Hello World][]</p>",
        unmapped=[("Hello World", None)],
    )


def test_no_fallback_for_provided_identifiers() -> None:
    """Do not slugify provided identifiers."""
    run_references_test(
        url_map={"hello-world": "foo.html#hello-world"},
        source="[Hello][Hello world]",
        output="<p>[Hello][Hello world]</p>",
        unmapped=[("Hello world", None)],
    )


def test_title_use_identifier() -> None:
    """Check that the identifier is used for the title."""
    run_references_test(
        url_map={"fully.qualified.name": "ok.html#fully.qualified.name"},
        source='<autoref optional identifier="fully.qualified.name">name</autoref>',
        output='<p><a class="autorefs autorefs-internal" title="fully.qualified.name" href="ok.html#fully.qualified.name">name</a></p>',
    )


def test_title_append_identifier() -> None:
    """Check that the identifier is appended to the title."""
    run_references_test(
        url_map={"fully.qualified.name": "ok.html#fully.qualified.name"},
        title_map={"fully.qualified.name": "Qualified Name"},
        source='<autoref optional identifier="fully.qualified.name">name</autoref>',
        output='<p><a class="autorefs autorefs-internal" title="Qualified Name (fully.qualified.name)" href="ok.html#fully.qualified.name">name</a></p>',
    )
