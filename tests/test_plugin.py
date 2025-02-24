"""Tests for the plugin module."""

from __future__ import annotations

import functools
from typing import Literal

import pytest
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.theme import Theme

from mkdocs_autorefs import AutorefsConfig, AutorefsPlugin, fix_refs
from tests.helpers import create_page


def test_url_registration() -> None:
    """Check that URLs can be registered, then obtained."""
    plugin = AutorefsPlugin()
    plugin.register_anchor(identifier="foo", page=create_page("foo1.html"), primary=True)
    plugin.register_url(identifier="bar", url="https://example.org/bar.html")

    assert plugin.get_item_url("foo") == ("foo1.html#foo", None)
    assert plugin.get_item_url("bar") == ("https://example.org/bar.html", None)
    with pytest.raises(KeyError):
        plugin.get_item_url("baz")


def test_url_registration_with_from_url() -> None:
    """Check that URLs can be registered, then obtained, relative to a page."""
    plugin = AutorefsPlugin()
    plugin.register_anchor(identifier="foo", page=create_page("foo1.html"), primary=True)
    plugin.register_url(identifier="bar", url="https://example.org/bar.html")

    assert plugin.get_item_url("foo", from_url="a/b.html") == ("../foo1.html#foo", None)
    assert plugin.get_item_url("bar", from_url="a/b.html") == ("https://example.org/bar.html", None)
    with pytest.raises(KeyError):
        plugin.get_item_url("baz", from_url="a/b.html")


# YORE: Bump 2: Remove block.
def test_url_registration_with_fallback() -> None:
    """Check that URLs can be registered, then obtained through a fallback."""
    plugin = AutorefsPlugin()
    plugin.register_anchor(identifier="foo", page=create_page("foo1.html"), primary=True)
    plugin.register_url(identifier="bar", url="https://example.org/bar.html")

    # URL map will be updated with baz -> foo1.html#foo
    assert plugin.get_item_url("baz", fallback=lambda _: ("foo",)) == ("foo1.html#foo", None)
    # as expected, baz is now known as foo1.html#foo
    assert plugin.get_item_url("baz", fallback=lambda _: ("bar",)) == ("foo1.html#foo", None)
    # unknown identifiers correctly fallback: qux -> https://example.org/bar.html
    assert plugin.get_item_url("qux", fallback=lambda _: ("bar",)) == ("https://example.org/bar.html", None)

    with pytest.raises(KeyError):
        plugin.get_item_url("foobar", fallback=lambda _: ("baaaa",))
    with pytest.raises(KeyError):
        plugin.get_item_url("foobar", fallback=lambda _: ())


