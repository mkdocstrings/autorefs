"""Cross-references module."""

from __future__ import annotations

import logging
import re
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from html import escape, unescape
from html.parser import HTMLParser
from typing import TYPE_CHECKING, Any, Callable, ClassVar
from urllib.parse import urlsplit
from xml.etree.ElementTree import Element

from markdown.core import Markdown
from markdown.extensions import Extension
from markdown.extensions.toc import slugify
from markdown.inlinepatterns import REFERENCE_RE, ReferenceInlineProcessor
from markdown.treeprocessors import Treeprocessor
from markdown.util import HTML_PLACEHOLDER_RE, INLINE_PLACEHOLDER_RE
from markupsafe import Markup

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path
    from re import Match

    from markdown import Markdown

    from mkdocs_autorefs.plugin import AutorefsPlugin

try:
    from mkdocs.plugins import get_plugin_logger

    log = get_plugin_logger(__name__)
except ImportError:
    # TODO: remove once support for MkDocs <1.5 is dropped
    log = logging.getLogger(f"mkdocs.plugins.{__name__}")  # type: ignore[assignment]


# YORE: Bump 2: Remove block.
def __getattr__(name: str) -> Any:
    if name == "AutoRefInlineProcessor":
        warnings.warn("AutoRefInlineProcessor was renamed AutorefsInlineProcessor", DeprecationWarning, stacklevel=2)
        return AutorefsInlineProcessor
    raise AttributeError(f"module 'mkdocs_autorefs.references' has no attribute {name}")


_ATTR_VALUE = r'"[^"<>]+"|[^"<> ]+'  # Possibly with double quotes around

# YORE: Bump 2: Remove block.
AUTO_REF_RE = re.compile(
    rf"<span data-(?P<kind>autorefs-(?:identifier|optional|optional-hover))=(?P<identifier>{_ATTR_VALUE})"
    rf"(?: class=(?P<class>{_ATTR_VALUE}))?(?P<attrs> [^<>]+)?>(?P<title>.*?)</span>",
    flags=re.DOTALL,
)
"""Deprecated. Use [`AUTOREF_RE`][mkdocs_autorefs.references.AUTOREF_RE] instead."""

AUTOREF_RE = re.compile(r"<autoref (?P<attrs>.*?)>(?P<title>.*?)</autoref>", flags=re.DOTALL)
"""The autoref HTML tag regular expression.

A regular expression to match mkdocs-autorefs' special reference markers
in the [`on_post_page` hook][mkdocs_autorefs.plugin.AutorefsPlugin.on_post_page].
"""


class AutorefsHookInterface(ABC):
    """An interface for hooking into how AutoRef handles inline references."""

    @dataclass
    class Context:
        """The context around an auto-reference."""

        domain: str
        role: str
        origin: str
        filepath: str | Path
        lineno: int

        def as_dict(self) -> dict[str, str]:
            """Convert the context to a dictionary of HTML attributes."""
            return {
                "domain": self.domain,
                "role": self.role,
                "origin": self.origin,
                "filepath": str(self.filepath),
                "lineno": str(self.lineno),
            }

    @abstractmethod
    def expand_identifier(self, identifier: str) -> str:
        """Expand an identifier in a given context.

        Parameters:
            identifier: The identifier to expand.

        Returns:
            The expanded identifier.
        """
        raise NotImplementedError

    @abstractmethod
    def get_context(self) -> AutorefsHookInterface.Context:
        """Get the current context.

        Returns:
            The current context.
        """
        raise NotImplementedError


