"""Tests for the references module."""

from __future__ import annotations

from textwrap import dedent
from typing import Mapping

import markdown
import pytest

from mkdocs_autorefs.plugin import AutorefsPlugin
from mkdocs_autorefs.references import AutorefsExtension, fix_refs, relative_url


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
    url_map: dict[str, str],
    source: str,
    output: str,
    unmapped: list[str] | None = None,
    from_url: str = "page.html",
    extensions: Mapping = {},
) -> None:
    """Help running tests about references.

    Arguments:
        url_map: The URL mapping.
        source: The source text.
        output: The expected output.
        unmapped: The expected unmapped list.
        from_url: The source page URL.
    """
    md = markdown.Markdown(extensions=[AutorefsExtension(), *extensions], extension_configs=extensions)
    content = md.convert(source)

    def url_mapper(identifier: str) -> str:
        return relative_url(from_url, url_map[identifier])

    actual_output, actual_unmapped = fix_refs(content, url_mapper)
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
    """Check that references with spaces are not fixed."""
    run_references_test(
        url_map={"Foo bar": "foo.html#Foo bar"},
        source="This [Foo bar][].",
        output="<p>This [Foo bar][].</p>",
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
        unmapped=["Foo"],
    )


def test_missing_reference_with_markdown_text() -> None:
    """Check unmapped explicit references."""
    run_references_test(
        url_map={"NotFoo": "foo.html#NotFoo"},
        source="[`Foo`][Foo]",
        output="<p>[<code>Foo</code>][Foo]</p>",
        unmapped=["Foo"],
    )


def test_missing_reference_with_markdown_id() -> None:
    """Check unmapped explicit references with Markdown in the identifier."""
    run_references_test(
        url_map={"Foo": "foo.html#Foo", "NotFoo": "foo.html#NotFoo"},
        source="[Foo][*NotFoo*]",
        output="<p>[Foo][*NotFoo*]</p>",
        unmapped=["*NotFoo*"],
    )


def test_missing_reference_with_markdown_implicit() -> None:
    """Check that implicit references are not fixed when the identifier is not the exact one."""
    run_references_test(
        url_map={"Foo-bar": "foo.html#Foo-bar"},
        source="[*Foo-bar*][] and [`Foo`-bar][]",
        output="<p>[<em>Foo-bar</em>][*Foo-bar*] and [<code>Foo</code>-bar][]</p>",
        unmapped=["*Foo-bar*"],
    )


def test_ignore_reference_with_special_char() -> None:
    """Check that references are not considered if there is a space character inside."""
    run_references_test(
        url_map={"a b": "foo.html#Foo"},
        source="This [*a b*][].",
        output="<p>This [<em>a b</em>][].</p>",
    )


def test_custom_required_reference() -> None:
    """Check that external HTML-based references are expanded or reported missing."""
    url_map = {"ok": "ok.html#ok"}
    source = "<span data-autorefs-identifier=bar>foo</span> <span data-autorefs-identifier=ok>ok</span>"
    output, unmapped = fix_refs(source, url_map.__getitem__)
    assert output == '[foo][bar] <a class="autorefs autorefs-internal" href="ok.html#ok">ok</a>'
    assert unmapped == ["bar"]


def test_custom_optional_reference() -> None:
    """Check that optional HTML-based references are expanded and never reported missing."""
    url_map = {"ok": "ok.html#ok"}
    source = '<span data-autorefs-optional="bar">foo</span> <span data-autorefs-optional=ok>ok</span>'
    output, unmapped = fix_refs(source, url_map.__getitem__)
    assert output == 'foo <a class="autorefs autorefs-internal" href="ok.html#ok">ok</a>'
    assert unmapped == []


def test_custom_optional_hover_reference() -> None:
    """Check that optional-hover HTML-based references are expanded and never reported missing."""
    url_map = {"ok": "ok.html#ok"}
    source = '<span data-autorefs-optional-hover="bar">foo</span> <span data-autorefs-optional-hover=ok>ok</span>'
    output, unmapped = fix_refs(source, url_map.__getitem__)
    assert (
        output
        == '<span title="bar">foo</span> <a class="autorefs autorefs-internal" title="ok" href="ok.html#ok">ok</a>'
    )
    assert unmapped == []


def test_external_references() -> None:
    """Check that external references are marked as such."""
    url_map = {"example": "https://example.com"}
    source = '<span data-autorefs-optional="example">example</span>'
    output, unmapped = fix_refs(source, url_map.__getitem__)
    assert output == '<a class="autorefs autorefs-external" href="https://example.com">example</a>'
    assert unmapped == []


def test_register_markdown_anchors() -> None:
    """Check that Markdown anchors are registered when enabled."""
    plugin = AutorefsPlugin()
    md = markdown.Markdown(extensions=["attr_list", "toc", AutorefsExtension(plugin)])
    plugin.current_page = "page"
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

            [](){#alias10}
            """,
        ),
    )
    assert plugin._url_map == {
        "foo": "page#heading-foo",
        "bar": "page#bar",
        "alias1": "page#heading-bar",
        "alias2": "page#heading-bar",
        "alias3": "page#alias3",
        "alias4": "page#heading-baz",
        "alias5": "page#alias5",
        "alias6": "page#alias6",
        "alias7": "page#alias7",
        "alias8": "page#alias8",
        "alias9": "page#heading-custom2",
        "alias10": "page#alias10",
    }


def test_register_markdown_anchors_with_admonition() -> None:
    """Check that Markdown anchors are registered inside a nested admonition element."""
    plugin = AutorefsPlugin()
    md = markdown.Markdown(extensions=["attr_list", "toc", "admonition", AutorefsExtension(plugin)])
    plugin.current_page = "page"
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
    assert plugin._url_map == {
        "alias1": "page#alias1",
        "alias2": "page#heading-bar",
        "alias3": "page#alias3",
    }


def test_keep_data_attributes() -> None:
    """Keep HTML data attributes from autorefs spans."""
    url_map = {"example": "https://e.com"}
    source = '<span data-autorefs-optional="example" class="hi ho" data-foo data-bar="0">e</span>'
    output, _ = fix_refs(source, url_map.__getitem__)
    assert output == '<a class="autorefs autorefs-external hi ho" href="https://e.com" data-foo data-bar="0">e</a>'
