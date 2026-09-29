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

"""mkdocs-autorefs package.

Automatically link across pages in MkDocs.
"""

from __future__ import annotations

from mkdocs_autorefs._internal.backlinks import Backlink, BacklinkCrumb, BacklinksTreeProcessor
from mkdocs_autorefs._internal.plugin import AutorefsConfig, AutorefsPlugin
from mkdocs_autorefs._internal.references import (
    AUTO_REF_RE,
    AUTOREF_RE,
    AnchorScannerTreeProcessor,
    AutorefsExtension,
    AutorefsHookInterface,
    AutorefsInlineProcessor,
    HeadingScannerTreeProcessor,
    fix_ref,
    fix_refs,
    relative_url,
)

__all__: list[str] = [
    "AUTOREF_RE",
    "AUTO_REF_RE",
    "AnchorScannerTreeProcessor",
    "AutorefsConfig",
    "AutorefsExtension",
    "AutorefsHookInterface",
    "AutorefsInlineProcessor",
    "AutorefsPlugin",
    "Backlink",
    "BacklinkCrumb",
    "BacklinksTreeProcessor",
    "HeadingScannerTreeProcessor",
    "fix_ref",
    "fix_refs",
    "relative_url",
]