class AutorefsInlineProcessor(ReferenceInlineProcessor):
    """A Markdown extension to handle inline references."""

    name: str = "mkdocs-autorefs"
    hook: AutorefsHookInterface | None = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D107
        super().__init__(REFERENCE_RE, *args, **kwargs)

    # Code based on
    # https://github.com/Python-Markdown/markdown/blob/8e7528fa5c98bf4652deb13206d6e6241d61630b/markdown/inlinepatterns.py#L780
    def handleMatch(self, m: Match[str], data: str) -> tuple[Element | None, int | None, int | None]:  # type: ignore[override]  # noqa: N802
        """Handle an element that matched.

        Arguments:
            m: The match object.
            data: The matched data.

        Returns:
            A new element or a tuple.
        """
        text, index, handled = self.getText(data, m.end(0))
        if not handled:
            return None, None, None

        identifier, slug, end, handled = self._eval_id(data, index, text)
        if not handled or identifier is None:
            return None, None, None

        if slug is None and re.search(r"[\x00-\x1f]", identifier):
            # Do nothing if the matched reference still contains control characters (from 0 to 31 included)
            # that weren't unstashed when trying to compute a slug of the title.
            return None, m.start(0), end

        return self._make_tag(identifier, text, slug=slug), m.start(0), end

    def _unstash(self, identifier: str) -> str:
        stashed_nodes: dict[str, Element | str] = self.md.treeprocessors["inline"].stashed_nodes  # type: ignore[attr-defined]

        def _repl(match: Match) -> str:
            el = stashed_nodes.get(match[1])
            if isinstance(el, Element):
                return f"`{''.join(el.itertext())}`"
            if el == "\x0296\x03":
                return "`"
            return str(el)

        return INLINE_PLACEHOLDER_RE.sub(_repl, identifier)

    def _eval_id(self, data: str, index: int, text: str) -> tuple[str | None, str | None, int, bool]:
        """Evaluate the id portion of `[ref][id]`.

        If `[ref][]` use `[ref]`.

        Arguments:
            data: The data to evaluate.
            index: The starting position.
            text: The text to use when no identifier.

        Returns:
            A tuple containing the identifier, its optional slug, its end position, and whether it matched.
        """
        m = self.RE_LINK.match(data, pos=index)
        if not m:
            return None, None, index, False

        if identifier := m.group(1):
            # An identifier was provided, match it exactly (later).
            slug = None
        else:
            # Only a title was provided, use it as identifier.
            identifier = text

            # Catch single stash entries, like the result of [`Foo`][].
            if match := INLINE_PLACEHOLDER_RE.fullmatch(identifier):
                stashed_nodes: dict[str, Element | str] = self.md.treeprocessors["inline"].stashed_nodes  # type: ignore[attr-defined]
                el = stashed_nodes.get(match[1])
                if isinstance(el, Element) and el.tag == "code":
                    # The title was wrapped in backticks, we only keep the content,
                    # and tell autorefs to match the identifier exactly.
                    identifier = "".join(el.itertext())
                    slug = None
                    # Special case: allow pymdownx.inlinehilite raw <code> snippets but strip them back to unhighlighted.
                    if match := HTML_PLACEHOLDER_RE.fullmatch(identifier):
                        stash_index = int(match.group(1))
                        html = self.md.htmlStash.rawHtmlBlocks[stash_index]
                        identifier = Markup(html).striptags()
                        self.md.htmlStash.rawHtmlBlocks[stash_index] = escape(identifier)

            # In any other case, unstash the title and slugify it.
            # Examples: ``[`Foo` and `Bar`]``, `[The *Foo*][]`.
            else:
                identifier = self._unstash(identifier)
                slug = slugify(identifier, separator="-")

        end = m.end(0)
        return identifier, slug, end, True

    def _make_tag(self, identifier: str, text: str, *, slug: str | None = None) -> Element:
        """Create a tag that can be matched by `AUTO_REF_RE`.

        Arguments:
            identifier: The identifier to use in the HTML property.
            text: The text to use in the HTML tag.

        Returns:
            A new element.
        """
        el = Element("autoref")
        if self.hook:
            identifier = self.hook.expand_identifier(identifier)
            el.attrib.update(self.hook.get_context().as_dict())
        el.set("identifier", identifier)
        el.text = text
        if slug:
            el.attrib["slug"] = slug
        return el


