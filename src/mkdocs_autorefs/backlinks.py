"""Backlinks module."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from markdown.core import Markdown
from markdown.treeprocessors import Treeprocessor

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from markdown import Markdown

    from mkdocs_autorefs.plugin import AutorefsPlugin

try:
    from mkdocs.plugins import get_plugin_logger

    log = get_plugin_logger(__name__)
except ImportError:
    # TODO: remove once support for MkDocs <1.5 is dropped
    log = logging.getLogger(f"mkdocs.plugins.{__name__}")  # type: ignore[assignment]


@dataclass(eq=True, frozen=True, order=True)
class BacklinkCrumb:
    """A navigation breadcrumb for a backlink."""

    title: str
    url: str


@dataclass(eq=True, frozen=True, order=True)
class Backlink:
    """A backlink (list of breadcrumbs)."""

    crumbs: tuple[BacklinkCrumb, ...]


class BacklinksTreeProcessor(Treeprocessor):
    """Enhance autorefs with `backlink-type` and `backlink-anchor` attributes.

    These attributes are then used later to register backlinks.
    """

    name: str = "mkdocs-autorefs-backlinks"
    initial_id: str | None = None
    _htags: ClassVar[set[str]] = {"h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self, plugin: AutorefsPlugin, md: Markdown | None = None) -> None:
        """Initialize the tree processor.

        Parameters:
            plugin: A reference to the autorefs plugin, to use its `register_anchor` method.
        """
        super().__init__(md)
        self.plugin = plugin
        self.last_heading_id: str | None = None

    def run(self, root: Element) -> None:  # noqa: D102
        if self.plugin.current_page is not None:
            self.last_heading_id = self.initial_id
            self._enhance_autorefs(root)

    def _enhance_autorefs(self, parent: Element) -> None:
        for el in parent:
            if el.tag == "a":  # Markdown anchor.
                if not (el.text or el.get("href") or (el.tail and el.tail.strip())) and (anchor_id := el.get("id")):
                    self.last_heading_id = anchor_id
            elif el.tag in self._htags:  # Heading.
                self.last_heading_id = el.get("id")
            elif el.tag == "autoref":
                if "backlink-type" not in el.attrib:
                    el.set("backlink-type", "referenced-by")
                if "backlink-anchor" not in el.attrib and self.last_heading_id:
                    el.set("backlink-anchor", self.last_heading_id)
            else:
                self._enhance_autorefs(el)
