"""Tests for the plugin module."""
import pytest

from mkdocs_autorefs.plugin import AutorefsPlugin


def test_url_registration():
    """Check that URLs can be registered, then obtained."""
    plugin = AutorefsPlugin()
    plugin.register_anchor(identifier="foo", page="foo1.html")
    plugin.register_url(identifier="bar", url="https://example.org/bar.html")

    assert plugin.get_item_url("foo") == "foo1.html#foo"
    assert plugin.get_item_url("bar") == "https://example.org/bar.html"
    with pytest.raises(KeyError):
        plugin.get_item_url("baz")


def test_url_registration_with_from_url():
    """Check that URLs can be registered, then obtained, relative to a page."""
    plugin = AutorefsPlugin()
    plugin.register_anchor(identifier="foo", page="foo1.html")
    plugin.register_url(identifier="bar", url="https://example.org/bar.html")

    assert plugin.get_item_url("foo", from_url="a/b.html") == "../foo1.html#foo"
    assert plugin.get_item_url("bar", from_url="a/b.html") == "https://example.org/bar.html"
    with pytest.raises(KeyError):
        plugin.get_item_url("baz", from_url="a/b.html")


def test_url_registration_with_fallback():
    """Check that URLs can be registered, then obtained through a fallback."""
    plugin = AutorefsPlugin()
    plugin.register_anchor(identifier="foo", page="foo1.html")
    plugin.register_url(identifier="bar", url="https://example.org/bar.html")

    assert plugin.get_item_url("baz", fallback=lambda s: "foo") == "foo1.html#foo"
    assert plugin.get_item_url("baz", fallback=lambda s: "bar") == "https://example.org/bar.html"
    with pytest.raises(KeyError):
        plugin.get_item_url("baz", fallback=lambda s: "baaaa")
    with pytest.raises(KeyError):
        plugin.get_item_url("baz", fallback=lambda s: None)
