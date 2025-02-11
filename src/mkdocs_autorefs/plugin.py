"""This module contains the "mkdocs-autorefs" plugin.

After each page is processed by the Markdown converter, this plugin stores absolute URLs of every HTML anchors
it finds to later be able to fix unresolved references.
It stores them during the [`on_page_content` event hook](https://www.mkdocs.org/user-guide/plugins/#on_page_content).

Just before writing the final HTML to the disc, during the
[`on_post_page` event hook](https://www.mkdocs.org/user-guide/plugins/#on_post_page),
this plugin searches for references of the form `[identifier][]` or `[title][identifier]` that were not resolved,
and fixes them using the previously stored identifier-URL mapping.
"""

from __future__ import annotations

import contextlib
import functools
import logging
from pathlib import PurePosixPath as URL  # noqa: N814
from typing import TYPE_CHECKING, Any, Callable
from urllib.parse import urlsplit
from warnings import warn

from mkdocs.config.base import Config
from mkdocs.config.config_options import Type
from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page

from mkdocs_autorefs.references import AutorefsExtension, fix_refs, relative_url

if TYPE_CHECKING:
    from collections.abc import Sequence

    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.pages import Page
    from mkdocs.structure.toc import AnchorLink

try:
    from mkdocs.plugins import get_plugin_logger

    log = get_plugin_logger(__name__)
except ImportError:
    # TODO: remove once support for MkDocs <1.5 is dropped
    log = logging.getLogger(f"mkdocs.plugins.{__name__}")  # type: ignore[assignment]


class AutorefsConfig(Config):
    """Configuration options for the `autorefs` plugin."""

    resolve_closest = Type(bool, default=False)
    """Whether to resolve an autoref to the closest URL when multiple URLs are found for an identifier.

    By closest, we mean a combination of "relative to the current page" and "shortest distance from the current page".

    For example, if you link to identifier `hello` from page `foo/bar/`,
    and the identifier is found in `foo/`, `foo/baz/` and `foo/bar/baz/qux/` pages,
    autorefs will resolve to `foo/bar/baz/qux`, which is the only URL relative to `foo/bar/`.

    If multiple URLs are equally close, autorefs will resolve to the first of these equally close URLs.
    If autorefs cannot find any URL that is close to the current page, it will log a warning and resolve to the first URL found.

    When false and multiple URLs are found for an identifier, autorefs will log a warning and resolve to the first URL.
    """


