"""Tests for the references module."""
import markdown
import pytest

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
def test_relative_url(current_url, to_url, href_url):
    """Compute relative URLs correctly."""
    assert relative_url(current_url, to_url) == href_url


def run_references_test(url_map, source, output, unmapped=None, from_url="page.html"):
    """Help running tests about references.

    Arguments:
        url_map: The URL mapping.
        source: The source text.
        output: The expected output.
        unmapped: The expected unmapped list.
        from_url: The source page URL.
    """
    md = markdown.Markdown(extensions=[AutorefsExtension()])
    content = md.convert(source)

    def url_mapper(identifier):  # noqa: WPS430
        return relative_url(from_url, url_map[identifier])

    actual_output, actual_unmapped = fix_refs(content, url_mapper)
    assert actual_output == output
    assert actual_unmapped == (unmapped or [])


def test_reference_implicit():
    """Check implicit references (identifier only)."""
    run_references_test(
        url_map={"Foo": "foo.html#Foo"},
        source="This [Foo][].",
        output='<p>This <a class="autorefs autorefs-internal" href="foo.html#Foo">Foo</a>.</p>',
    )


def test_reference_explicit_with_markdown_text():
    """Check explicit references with Markdown formatting."""
    run_references_test(
        url_map={"Foo": "foo.html#Foo"},
        source="This [**Foo**][Foo].",
        output='<p>This <a class="autorefs autorefs-internal" href="foo.html#Foo"><strong>Foo</strong></a>.</p>',
    )


def test_reference_implicit_with_code():
    """Check implicit references (identifier only, wrapped in backticks)."""
    run_references_test(
        url_map={"Foo": "foo.html#Foo"},
        source="This [`Foo`][].",
        output='<p>This <a class="autorefs autorefs-internal" href="foo.html#Foo"><code>Foo</code></a>.</p>',
    )


def test_reference_with_punctuation():
    """Check references with punctuation."""
    run_references_test(
        url_map={'Foo&"bar': 'foo.html#Foo&"bar'},
        source='This [Foo&"bar][].',
        output='<p>This <a class="autorefs autorefs-internal" href="foo.html#Foo&amp;&quot;bar">Foo&amp;"bar</a>.</p>',
    )


def test_reference_to_relative_path():
    """Check references from a page at a nested path."""
    run_references_test(
        from_url="sub/sub/page.html",
        url_map={"zz": "foo.html#zz"},
        source="This [zz][].",
        output='<p>This <a class="autorefs autorefs-internal" href="../../foo.html#zz">zz</a>.</p>',
    )


def test_no_reference_with_space():
    """Check that references with spaces are not fixed."""
    run_references_test(
        url_map={"Foo bar": "foo.html#Foo bar"},
        source="This [Foo bar][].",
        output="<p>This [Foo bar][].</p>",
    )


def test_no_reference_inside_markdown():
    """Check that references inside code are not fixed."""
    run_references_test(
        url_map={"Foo": "foo.html#Foo"},
        source="This `[Foo][]`.",
        output="<p>This <code>[Foo][]</code>.</p>",
    )


def test_missing_reference():
    """Check that implicit references are correctly seen as unmapped."""
    run_references_test(
        url_map={"NotFoo": "foo.html#NotFoo"},
        source="[Foo][]",
        output="<p>[Foo][]</p>",
        unmapped=["Foo"],
    )


def test_missing_reference_with_markdown_text():
    """Check unmapped explicit references."""
    run_references_test(
        url_map={"NotFoo": "foo.html#NotFoo"},
        source="[`Foo`][Foo]",
        output="<p>[<code>Foo</code>][Foo]</p>",
        unmapped=["Foo"],
    )


def test_missing_reference_with_markdown_id():
    """Check unmapped explicit references with Markdown in the identifier."""
    run_references_test(
        url_map={"Foo": "foo.html#Foo", "NotFoo": "foo.html#NotFoo"},
        source="[Foo][*NotFoo*]",
        output="<p>[Foo][*NotFoo*]</p>",
        unmapped=["*NotFoo*"],
    )


def test_missing_reference_with_markdown_implicit():
    """Check that implicit references are not fixed when the identifier is not the exact one."""
    run_references_test(
        url_map={"Foo-bar": "foo.html#Foo-bar"},
        source="[*Foo-bar*][] and [`Foo`-bar][]",
        output="<p>[<em>Foo-bar</em>][*Foo-bar*] and [<code>Foo</code>-bar][]</p>",
        unmapped=["*Foo-bar*"],
    )


def test_ignore_reference_with_special_char():
    """Check that references are not considered if there is a space character inside."""
    run_references_test(
        url_map={"a b": "foo.html#Foo"},
        source="This [*a b*][].",
        output="<p>This [<em>a b</em>][].</p>",
    )


def test_custom_required_reference():
    """Check that external HTML-based references are expanded or reported missing."""
    url_map = {"ok": "ok.html#ok"}
    source = "<span data-autorefs-identifier=bar>foo</span> <span data-autorefs-identifier=ok>ok</span>"
    output, unmapped = fix_refs(source, url_map.__getitem__)  # noqa: WPS609
    assert output == '[foo][bar] <a class="autorefs autorefs-internal" href="ok.html#ok">ok</a>'
    assert unmapped == ["bar"]


def test_custom_optional_reference():
    """Check that optional HTML-based references are expanded and never reported missing."""
    url_map = {"ok": "ok.html#ok"}
    source = '<span data-autorefs-optional="bar">foo</span> <span data-autorefs-optional=ok>ok</span>'
    output, unmapped = fix_refs(source, url_map.__getitem__)  # noqa: WPS609
    assert output == 'foo <a class="autorefs autorefs-internal" href="ok.html#ok">ok</a>'
    assert unmapped == []  # noqa: WPS520


def test_custom_optional_hover_reference():
    """Check that optional-hover HTML-based references are expanded and never reported missing."""
    url_map = {"ok": "ok.html#ok"}
    source = '<span data-autorefs-optional-hover="bar">foo</span> <span data-autorefs-optional-hover=ok>ok</span>'
    output, unmapped = fix_refs(source, url_map.__getitem__)  # noqa: WPS609
    assert (
        output
        == '<span title="bar">foo</span> <a class="autorefs autorefs-internal" title="ok" href="ok.html#ok">ok</a>'
    )
    assert unmapped == []  # noqa: WPS520


def test_external_references():
    """Check that external references are marked as such."""
    url_map = {"example": "https://example.com"}
    source = '<span data-autorefs-optional="example">example</span>'
    output, unmapped = fix_refs(source, url_map.__getitem__)  # noqa: WPS609
    assert output == '<a class="autorefs autorefs-external" href="https://example.com">example</a>'
    assert unmapped == []  # noqa: WPS520
