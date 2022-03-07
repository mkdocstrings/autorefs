# mkdocs-autorefs

[![ci](https://github.com/mkdocstrings/autorefs/workflows/ci/badge.svg)](https://github.com/mkdocstrings/autorefs/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://mkdocstrings.github.io/autorefs/)
[![pypi version](https://img.shields.io/pypi/v/mkdocs-autorefs.svg)](https://pypi.org/project/mkdocs-autorefs/)
[![Anaconda-Server Badge](https://img.shields.io/conda/vn/conda-forge/mkdocs-autorefs.svg)](https://anaconda.org/conda-forge/mkdocs-autorefs)
[![gitpod](https://img.shields.io/badge/gitpod-workspace-blue.svg?style=flat)](https://gitpod.io/#https://github.com/mkdocstrings/autorefs)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://gitter.im/autorefs/community)

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

Note that this plugin's behavior is undefined when trying to link to a heading title that appears several times throughout the site. Currently it arbitrarily chooses one of the pages.

## Requirements

mkdocs-autorefs requires Python 3.7 or above.

<details>
<summary>To install Python 3.7, I recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>

```bash
# install pyenv
git clone https://github.com/pyenv/pyenv ~/.pyenv

# setup pyenv (you should also put these three lines in .bashrc or similar)
export PATH="${HOME}/.pyenv/bin:${PATH}"
export PYENV_ROOT="${HOME}/.pyenv"
eval "$(pyenv init -)"

# install Python 3.7
pyenv install 3.7.12

# make it available globally
pyenv global system 3.7.12
```
</details>