class AutorefsPlugin(BasePlugin[AutorefsConfig]):
    """The `autorefs` plugin for `mkdocs`.

    This plugin defines the following event hooks:

    - `on_config`
    - `on_page_content`
    - `on_post_page`

    Check the [Developing Plugins](https://www.mkdocs.org/user-guide/plugins/#developing-plugins) page of `mkdocs`
    for more information about its plugin system.
    """

    scan_toc: bool = True
    current_page: str | None = None
    # YORE: Bump 2: Remove line.
    legacy_refs: bool = True

    def __init__(self) -> None:
        """Initialize the object."""
        super().__init__()

        # The plugin uses three URL maps, one for "primary" URLs, one for "secondary" URLs,
        # and one for "absolute" URLs.
        #
        # - A primary URL is an identifier that links to a specific anchor on a page.
        # - A secondary URL is an alias of an identifier that links to the same anchor as the identifier's primary URL.
        #   Primary URLs with these aliases as identifiers may or may not be rendered later.
        # - An absolute URL is an identifier that links to an external resource.
        #   These URLs are typically registered by mkdocstrings when loading object inventories.
        #
        # For example, mkdocstrings registers a primary URL for each heading rendered in a page.
        # Then, for each alias of this heading's identifier, it registers a secondary URL.
        #
        # We need to keep track of whether an identifier is primary or secondary,
        # to give it precedence when resolving cross-references.
        # We wouldn't want to log a warning if there is a single primary URL and one or more secondary URLs,
        # instead we want to use the primary URL without any warning.
        #
        # - A single primary URL mapped to an identifer? Use it.
        # - Multiple primary URLs mapped to an identifier? Use the first one, or closest one if configured as such.
        # - No primary URL mapped to an identifier, but a secondary URL mapped? Use it.
        # - Multiple secondary URLs mapped to an identifier? Use the first one, or closest one if configured as such.
        # - No secondary URL mapped to an identifier? Try using absolute URLs
        #   (typically registered by loading inventories in mkdocstrings).
        #
        # This logic unfolds in `_get_item_url`.
        self._primary_url_map: dict[str, list[str]] = {}
        self._secondary_url_map: dict[str, list[str]] = {}
        self._abs_url_map: dict[str, str] = {}
        # YORE: Bump 2: Remove line.
        self._get_fallback_anchor: Callable[[str], tuple[str, ...]] | None = None

    # YORE: Bump 2: Remove block.
    @property
    def get_fallback_anchor(self) -> Callable[[str], tuple[str, ...]] | None:
        """Fallback anchors getter."""
        return self._get_fallback_anchor

    # YORE: Bump 2: Remove block.
    @get_fallback_anchor.setter
    def get_fallback_anchor(self, value: Callable[[str], tuple[str, ...]] | None) -> None:
        """Fallback anchors setter."""
        self._get_fallback_anchor = value
        if value is not None:
            warn(
                "Setting a fallback anchor function is deprecated and will be removed in a future release.",
                DeprecationWarning,
                stacklevel=2,
            )

    def register_anchor(self, page: str, identifier: str, anchor: str | None = None, *, primary: bool = True) -> None:
        """Register that an anchor corresponding to an identifier was encountered when rendering the page.

        Arguments:
            page: The relative URL of the current page. Examples: `'foo/bar/'`, `'foo/index.html'`
            identifier: The identifier to register.
            anchor: The anchor on the page, without `#`. If not provided, defaults to the identifier.
            primary: Whether this anchor is the primary one for the identifier.
        """
        page_anchor = f"{page}#{anchor or identifier}"
        url_map = self._primary_url_map if primary else self._secondary_url_map
        if identifier in url_map:
            if page_anchor not in url_map[identifier]:
                url_map[identifier].append(page_anchor)
        else:
            url_map[identifier] = [page_anchor]

    def register_url(self, identifier: str, url: str) -> None:
        """Register that the identifier should be turned into a link to this URL.

        Arguments:
            identifier: The new identifier.
            url: The absolute URL (including anchor, if needed) where this item can be found.
        """
        self._abs_url_map[identifier] = url

    @staticmethod
    def _get_closest_url(from_url: str, urls: list[str], qualifier: str) -> str:
        """Return the closest URL to the current page.

        Arguments:
            from_url: The URL of the base page, from which we link towards the targeted pages.
            urls: A list of URLs to choose from.
            qualifier: The type of URLs we are choosing from.

        Returns:
            The closest URL to the current page.
        """
        base_url = URL(from_url)

        while True:
            if candidates := [url for url in urls if URL(url).is_relative_to(base_url)]:
                break
            base_url = base_url.parent
            if not base_url.name:
                break

        if not candidates:
            log.warning(
                "Could not find closest %s URL (from %s, candidates: %s). "
                "Make sure to use unique headings, identifiers, or Markdown anchors (see our docs).",
                qualifier,
                from_url,
                urls,
            )
            return urls[0]

        winner = candidates[0] if len(candidates) == 1 else min(candidates, key=lambda c: c.count("/"))
        log.debug("Closest URL found: %s (from %s, candidates: %s)", winner, from_url, urls)
        return winner

    def _get_urls(self, identifier: str) -> tuple[list[str], str]:
        try:
            return self._primary_url_map[identifier], "primary"
        except KeyError:
            return self._secondary_url_map[identifier], "secondary"

    def _get_item_url(
        self,
        identifier: str,
        from_url: str | None = None,
        # YORE: Bump 2: Remove line.
        fallback: Callable[[str], Sequence[str]] | None = None,
    ) -> str:
        try:
            urls, qualifier = self._get_urls(identifier)
        except KeyError:
            # YORE: Bump 2: Replace block with line 2.
            if identifier in self._abs_url_map:
                return self._abs_url_map[identifier]
            if fallback:
                new_identifiers = fallback(identifier)
                for new_identifier in new_identifiers:
                    with contextlib.suppress(KeyError):
                        url = self._get_item_url(new_identifier)
                        self._secondary_url_map[identifier] = [url]
                        return url
            raise

        if len(urls) > 1:
            if (self.config.resolve_closest or qualifier == "secondary") and from_url is not None:
                return self._get_closest_url(from_url, urls, qualifier)
            log.warning(
                "Multiple %s URLs found for '%s': %s. "
                "Make sure to use unique headings, identifiers, or Markdown anchors (see our docs).",
                qualifier,
                identifier,
                urls,
            )
        return urls[0]

    def get_item_url(
        self,
        identifier: str,
        from_url: str | None = None,
        # YORE: Bump 2: Remove line.
        fallback: Callable[[str], Sequence[str]] | None = None,
    ) -> str:
        """Return a site-relative URL with anchor to the identifier, if it's present anywhere.

        Arguments:
            identifier: The anchor (without '#').
            from_url: The URL of the base page, from which we link towards the targeted pages.

        Returns:
            A site-relative URL.
        """
        # YORE: Bump 2: Replace `, fallback` with `` within line.
        url = self._get_item_url(identifier, from_url, fallback)
        if from_url is not None:
            parsed = urlsplit(url)
            if not parsed.scheme and not parsed.netloc:
                return relative_url(from_url, url)
        return url

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig | None:
        """Instantiate our Markdown extension.

        Hook for the [`on_config` event](https://www.mkdocs.org/user-guide/plugins/#on_config).
        In this hook, we instantiate our [`AutorefsExtension`][mkdocs_autorefs.references.AutorefsExtension]
        and add it to the list of Markdown extensions used by `mkdocs`.

        Arguments:
            config: The MkDocs config object.

        Returns:
            The modified config.
        """
        log.debug("Adding AutorefsExtension to the list")
        config["markdown_extensions"].append(AutorefsExtension(self))
        return config

    def on_page_markdown(self, markdown: str, page: Page, **kwargs: Any) -> str:  # noqa: ARG002
        """Remember which page is the current one.

        Arguments:
            markdown: Input Markdown.
            page: The related MkDocs page instance.
            kwargs: Additional arguments passed by MkDocs.

        Returns:
            The same Markdown. We only use this hook to keep a reference to the current page URL,
                used during Markdown conversion by the anchor scanner tree processor.
        """
        self.current_page = page.url
        return markdown

    def on_page_content(self, html: str, page: Page, **kwargs: Any) -> str:  # noqa: ARG002
        """Map anchors to URLs.

        Hook for the [`on_page_content` event](https://www.mkdocs.org/user-guide/plugins/#on_page_content).
        In this hook, we map the IDs of every anchor found in the table of contents to the anchors absolute URLs.
        This mapping will be used later to fix unresolved reference of the form `[title][identifier]` or
        `[identifier][]`.

        Arguments:
            html: HTML converted from Markdown.
            page: The related MkDocs page instance.
            kwargs: Additional arguments passed by MkDocs.

        Returns:
            The same HTML. We only use this hook to map anchors to URLs.
        """
        if self.scan_toc:
            log.debug("Mapping identifiers to URLs for page %s", page.file.src_path)
            for item in page.toc.items:
                self.map_urls(page.url, item)
        return html

    def map_urls(self, base_url: str, anchor: AnchorLink) -> None:
        """Recurse on every anchor to map its ID to its absolute URL.

        This method populates `self._primary_url_map` by side-effect.

        Arguments:
            base_url: The base URL to use as a prefix for each anchor's relative URL.
            anchor: The anchor to process and to recurse on.
        """
        self.register_anchor(base_url, anchor.id, primary=True)
        for child in anchor.children:
            self.map_urls(base_url, child)

    def on_post_page(self, output: str, page: Page, **kwargs: Any) -> str:  # noqa: ARG002
        """Fix cross-references.

        Hook for the [`on_post_page` event](https://www.mkdocs.org/user-guide/plugins/#on_post_page).
        In this hook, we try to fix unresolved references of the form `[title][identifier]` or `[identifier][]`.
        Doing that allows the user of `autorefs` to cross-reference objects in their documentation strings.
        It uses the native Markdown syntax so it's easy to remember and use.

        We log a warning for each reference that we couldn't map to an URL, but try to be smart and ignore identifiers
        that do not look legitimate (sometimes documentation can contain strings matching
        our [`AUTO_REF_RE`][mkdocs_autorefs.references.AUTO_REF_RE] regular expression that did not intend to reference anything).
        We currently ignore references when their identifier contains a space or a slash.

        Arguments:
            output: HTML converted from Markdown.
            page: The related MkDocs page instance.
            kwargs: Additional arguments passed by MkDocs.

        Returns:
            Modified HTML.
        """
        log.debug("Fixing references in page %s", page.file.src_path)

        # YORE: Bump 2: Replace `, fallback=self.get_fallback_anchor` with `` within line.
        url_mapper = functools.partial(self.get_item_url, from_url=page.url, fallback=self.get_fallback_anchor)
        # YORE: Bump 2: Replace `, _legacy_refs=self.legacy_refs` with `` within line.
        fixed_output, unmapped = fix_refs(output, url_mapper, _legacy_refs=self.legacy_refs)

        if unmapped and log.isEnabledFor(logging.WARNING):
            for ref, context in unmapped:
                message = f"from {context.filepath}:{context.lineno}: ({context.origin}) " if context else ""
                log.warning(f"{page.file.src_path}: {message}Could not find cross-reference target '{ref}'")

        return fixed_output