def test_dont_make_relative_urls_relative_again() -> None:
    """Check that URLs are not made relative more than once."""
    plugin = AutorefsPlugin()
    plugin.register_anchor(identifier="foo.bar.baz", page=create_page("foo/bar/baz.html"), primary=True)

    for _ in range(2):
        assert plugin.get_item_url("foo.bar.baz", from_url="baz/bar/foo.html") == (
            "../../foo/bar/baz.html#foo.bar.baz",
            None,
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
    plugin.register_anchor(identifier="foo", page=create_page("foo.html"), primary=False)
    assert plugin._secondary_url_map == {"foo": ["foo.html#foo"]}


@pytest.mark.parametrize("primary", [True, False])
def test_warn_multiple_urls(caplog: pytest.LogCaptureFixture, primary: bool) -> None:
    """Warn when multiple URLs are found for the same identifier."""
    plugin = AutorefsPlugin()
    plugin.config = AutorefsConfig()
    plugin.register_anchor(identifier="foo", page=create_page("foo.html"), primary=primary)
    plugin.register_anchor(identifier="foo", page=create_page("bar.html"), primary=primary)
    url_mapper = functools.partial(plugin.get_item_url, from_url="/hello")
    # YORE: Bump 2: Replace `, _legacy_refs=False` with `` within line.
    fix_refs('<autoref identifier="foo">Foo</autoref>', url_mapper, _legacy_refs=False)
    qualifier = "primary" if primary else "secondary"
    assert (f"Multiple {qualifier} URLs found for 'foo': ['foo.html#foo', 'bar.html#foo']" in caplog.text) is primary


@pytest.mark.parametrize("primary", [True, False])
def test_use_closest_url(caplog: pytest.LogCaptureFixture, primary: bool) -> None:
    """Use the closest URL when multiple URLs are found for the same identifier."""
    plugin = AutorefsPlugin()
    plugin.config = AutorefsConfig()
    plugin.config.resolve_closest = True
    plugin.register_anchor(identifier="foo", page=create_page("foo.html"), primary=primary)
    plugin.register_anchor(identifier="foo", page=create_page("bar.html"), primary=primary)
    url_mapper = functools.partial(plugin.get_item_url, from_url="/hello")
    # YORE: Bump 2: Replace `, _legacy_refs=False` with `` within line.
    fix_refs('<autoref identifier="foo">Foo</autoref>', url_mapper, _legacy_refs=False)
    qualifier = "primary" if primary else "secondary"
    assert f"Multiple {qualifier} URLs found for 'foo': ['foo.html#foo', 'bar.html#foo']" not in caplog.text


def test_on_config_hook() -> None:
    """Check that the `on_config` hook runs without issue."""
    plugin = AutorefsPlugin()
    plugin.config = AutorefsConfig()
    plugin.on_config(config=MkDocsConfig())


def test_auto_link_titles_external() -> None:
    """Check that `link_titles` are made external when automatic and Material is detected."""
    plugin = AutorefsPlugin()
    plugin.config = AutorefsConfig()
    plugin.config.link_titles = "auto"
    config = MkDocsConfig()
    config.theme = Theme(name="material", features=["navigation.instant.preview"])
    plugin.on_config(config=config)
    assert plugin._link_titles == "external"


def test_auto_link_titles() -> None:
    """Check that `link_titles` are made true when automatic and Material is not detected."""
    plugin = AutorefsPlugin()
    plugin.config = AutorefsConfig()
    plugin.config.link_titles = "auto"
    config = MkDocsConfig()

    config.theme = Theme(name="material", features=[])
    plugin.on_config(config=config)
    assert plugin._link_titles is True

    config.theme = Theme("mkdocs")
    plugin.on_config(config=config)
    assert plugin._link_titles is True

    config.theme = Theme("readthedocs")
    plugin.on_config(config=config)
    assert plugin._link_titles is True


@pytest.mark.parametrize("link_titles", ["external", True, False])
def test_explicit_link_titles(link_titles: bool | Literal["external"]) -> None:
    """Check that explicit `link_titles` are kept unchanged."""
    plugin = AutorefsPlugin()
    plugin.config = AutorefsConfig()
    plugin.config.link_titles = link_titles
    plugin.on_config(config=MkDocsConfig())
    assert plugin._link_titles is link_titles


def test_auto_strip_title_tags_false() -> None:
    """Check that `strip_title_tags` is made false when Material is detected."""
    plugin = AutorefsPlugin()
    plugin.config = AutorefsConfig()
    plugin.config.strip_title_tags = "auto"
    config = MkDocsConfig()
    config.theme = Theme(name="material", features=["content.tooltips"])
    plugin.on_config(config=config)
    assert plugin._strip_title_tags is False


def test_auto_strip_title_tags_true() -> None:
    """Check that `strip_title_tags` are made true when automatic and Material is not detected."""
    plugin = AutorefsPlugin()
    plugin.config = AutorefsConfig()
    plugin.config.strip_title_tags = "auto"
    config = MkDocsConfig()

    config.theme = Theme(name="material", features=[])
    plugin.on_config(config=config)
    assert plugin._strip_title_tags is True

    config.theme = Theme("mkdocs")
    plugin.on_config(config=config)
    assert plugin._strip_title_tags is True

    config.theme = Theme("readthedocs")
    plugin.on_config(config=config)
    assert plugin._strip_title_tags is True


@pytest.mark.parametrize("strip_title_tags", [True, False])
def test_explicit_strip_tags(strip_title_tags: bool) -> None:
    """Check that explicit `_strip_title_tags` are kept unchanged."""
    plugin = AutorefsPlugin()
    plugin.config = AutorefsConfig()
    plugin.config.strip_title_tags = strip_title_tags
    plugin.on_config(config=MkDocsConfig())
    assert plugin._strip_title_tags is strip_title_tags