def relative_url(url_a: str, url_b: str) -> str:
    """Compute the relative path from URL A to URL B.

    Arguments:
        url_a: URL A.
        url_b: URL B.

    Returns:
        The relative URL to go from A to B.
    """
    parts_a = url_a.split("/")
    url_b, anchor = url_b.split("#", 1)
    parts_b = url_b.split("/")

    # remove common left parts
    while parts_a and parts_b and parts_a[0] == parts_b[0]:
        parts_a.pop(0)
        parts_b.pop(0)

    # go up as many times as remaining a parts' depth
    levels = len(parts_a) - 1
    parts_relative = [".."] * levels + parts_b
    relative = "/".join(parts_relative)
    return f"{relative}#{anchor}"


# YORE: Bump 2: Remove block.
def _legacy_fix_ref(
    url_mapper: Callable[[str], str],
    unmapped: list[tuple[str, AutorefsHookInterface.Context | None]],
) -> Callable:
    """Return a `repl` function for [`re.sub`](https://docs.python.org/3/library/re.html#re.sub).

    In our context, we match Markdown references and replace them with HTML links.

    When the matched reference's identifier was not mapped to an URL, we append the identifier to the outer
    `unmapped` list. It generally means the user is trying to cross-reference an object that was not collected
    and rendered, making it impossible to link to it. We catch this exception in the caller to issue a warning.

    Arguments:
        url_mapper: A callable that gets an object's site URL by its identifier,
            such as [mkdocs_autorefs.plugin.AutorefsPlugin.get_item_url][].
        unmapped: A list to store unmapped identifiers.

    Returns:
        The actual function accepting a [`Match` object](https://docs.python.org/3/library/re.html#match-objects)
        and returning the replacement strings.
    """

    def inner(match: Match) -> str:
        identifier = match["identifier"].strip('"')
        title = match["title"]
        kind = match["kind"]
        attrs = match["attrs"] or ""
        classes = (match["class"] or "").strip('"').split()

        try:
            url = url_mapper(unescape(identifier))
        except KeyError:
            if kind == "autorefs-optional":
                return title
            if kind == "autorefs-optional-hover":
                return f'<span title="{identifier}">{title}</span>'
            unmapped.append((identifier, None))
            if title == identifier:
                return f"[{identifier}][]"
            return f"[{title}][{identifier}]"

        warnings.warn(
            "autorefs `span` elements are deprecated in favor of `autoref` elements: "
            f'`<span data-autorefs-identifier="{identifier}">...</span>` becomes `<autoref identifer="{identifier}">...</autoref>`',
            DeprecationWarning,
            stacklevel=1,
        )
        parsed = urlsplit(url)
        external = parsed.scheme or parsed.netloc
        classes = ["autorefs", "autorefs-external" if external else "autorefs-internal", *classes]
        class_attr = " ".join(classes)
        if kind == "autorefs-optional-hover":
            return f'<a class="{class_attr}" title="{identifier}" href="{escape(url)}"{attrs}>{title}</a>'
        return f'<a class="{class_attr}" href="{escape(url)}"{attrs}>{title}</a>'

    return inner


class _AutorefsAttrs(dict):
    _handled_attrs: ClassVar[set[str]] = {
        "identifier",
        "optional",
        "hover",
        "class",
        "domain",
        "role",
        "origin",
        "filepath",
        "lineno",
        "slug",
    }

    @property
    def context(self) -> AutorefsHookInterface.Context | None:
        try:
            return AutorefsHookInterface.Context(
                domain=self["domain"],
                role=self["role"],
                origin=self["origin"],
                filepath=self["filepath"],
                lineno=int(self["lineno"]),
            )
        except KeyError:
            return None

    @property
    def remaining(self) -> str:
        return " ".join(k if v is None else f'{k}="{v}"' for k, v in self.items() if k not in self._handled_attrs)


class _HTMLAttrsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.attrs = {}

    def parse(self, html: str) -> _AutorefsAttrs:
        self.attrs.clear()
        self.feed(html)
        return _AutorefsAttrs(self.attrs)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:  # noqa: ARG002
        self.attrs.update(attrs)


_html_attrs_parser = _HTMLAttrsParser()


