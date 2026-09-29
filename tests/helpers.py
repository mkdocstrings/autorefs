# SPDX-License-Identifier: ISC
#
# ISC License
#
# Copyright (c) 2019, Timothée Mazzucotelli, Oleh Prypin and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

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
        config=MkDocsConfig(),  # ty:ignore[invalid-argument-type]
    )


def create_anchor_link(title: str, anchor_id: str, level: int = 1) -> AnchorLink:
    """Create an anchor link."""
    return AnchorLink(
        title=title,
        id=anchor_id,
        level=level,
    )
