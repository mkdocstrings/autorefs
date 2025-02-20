"""Helper functions for the tests."""

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File
from mkdocs.structure.pages import Page


def create_page(url: str) -> Page:
    """Create a page with the given URL."""
    return Page(
        title=url,
        file=File(url, "docs", "site", use_directory_urls=False),
        config=MkDocsConfig(),
    )
