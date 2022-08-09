"""Tests for the plugin module."""

from __future__ import annotations

import pytest

from mkdocs_autorefs.plugin import AutorefsPlugin


def test_url_registration() -> None:
    """Check that URLs can be registered, then obtained."""
    plugin = AutorefsPlugin()
    plugin.register_anchor(identifier="foo", page="foo1.html")
    plugin.register_url(identifier="bar", url="https://example.org/bar.html")

    assert plugin.get_item_url("foo") == "foo1.html#foo"
    assert plugin.get_item_url("bar") == "https://example.org/bar.html"
    with pytest.raises(KeyError):
        plugin.get_item_url("baz")


def test_url_registration_with_from_url() -> None:
    """Check that URLs can be registered, then obtained, relative to a page."""
    plugin = AutorefsPlugin()
    plugin.register_anchor(identifier="foo", page="foo1.html")
    plugin.register_url(identifier="bar", url="https://example.org/bar.html")

    assert plugin.get_item_url("foo", from_url="a/b.html") == "../foo1.html#foo"
    assert plugin.get_item_url("bar", from_url="a/b.html") == "https://example.org/bar.html"
    with pytest.raises(KeyError):
        plugin.get_item_url("baz", from_url="a/b.html")


def test_url_registration_with_fallback() -> None:
    """Check that URLs can be registered, then obtained through a fallback."""
    plugin = AutorefsPlugin()
    plugin.register_anchor(identifier="foo", page="foo1.html")
    plugin.register_url(identifier="bar", url="https://example.org/bar.html")

    # URL map will be updated with baz -> foo1.html#foo
    assert plugin.get_item_url("baz", fallback=lambda _: ("foo",)) == "foo1.html#foo"
    # as expected, baz is now known as foo1.html#foo
    assert plugin.get_item_url("baz", fallback=lambda _: ("bar",)) == "foo1.html#foo"
    # unknown identifiers correctly fallback: qux -> https://example.org/bar.html
    assert plugin.get_item_url("qux", fallback=lambda _: ("bar",)) == "https://example.org/bar.html"

    with pytest.raises(KeyError):
        plugin.get_item_url("foobar", fallback=lambda _: ("baaaa",))
    with pytest.raises(KeyError):
        plugin.get_item_url("foobar", fallback=lambda _: ())


def test_dont_make_relative_urls_relative_again() -> None:
    """Check that URLs are not made relative more than once."""
    plugin = AutorefsPlugin()
    plugin.register_anchor(identifier="foo.bar.baz", page="foo/bar/baz.html")

    for _ in range(2):
        assert (
            plugin.get_item_url("hello", from_url="baz/bar/foo.html", fallback=lambda _: ("foo.bar.baz",))
            == "../../foo/bar/baz.html#foo.bar.baz"
        )


def test_register_html_anchors() -> None:
    """Check that HT?ML anchors are registered when enabled."""
    plugin = AutorefsPlugin()
    plugin.scan_toc = False
    plugin.scan_anchors = True

    class Page:
        url = "/page/url"

    plugin.on_page_content(
        """
        <a id="foo.bar">
        <a href="#foo.baz">
        <a id="foo.qux" href="#fooqux">
        <a href="quxfoo" id="qux.foo">
        """,
        page=Page(),  # type: ignore[arg-type]
    )
    assert "foo.bar" in plugin._url_map
    assert "foo.baz" not in plugin._url_map
    assert "foo.qux" in plugin._url_map
    assert "qux.foo" in plugin._url_map