def _find_url(identifiers: Iterable[str], url_mapper: Callable[[str], str]) -> str:
    for identifier in identifiers:
        try:
            return url_mapper(identifier)
        except KeyError:
            pass
    raise KeyError(f"None of the identifiers {identifiers} were found")


def fix_ref(
    url_mapper: Callable[[str], str],
    unmapped: list[tuple[str, AutorefsHookInterface.Context | None]],
) -> Callable:
    """Return a `repl` function for [`re.sub`](https://docs.python.org/3/library/re.html#re.sub).

    In our context, we match Markdown references and replace them with HTML links.

    When the matched reference's identifier was not mapped to an URL, we append the identifier to the outer
    `unmapped` list. It generally means the user is trying to cross-reference an object that was not collected
    and rendered, making it impossible to link to it. We catch this exception in the caller to issue a warning.

    Arguments:
        url_mapper: A callable that gets an object's site URL by its identifier,
            such as [mkdocs_autorefs.plugin.AutorefsPlugin.get_item_url][].
        unmapped: A list to store unmapped identifiers.

    Returns:
        The actual function accepting a [`Match` object](https://docs.python.org/3/library/re.html#match-objects)
        and returning the replacement strings.
    """

    def inner(match: Match) -> str:
        title = match["title"]
        attrs = _html_attrs_parser.parse(f"<a {match['attrs']}>")
        identifier: str = attrs["identifier"]
        slug = attrs.get("slug", None)
        optional = "optional" in attrs
        hover = "hover" in attrs

        identifiers = (identifier, slug) if slug else (identifier,)

        try:
            url = _find_url(identifiers, url_mapper)
        except KeyError:
            if optional:
                log.debug("Unresolved optional cross-reference: %s", identifier)
                if hover:
                    return f'<span title="{identifier}">{title}</span>'
                return title
            unmapped.append((identifier, attrs.context))
            if title == identifier:
                return f"[{identifier}][]"
            if title == f"<code>{identifier}</code>" and not slug:
                return f"[<code>{identifier}</code>][]"
            return f"[{title}][{identifier}]"

        parsed = urlsplit(url)
        external = parsed.scheme or parsed.netloc
        classes = (attrs.get("class") or "").strip().split()
        classes = ["autorefs", "autorefs-external" if external else "autorefs-internal", *classes]
        class_attr = " ".join(classes)
        if remaining := attrs.remaining:
            remaining = f" {remaining}"
        if optional and hover:
            return f'<a class="{class_attr}" title="{identifier}" href="{escape(url)}"{remaining}>{title}</a>'
        return f'<a class="{class_attr}" href="{escape(url)}"{remaining}>{title}</a>'

    return inner


def fix_refs(
    html: str,
    url_mapper: Callable[[str], str],
    # YORE: Bump 2: Remove line.
    _legacy_refs: bool = True,  # noqa: FBT001, FBT002
) -> tuple[str, list[tuple[str, AutorefsHookInterface.Context | None]]]:
    """Fix all references in the given HTML text.

    Arguments:
        html: The text to fix.
        url_mapper: A callable that gets an object's site URL by its identifier,
            such as [mkdocs_autorefs.plugin.AutorefsPlugin.get_item_url][].

    Returns:
        The fixed HTML, and a list of unmapped identifiers (string and optional context).
    """
    unmapped: list[tuple[str, AutorefsHookInterface.Context | None]] = []
    html = AUTOREF_RE.sub(fix_ref(url_mapper, unmapped), html)

    # YORE: Bump 2: Remove block.
    if _legacy_refs:
        html = AUTO_REF_RE.sub(_legacy_fix_ref(url_mapper, unmapped), html)

    return html, unmapped


