# mkdocs-autorefs

[![ci](https://github.com/mkdocstrings/autorefs/workflows/ci/badge.svg)](https://github.com/mkdocstrings/autorefs/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://mkdocstrings.github.io/autorefs/)
[![pypi version](https://img.shields.io/pypi/v/mkdocs-autorefs.svg)](https://pypi.org/project/mkdocs-autorefs/)
[![conda version](https://img.shields.io/conda/vn/conda-forge/mkdocs-autorefs.svg)](https://anaconda.org/conda-forge/mkdocs-autorefs)
[![gitpod](https://img.shields.io/badge/gitpod-workspace-blue.svg?style=flat)](https://gitpod.io/#https://github.com/mkdocstrings/autorefs)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://app.gitter.im/#/room/#autorefs:gitter.im)

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

Linking to a heading without needing to know the destination page can be useful if specifying that path is cumbersome, e.g. when the pages have deeply nested paths, are far apart, or are moved around frequently. And the issue is somewhat exacerbated by the fact that [MkDocs supports only *relative* links between pages](https://github.com/mkdocs/mkdocs/issues/1592).

Note that this plugin's behavior is undefined when trying to link to a heading title that appears several times throughout the site. Currently it arbitrarily chooses one of the pages. In such cases, use [Markdown anchors](#markdown-anchors) to add unique aliases to your headings.

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

Check out the [paragraph about foobar][foobar-pararaph].
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
