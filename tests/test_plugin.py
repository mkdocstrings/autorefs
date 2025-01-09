"""Tests for the plugin module."""

from __future__ import annotations

import pytest

from mkdocs_autorefs.plugin import AutorefsPlugin


def test_url_registration() -> None:
    """Check that URLs can be registered, then obtained."""
    plugin = AutorefsPlugin()
    plugin.register_anchor(identifier="foo", page="foo1.html", primary=True)
    plugin.register_url(identifier="bar", url="https://example.org/bar.html")

    assert plugin.get_item_url("foo") == "foo1.html#foo"
    assert plugin.get_item_url("bar") == "https://example.org/bar.html"
    with pytest.raises(KeyError):
        plugin.get_item_url("baz")


def test_url_registration_with_from_url() -> None:
    """Check that URLs can be registered, then obtained, relative to a page."""
    plugin = AutorefsPlugin()
    plugin.register_anchor(identifier="foo", page="foo1.html", primary=True)
    plugin.register_url(identifier="bar", url="https://example.org/bar.html")

    assert plugin.get_item_url("foo", from_url="a/b.html") == "../foo1.html#foo"
    assert plugin.get_item_url("bar", from_url="a/b.html") == "https://example.org/bar.html"
    with pytest.raises(KeyError):
        plugin.get_item_url("baz", from_url="a/b.html")


def test_url_registration_with_fallback() -> None:
    """Check that URLs can be registered, then obtained through a fallback."""
    plugin = AutorefsPlugin()
    plugin.register_anchor(identifier="foo", page="foo1.html", primary=True)
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
    plugin.register_anchor(identifier="foo.bar.baz", page="foo/bar/baz.html", primary=True)

    for _ in range(2):
        assert (
            plugin.get_item_url("hello", from_url="baz/bar/foo.html", fallback=lambda _: ("foo.bar.baz",))
            == "../../foo/bar/baz.html#foo.bar.baz"
        )


@pytest.mark.parametrize(
    ("base", "urls", "expected"),
    [
        # One URL is closest.
        ("", ["x/#b", "#b"], "#b"),
        # Several URLs are equally close.
        ("a/b", ["x/#e", "a/c/#e", "a/d/#e"], "a/c/#e"),
        ("a/b/", ["x/#e", "a/d/#e", "a/c/#e"], "a/d/#e"),
        # Two close URLs, one is shorter (closer).
        ("a/b", ["x/#e", "a/c/#e", "a/c/d/#e"], "a/c/#e"),
        ("a/b/", ["x/#e", "a/c/d/#e", "a/c/#e"], "a/c/#e"),
        # Deeper-nested URLs.
        ("a/b/c", ["x/#e", "a/#e", "a/b/#e", "a/b/c/#e", "a/b/c/d/#e"], "a/b/c/#e"),
        ("a/b/c/", ["x/#e", "a/#e", "a/b/#e", "a/b/c/d/#e", "a/b/c/#e"], "a/b/c/#e"),
        # No closest URL, use first one even if longer distance.
        ("a", ["b/c/#d", "c/#d"], "b/c/#d"),
        ("a/", ["c/#d", "b/c/#d"], "c/#d"),
    ],
)
def test_find_closest_url(base: str, urls: list[str], expected: str) -> None:
    """Find closest URLs given a list of URLs."""
    assert AutorefsPlugin._get_closest_url(base, urls, "test") == expected


def test_register_secondary_url() -> None:
    """Test registering secondary URLs."""
    plugin = AutorefsPlugin()
    plugin.register_anchor(identifier="foo", page="foo.html", primary=False)
    assert plugin._secondary_url_map == {"foo": ["foo.html#foo"]}