class AnchorScannerTreeProcessor(Treeprocessor):
    """Tree processor to scan and register HTML anchors."""

    name: str = "mkdocs-autorefs-anchors-scanner"
    _htags: ClassVar[set[str]] = {"h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self, plugin: AutorefsPlugin, md: Markdown | None = None) -> None:
        """Initialize the tree processor.

        Parameters:
            plugin: A reference to the autorefs plugin, to use its `register_anchor` method.
        """
        super().__init__(md)
        self.plugin = plugin

    def run(self, root: Element) -> None:  # noqa: D102
        if self.plugin.current_page is not None:
            pending_anchors = _PendingAnchors(self.plugin, self.plugin.current_page)
            self._scan_anchors(root, pending_anchors)
            pending_anchors.flush()

    def _scan_anchors(self, parent: Element, pending_anchors: _PendingAnchors) -> None:
        for el in parent:
            if el.tag == "a":
                # We found an anchor. Record its id if it has one.
                if anchor_id := el.get("id"):
                    pending_anchors.append(anchor_id)
                # If the element has text or a link, it's not an alias.
                # Non-whitespace text after the element interrupts the chain, aliases can't apply.
                if el.text or el.get("href") or (el.tail and el.tail.strip()):
                    pending_anchors.flush()

            elif el.tag == "p":
                # A `p` tag is a no-op for our purposes, just recurse into it in the context
                # of the current collection of anchors.
                self._scan_anchors(el, pending_anchors)
                # Non-whitespace text after the element interrupts the chain, aliases can't apply.
                if el.tail and el.tail.strip():
                    pending_anchors.flush()

            elif el.tag in self._htags:
                # If the element is a heading, that turns the pending anchors into aliases.
                pending_anchors.flush(el.get("id"))

            else:
                # But if it's some other interruption, flush anchors anyway as non-aliases.
                pending_anchors.flush()
                # Recurse into sub-elements, in a *separate* context.
                self.run(el)


class _PendingAnchors:
    """A collection of HTML anchors that may or may not become aliased to an upcoming heading."""

    def __init__(self, plugin: AutorefsPlugin, current_page: str):
        self.plugin = plugin
        self.current_page = current_page
        self.anchors: list[str] = []

    def append(self, anchor: str) -> None:
        self.anchors.append(anchor)

    def flush(self, alias_to: str | None = None) -> None:
        for anchor in self.anchors:
            self.plugin.register_anchor(self.current_page, anchor, alias_to, primary=True)
        self.anchors.clear()


@lru_cache
def _log_enabling_markdown_anchors() -> None:
    log.debug("Enabling Markdown anchors feature")


class AutorefsExtension(Extension):
    """Markdown extension that transforms unresolved references into auto-references.

    Auto-references are then resolved later by the MkDocs plugin.

    This extension also scans Markdown anchors (`[](){#some-id}`)
    to register them with the MkDocs plugin.
    """

    def __init__(
        self,
        plugin: AutorefsPlugin | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the Markdown extension.

        Parameters:
            plugin: An optional reference to the autorefs plugin (to pass it to the anchor scanner tree processor).
            **kwargs: Keyword arguments passed to the [base constructor][markdown.extensions.Extension].
        """
        super().__init__(**kwargs)
        self.plugin = plugin

    def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802 (casing: parent method's name)
        """Register the extension.

        Add an instance of our [`AutorefsInlineProcessor`][mkdocs_autorefs.references.AutorefsInlineProcessor] to the Markdown parser.
        Also optionally add an instance of our [`AnchorScannerTreeProcessor`][mkdocs_autorefs.references.AnchorScannerTreeProcessor]
        to the Markdown parser if a reference to the autorefs plugin was passed to this extension.

        Arguments:
            md: A `markdown.Markdown` instance.
        """
        md.inlinePatterns.register(
            AutorefsInlineProcessor(md),
            AutorefsInlineProcessor.name,
            priority=168,  # Right after markdown.inlinepatterns.ReferenceInlineProcessor
        )
        if self.plugin is not None and self.plugin.scan_toc and "attr_list" in md.treeprocessors:
            _log_enabling_markdown_anchors()
            md.treeprocessors.register(
                AnchorScannerTreeProcessor(self.plugin, md),
                AnchorScannerTreeProcessor.name,
                priority=0,
            )
