"""Helper functions for the tests."""

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File
from mkdocs.structure.pages import Page
from mkdocs.structure.toc import AnchorLink


def create_page(url: str) -> Page:
    """Create a page with the given URL."""
    return Page(
        title=url,
        file=File(url, "docs", "site", use_directory_urls=False),
        config=MkDocsConfig(),
    )


def create_anchor_link(title: str, anchor_id: str, level: int = 1) -> AnchorLink:
    """Create an anchor link."""
    return AnchorLink(
        title=title,
        id=anchor_id,
        level=level,
    )
