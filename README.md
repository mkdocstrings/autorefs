# mkdocs-autorefs

[![ci](https://github.com/mkdocstrings/autorefs/workflows/ci/badge.svg)](https://github.com/mkdocstrings/autorefs/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://mkdocstrings.github.io/autorefs/)
[![pypi version](https://img.shields.io/pypi/v/mkdocs-autorefs.svg)](https://pypi.org/project/mkdocs-autorefs/)
[![conda version](https://img.shields.io/conda/vn/conda-forge/mkdocs-autorefs.svg)](https://anaconda.org/conda-forge/mkdocs-autorefs)
[![gitpod](https://img.shields.io/badge/gitpod-workspace-708FCC.svg?style=flat)](https://gitpod.io/#https://github.com/mkdocstrings/autorefs)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://app.gitter.im/#/room/#mkdocstrings/autorefs:gitter.im)

Automatically link across pages in MkDocs.

## Installation

With `pip`:

```bash
python3 -m pip install mkdocs-autorefs
```

## Usage

```yaml
# mkdocs.yml
plugins:
  - search
  - autorefs
```

In one of your Markdown files (e.g. `doc1.md`) create some headings:

```markdown
## Hello, world!

## Another heading

Link to [Hello, World!](#hello-world) on the same page.
```

This is a [*normal* link to an anchor](https://www.mkdocs.org/user-guide/writing-your-docs/#linking-to-pages). MkDocs generates anchors for each heading, and they can always be used to link to something, either within the same page (as shown here) or by specifying the path of the other page.

But with this plugin, you can **link to a heading from any other page** on the site *without* needing to know the path of either of the pages, just the heading title itself.  
Let's create another Markdown page to try this, `subdir/doc2.md`:

```markdown
We can [link to that heading][hello-world] from another page too.

This works the same as [a normal link to that heading](../doc1.md#hello-world).
```

Linking to a heading without needing to know the destination page can be useful if specifying that path is cumbersome, e.g. when the pages have deeply nested paths, are far apart, or are moved around frequently.

### Non-unique headings

When linking to a heading that appears several times throughout the site, this plugin will log a warning message stating that multiple URLs were found and that headings should be made unique, and will resolve the link using the first found URL.

To prevent getting warnings, use [Markdown anchors](#markdown-anchors) to add unique aliases to your headings, and use these aliases when referencing the headings.

If you cannot use Markdown anchors, for example because you inject the same generated contents in multiple locations (for example mkdocstrings' API documentation), then you can try to alleviate the warnings by enabling the `resolve_closest` option:

```yaml
plugins:
- autorefs:
    resolve_closest: true
```

When `resolve_closest` is enabled, and multiple URLs are found for the same identifier, the plugin will try to resolve to the one that is "closest" to the current page (the page containing the link). By closest, we mean:

- URLs that are relative to the current page's URL, climbing up parents
- if multiple URLs are relative to it, use the one at the shortest distance if possible.

If multiple relative URLs are at the same distance, the first of these URLs will be used. If no URL is relative to the current page's URL, the first URL of all found URLs will be used.

Examples:

Current page | Candidate URLs | Relative URLs | Winner
------------ | -------------- | ------------- | ------
` ` | `x/#b`, `#b` | `#b` | `#b` (only one relative)
`a/` | `b/c/#d`, `c/#d` | none | `b/c/#d` (no relative, use first one, even if longer distance)
`a/b/` | `x/#e`, `a/c/#e`, `a/d/#e` | `a/c/#e`, `a/d/#e` (relative to parent `a/`) | `a/c/#e` (same distance, use first one)
`a/b/` | `x/#e`, `a/c/d/#e`, `a/c/#e` | `a/c/d/#e`, `a/c/#e` (relative to parent `a/`) | `a/c/#e` (shortest distance)
`a/b/c/` | `x/#e`, `a/#e`, `a/b/#e`, `a/b/c/d/#e`, `a/b/c/#e` | `a/b/c/d/#e`, `a/b/c/#e` | `a/b/c/#e` (shortest distance)

### Markdown anchors

The autorefs plugin offers a feature called "Markdown anchors". Such anchors can be added anywhere in a document, and linked to from any other place.

The syntax is:

```md
[](){#id-of-the-anchor}
```

If you look closely, it starts with the usual syntax for a link, `[]()`, except both the text value and URL of the link are empty. Then we see `{#id-of-the-anchor}`, which is the syntax supported by the [`attr_list`](https://python-markdown.github.io/extensions/attr_list/) extension. It sets an HTML id to the anchor element. The autorefs plugin simply gives a meaning to such anchors with ids. Note that raw HTML anchors like `<a id="foo"></a>` are not supported.

The `attr_list` extension must be enabled for the Markdown anchors feature to work:

```yaml
# mkdocs.yml
plugins:
  - search
  - autorefs

markdown_extensions:
  - attr_list
```

Now, you can add anchors to documents:

```md
Somewhere in a document.

[](){#foobar-paragraph}

Paragraph about foobar.
```

...making it possible to link to this anchor with our automatic links:

```md
In any document.

Check out the [paragraph about foobar][foobar-paragraph].
```

If you add a Markdown anchor right above a heading, this anchor will redirect to the heading itself:

```md
[](){#foobar}
## A verbose title about foobar
```

Linking to the `foobar` anchor will bring you directly to the heading, not the anchor itself, so the URL will show `#a-verbose-title-about-foobar` instead of `#foobar`. These anchors therefore act as "aliases" for headings. It is possible to define multiple aliases per heading:

```md
[](){#contributing}
[](){#development-setup}
## How to contribute to the project?
```

Such aliases are especially useful when the same headings appear in several different pages. Without aliases, linking to the heading is undefined behavior (it could lead to any one of the headings). With unique aliases above headings, you can make sure to link to the right heading.

For example, consider the following setup. You have one document per operating system describing how to install a project with the OS package manager or from sources:

```tree
docs/
  install/
    arch.md
    debian.md
    gentoo.md
```

Each page has:

```md
## Install with package manager
...

## Install from sources
...
```

You don't want to change headings and make them redundant, like `## Arch: Install with package manager` and `## Debian: Install with package manager` just to be able to reference the right one with autorefs. Instead you can do this:

```md
[](){#arch-install-pkg}
## Install with package manager
...

[](){#arch-install-src}
## Install from sources
...
```

...changing `arch` by `debian`, `gentoo`, etc. in the other pages.

---

You can also change the actual identifier of a heading, thanks again to the `attr_list` Markdown extension:

```md
## Install from sources { #arch-install-src }
...
```

...though note that this will impact the URL anchor too (and therefore the permalink to the heading).
