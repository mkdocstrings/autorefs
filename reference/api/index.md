# mkdocs_autorefs

mkdocs-autorefs package.

Automatically link across pages in MkDocs.

Modules:

- **`plugin`** – Deprecated. Import from 'mkdocs_autorefs' instead.
- **`references`** – Deprecated. Import from 'mkdocs_autorefs' instead.

Classes:

- **`AnchorScannerTreeProcessor`** – Tree processor to scan and register HTML anchors.
- **`AutorefsConfig`** – Configuration options for the autorefs plugin.
- **`AutorefsExtension`** – Markdown extension that transforms unresolved references into auto-references.
- **`AutorefsHookInterface`** – An interface for hooking into how AutoRef handles inline references.
- **`AutorefsInlineProcessor`** – A Markdown extension to handle inline references.
- **`AutorefsPlugin`** – The autorefs plugin for mkdocs.
- **`Backlink`** – A backlink (list of breadcrumbs).
- **`BacklinkCrumb`** – A navigation breadcrumb for a backlink.
- **`BacklinksTreeProcessor`** – Enhance autorefs with backlink-type and backlink-anchor attributes.

Functions:

- **`fix_ref`** – Return a repl function for re.sub.
- **`fix_refs`** – Fix all references in the given HTML text.
- **`relative_url`** – Compute the relative path from URL A to URL B.

Attributes:

- **`AUTOREF_RE`** – The autoref HTML tag regular expression.
- **`AUTO_REF_RE`** – Deprecated. Use AUTOREF_RE instead.

## AUTOREF_RE

```
AUTOREF_RE = compile(
    "<autoref (?P<attrs>.*?)>(?P<title>.*?)</autoref>",
    flags=DOTALL,
)

```

The autoref HTML tag regular expression.

A regular expression to match mkdocs-autorefs' special reference markers in the on_env hook.

## AUTO_REF_RE

```
AUTO_REF_RE = compile(
    f"<span data-(?P<kind>autorefs-(?:identifier|optional|optional-hover))=(?P<identifier>{_ATTR_VALUE})(?: class=(?P<class>{_ATTR_VALUE}))?(?P<attrs> [^<>]+)?>(?P<title>.*?)</span>",
    flags=DOTALL,
)

```

Deprecated. Use AUTOREF_RE instead.

## AnchorScannerTreeProcessor

```
AnchorScannerTreeProcessor(
    plugin: AutorefsPlugin, md: Markdown | None = None
)

```

Bases: `Treeprocessor`

Tree processor to scan and register HTML anchors.

Parameters:

- **`plugin`** (`AutorefsPlugin`) – A reference to the autorefs plugin, to use its register_anchor method.

Methods:

- **`run`** – Run the tree processor.

Attributes:

- **`name`** (`str`) – The name of the tree processor.

Source code in `src/mkdocs_autorefs/_internal/references.py`

```
def __init__(self, plugin: AutorefsPlugin, md: Markdown | None = None) -> None:
    """Initialize the tree processor.

    Parameters:
        plugin: A reference to the autorefs plugin, to use its `register_anchor` method.
    """
    super().__init__(md)
    self._plugin = plugin

```

### name

```
name: str = 'mkdocs-autorefs-anchors-scanner'

```

The name of the tree processor.

### run

```
run(root: Element) -> None

```

Run the tree processor.

Parameters:

- **`root`** (`Element`) – The root element of the tree.

Source code in `src/mkdocs_autorefs/_internal/references.py`

```
def run(self, root: Element) -> None:
    """Run the tree processor.

    Arguments:
        root: The root element of the tree.
    """
    if self._plugin.current_page is not None:
        pending_anchors = _PendingAnchors(self._plugin)
        self._scan_anchors(root, pending_anchors)
        pending_anchors.flush()

```

## AutorefsConfig

Bases: `Config`

Configuration options for the `autorefs` plugin.

Attributes:

- **`link_titles`** (`bool | Literal['auto', 'external']`) – Whether to set titles on links.
- **`resolve_closest`** (`bool`) – Whether to resolve an autoref to the closest URL when multiple URLs are found for an identifier.
- **`strip_title_tags`** (`bool | Literal['auto']`) – Whether to strip HTML tags from link titles.

### link_titles

```
link_titles: bool | Literal["auto", "external"] = Choice(
    (True, False, "auto", "external"), default="auto"
)

```

Whether to set titles on links.

Such title attributes are displayed as tooltips when hovering over the links.

- `"auto"`: autorefs will detect whether the instant preview feature of Material for MkDocs is enabled, and set titles on external links when it is, all links if it is not.
- `"external"`: autorefs will set titles on external links only.
- `True`: autorefs will set titles on all links.
- `False`: autorefs will not set any title attributes on links.

Titles are only set when they are different from the link's text. Titles are constructed from the linked heading's original title, optionally appending the identifier for API objects.

### resolve_closest

```
resolve_closest: bool = Type(bool, default=False)

```

Whether to resolve an autoref to the closest URL when multiple URLs are found for an identifier.

By closest, we mean a combination of "relative to the current page" and "shortest distance from the current page".

For example, if you link to identifier `hello` from page `foo/bar/`, and the identifier is found in `foo/`, `foo/baz/` and `foo/bar/baz/qux/` pages, autorefs will resolve to `foo/bar/baz/qux`, which is the only URL relative to `foo/bar/`.

If multiple URLs are equally close, autorefs will resolve to the first of these equally close URLs. If autorefs cannot find any URL that is close to the current page, it will log a warning and resolve to the first URL found.

When false and multiple URLs are found for an identifier, autorefs will log a warning and resolve to the first URL.

### strip_title_tags

```
strip_title_tags: bool | Literal["auto"] = Choice(
    (True, False, "auto"), default="auto"
)

```

Whether to strip HTML tags from link titles.

Some themes support HTML in link titles, but others do not.

- `"auto"`: strip tags unless the Material for MkDocs theme is detected.

## AutorefsExtension

```
AutorefsExtension(
    plugin: AutorefsPlugin | None = None, **kwargs: Any
)

```

Bases: `Extension`

Markdown extension that transforms unresolved references into auto-references.

Auto-references are then resolved later by the MkDocs plugin.

This extension also scans Markdown anchors (`[](){#some-id}`) to register them with the MkDocs plugin.

Parameters:

- **`plugin`** (`AutorefsPlugin | None`, default: `None` ) – An optional reference to the autorefs plugin (to pass it to the anchor scanner tree processor).
- **`**kwargs`** (`Any`, default: `{}` ) – Keyword arguments passed to the base constructor.

Methods:

- **`extendMarkdown`** – Register the extension.

Attributes:

- **`plugin`** – A reference to the autorefs plugin.

Source code in `src/mkdocs_autorefs/_internal/references.py`

```
def __init__(
    self,
    plugin: AutorefsPlugin | None = None,
    **kwargs: Any,
) -> None:
    """Initialize the Markdown extension.

    Parameters:
        plugin: An optional reference to the autorefs plugin (to pass it to the anchor scanner tree processor).
        **kwargs: Keyword arguments passed to the [base constructor][markdown.Extension].
    """
    super().__init__(**kwargs)
    self.plugin = plugin
    """A reference to the autorefs plugin."""

```

### plugin

```
plugin = plugin

```

A reference to the autorefs plugin.

### extendMarkdown

```
extendMarkdown(md: Markdown) -> None

```

Register the extension.

Add an instance of our AutorefsInlineProcessor to the Markdown parser. Also optionally add an instance of our AnchorScannerTreeProcessor and BacklinksTreeProcessor to the Markdown parser if a reference to the autorefs plugin was passed to this extension.

Parameters:

- **`md`** (`Markdown`) – A markdown.Markdown instance.

Source code in `src/mkdocs_autorefs/_internal/references.py`

```
def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802 (casing: parent method's name)
    """Register the extension.

    Add an instance of our [`AutorefsInlineProcessor`][mkdocs_autorefs.AutorefsInlineProcessor] to the Markdown parser.
    Also optionally add an instance of our [`AnchorScannerTreeProcessor`][mkdocs_autorefs.AnchorScannerTreeProcessor]
    and [`BacklinksTreeProcessor`][mkdocs_autorefs.BacklinksTreeProcessor] to the Markdown parser
    if a reference to the autorefs plugin was passed to this extension.

    Arguments:
        md: A `markdown.Markdown` instance.
    """
    md.inlinePatterns.register(
        AutorefsInlineProcessor(md),
        AutorefsInlineProcessor.name,
        priority=168,  # Right after markdown.inlinepatterns.ReferenceInlineProcessor
    )
    if self.plugin is not None:
        # Markdown anchors require the `attr_list` extension.
        if self.plugin.scan_toc and "attr_list" in md.treeprocessors:
            _log_enabling_markdown_anchors()
            md.treeprocessors.register(
                AnchorScannerTreeProcessor(self.plugin, md),
                AnchorScannerTreeProcessor.name,
                priority=0,
            )
        # Backlinks require IDs on headings, which are either set by `toc`,
        # or manually by the user with `attr_list`.
        if self.plugin.record_backlinks and ("attr_list" in md.treeprocessors or "toc" in md.treeprocessors):
            _log_enabling_backlinks()
            md.treeprocessors.register(
                BacklinksTreeProcessor(self.plugin, md),
                BacklinksTreeProcessor.name,
                priority=0,
            )

```

## AutorefsHookInterface

Bases: `ABC`

An interface for hooking into how AutoRef handles inline references.

Classes:

- **`Context`** – The context around an auto-reference.

Methods:

- **`expand_identifier`** – Expand an identifier in a given context.
- **`get_context`** – Get the current context.

### Context

```
Context(
    domain: str,
    role: str,
    origin: str,
    filepath: str | Path,
    lineno: int,
)

```

The context around an auto-reference.

Methods:

- **`as_dict`** – Convert the context to a dictionary of HTML attributes.

Attributes:

- **`domain`** (`str`) – A domain like py or js.
- **`filepath`** (`str | Path`) – The path to the file containing the autoref.
- **`lineno`** (`int`) – The line number in the file containing the autoref.
- **`origin`** (`str`) – The origin of an autoref (an object identifier).
- **`role`** (`str`) – A role like class or function.

#### domain

```
domain: str

```

A domain like `py` or `js`.

#### filepath

```
filepath: str | Path

```

The path to the file containing the autoref.

#### lineno

```
lineno: int

```

The line number in the file containing the autoref.

#### origin

```
origin: str

```

The origin of an autoref (an object identifier).

#### role

```
role: str

```

A role like `class` or `function`.

#### as_dict

```
as_dict() -> dict[str, str]

```

Convert the context to a dictionary of HTML attributes.

Source code in `src/mkdocs_autorefs/_internal/references.py`

```
def as_dict(self) -> dict[str, str]:
    """Convert the context to a dictionary of HTML attributes."""
    return {
        "domain": self.domain,
        "role": self.role,
        "origin": self.origin,
        "filepath": str(self.filepath),
        "lineno": str(self.lineno),
    }

```

### expand_identifier

```
expand_identifier(identifier: str) -> str

```

Expand an identifier in a given context.

Parameters:

- **`identifier`** (`str`) – The identifier to expand.

Returns:

- `str` – The expanded identifier.

Source code in `src/mkdocs_autorefs/_internal/references.py`

```
@abstractmethod
def expand_identifier(self, identifier: str) -> str:
    """Expand an identifier in a given context.

    Parameters:
        identifier: The identifier to expand.

    Returns:
        The expanded identifier.
    """
    raise NotImplementedError

```

### get_context

```
get_context() -> Context

```

Get the current context.

Returns:

- `Context` – The current context.

Source code in `src/mkdocs_autorefs/_internal/references.py`

```
@abstractmethod
def get_context(self) -> AutorefsHookInterface.Context:
    """Get the current context.

    Returns:
        The current context.
    """
    raise NotImplementedError

```

## AutorefsInlineProcessor

```
AutorefsInlineProcessor(*args: Any, **kwargs: Any)

```

Bases: `ReferenceInlineProcessor`

A Markdown extension to handle inline references.

Methods:

- **`handleMatch`** – Handle an element that matched.

Attributes:

- **`hook`** (`AutorefsHookInterface | None`) – The hook to use for expanding identifiers or adding context to autorefs.
- **`name`** (`str`) – The name of the inline processor.

Source code in `src/mkdocs_autorefs/_internal/references.py`

```
def __init__(self, *args: Any, **kwargs: Any) -> None:
    super().__init__(REFERENCE_RE, *args, **kwargs)

```

### hook

```
hook: AutorefsHookInterface | None = None

```

The hook to use for expanding identifiers or adding context to autorefs.

### name

```
name: str = 'mkdocs-autorefs'

```

The name of the inline processor.

### handleMatch

```
handleMatch(
    m: Match[str], data: str
) -> tuple[Element | None, int | None, int | None]

```

Handle an element that matched.

Parameters:

- **`m`** (`Match[str]`) – The match object.
- **`data`** (`str`) – The matched data.

Returns:

- `tuple[Element | None, int | None, int | None]` – A new element or a tuple.

Source code in `src/mkdocs_autorefs/_internal/references.py`

```
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

```

## AutorefsPlugin

```
AutorefsPlugin()

```

Bases: `BasePlugin[AutorefsConfig]`

The `autorefs` plugin for `mkdocs`.

This plugin defines the following event hooks:

- `on_config`, to configure itself
- `on_page_markdown`, to set the current page in order for Markdown extension to use it
- `on_env`, to apply cross-references once all pages have been rendered

Check the [Developing Plugins](https://www.mkdocs.org/user-guide/plugins/#developing-plugins) page of `mkdocs` for more information about its plugin system.

Methods:

- **`get_backlinks`** – Return the backlinks to an identifier relative to the given URL.
- **`get_item_url`** – Return a site-relative URL with anchor to the identifier, if it's present anywhere.
- **`map_urls`** – Recurse on every anchor to map its ID to its absolute URL.
- **`on_config`** – Instantiate our Markdown extension.
- **`on_env`** – Apply cross-references and collect backlinks.
- **`on_page_content`** – Map anchors to URLs.
- **`on_page_markdown`** – Remember which page is the current one.
- **`register_anchor`** – Register that an anchor corresponding to an identifier was encountered when rendering the page.
- **`register_url`** – Register that the identifier should be turned into a link to this URL.

Attributes:

- **`current_page`** (`Page | None`) – The current page being processed.
- **`get_fallback_anchor`** (`Callable[[str], tuple[str, ...]] | None`) – Fallback anchors getter.
- **`legacy_refs`** (`bool`) – Whether to support legacy references.
- **`record_backlinks`** (`bool`) – Whether to record backlinks.
- **`scan_toc`** (`bool`) – Whether to scan the table of contents for identifiers to map to URLs.

Source code in `src/mkdocs_autorefs/_internal/plugin.py`

```
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
    self._title_map: dict[str, str] = {}
    self._breadcrumbs_map: dict[str, BacklinkCrumb] = {}
    self._abs_url_map: dict[str, str] = {}
    self._backlinks: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    # YORE: Bump 2: Remove line.
    self._get_fallback_anchor: Callable[[str], tuple[str, ...]] | None = None
    # YORE: Bump 2: Remove line.
    self._url_to_page: dict[str, Page] = {}

    self._link_titles: bool | Literal["external"] = True
    self._strip_title_tags: bool = False

```

### current_page

```
current_page: Page | None = None

```

The current page being processed.

### get_fallback_anchor

```
get_fallback_anchor: Callable[[str], tuple[str, ...]] | None

```

Fallback anchors getter.

### legacy_refs

```
legacy_refs: bool = True

```

Whether to support legacy references.

### record_backlinks

```
record_backlinks: bool = False

```

Whether to record backlinks.

### scan_toc

```
scan_toc: bool = True

```

Whether to scan the table of contents for identifiers to map to URLs.

### get_backlinks

```
get_backlinks(
    *identifiers: str, from_url: str
) -> dict[str, set[Backlink]]

```

Return the backlinks to an identifier relative to the given URL.

Parameters:

- **`*identifiers`** (`str`, default: `()` ) – The identifiers to get backlinks for.
- **`from_url`** (`str`) – The URL of the page where backlinks are rendered.

Returns:

- `dict[str, set[Backlink]]` – A dictionary of backlinks, with the type of reference as key and a set of backlinks as value.
- `dict[str, set[Backlink]]` – Each backlink is a tuple of (URL, title) tuples forming navigation breadcrumbs.

Source code in `src/mkdocs_autorefs/_internal/plugin.py`

```
def get_backlinks(self, *identifiers: str, from_url: str) -> dict[str, set[Backlink]]:
    """Return the backlinks to an identifier relative to the given URL.

    Arguments:
        *identifiers: The identifiers to get backlinks for.
        from_url: The URL of the page where backlinks are rendered.

    Returns:
        A dictionary of backlinks, with the type of reference as key and a set of backlinks as value.
        Each backlink is a tuple of (URL, title) tuples forming navigation breadcrumbs.
    """
    relative_backlinks: dict[str, set[Backlink]] = defaultdict(set)
    for identifier in set(identifiers):
        backlinks = self._backlinks.get(identifier, {})
        for backlink_type, backlink_urls in backlinks.items():
            for backlink_url in backlink_urls:
                relative_backlinks[backlink_type].add(self._get_backlink(from_url, backlink_url))
    return relative_backlinks

```

### get_item_url

```
get_item_url(
    identifier: str,
    from_url: str | None = None,
    fallback: Callable[[str], Sequence[str]] | None = None,
) -> tuple[str, str | None]

```

Return a site-relative URL with anchor to the identifier, if it's present anywhere.

Parameters:

- **`identifier`** (`str`) – The anchor (without '#').
- **`from_url`** (`str | None`, default: `None` ) – The URL of the base page, from which we link towards the targeted pages.

Returns:

- `tuple[str, str | None]` – A site-relative URL.

Source code in `src/mkdocs_autorefs/_internal/plugin.py`

```
def get_item_url(
    self,
    identifier: str,
    from_url: str | None = None,
    # YORE: Bump 2: Remove line.
    fallback: Callable[[str], Sequence[str]] | None = None,
) -> tuple[str, str | None]:
    """Return a site-relative URL with anchor to the identifier, if it's present anywhere.

    Arguments:
        identifier: The anchor (without '#').
        from_url: The URL of the base page, from which we link towards the targeted pages.

    Returns:
        A site-relative URL.
    """
    # YORE: Bump 2: Replace `, fallback` with `` within line.
    url = self._get_item_url(identifier, from_url, fallback)
    title = self._title_map.get(url) or None
    if from_url is not None:
        parsed = urlsplit(url)
        if not parsed.scheme and not parsed.netloc:
            url = relative_url(from_url, url)
    return url, title

```

### map_urls

```
map_urls(page: Page, anchor: AnchorLink) -> None

```

Recurse on every anchor to map its ID to its absolute URL.

This method populates `self._primary_url_map` by side-effect.

Parameters:

- **`page`** (`Page`) – The page containing the anchors.
- **`anchor`** (`AnchorLink`) – The anchor to process and to recurse on.

Source code in `src/mkdocs_autorefs/_internal/plugin.py`

```
def map_urls(self, page: Page, anchor: AnchorLink) -> None:
    """Recurse on every anchor to map its ID to its absolute URL.

    This method populates `self._primary_url_map` by side-effect.

    Arguments:
        page: The page containing the anchors.
        anchor: The anchor to process and to recurse on.
    """
    return self._map_urls(page, anchor)

```

### on_config

```
on_config(config: MkDocsConfig) -> MkDocsConfig | None

```

Instantiate our Markdown extension.

Hook for the [`on_config` event](https://www.mkdocs.org/user-guide/plugins/#on_config). In this hook, we instantiate our AutorefsExtension and add it to the list of Markdown extensions used by `mkdocs`.

Parameters:

- **`config`** (`MkDocsConfig`) – The MkDocs config object.

Returns:

- `MkDocsConfig | None` – The modified config.

Source code in `src/mkdocs_autorefs/_internal/plugin.py`

```
def on_config(self, config: MkDocsConfig) -> MkDocsConfig | None:
    """Instantiate our Markdown extension.

    Hook for the [`on_config` event](https://www.mkdocs.org/user-guide/plugins/#on_config).
    In this hook, we instantiate our [`AutorefsExtension`][mkdocs_autorefs.AutorefsExtension]
    and add it to the list of Markdown extensions used by `mkdocs`.

    Arguments:
        config: The MkDocs config object.

    Returns:
        The modified config.
    """
    _log.debug("Adding AutorefsExtension to the list")
    config.markdown_extensions.append(AutorefsExtension(self))  # type: ignore[arg-type]

    # YORE: Bump 2: Remove block.
    # mkdocstrings still uses the `page` attribute as a string.
    # Fortunately, it does so in f-strings, so we can simply patch the `__str__` method
    # to render the URL.
    Page.__str__ = lambda page: page.url  # type: ignore[method-assign,attr-defined]

    if self.config.link_titles == "auto":
        if getattr(config.theme, "name", None) == "material" and "navigation.instant.preview" in config.theme.get(
            "features",
            (),
        ):
            self._link_titles = "external"
        else:
            self._link_titles = True
    else:
        self._link_titles = self.config.link_titles

    if self.config.strip_title_tags == "auto":
        if getattr(config.theme, "name", None) == "material" and "content.tooltips" in config.theme.get(
            "features",
            (),
        ):
            self._strip_title_tags = False
        else:
            self._strip_title_tags = True
    else:
        self._strip_title_tags = self.config.strip_title_tags

    return config

```

### on_env

```
on_env(
    env: Environment,
    /,
    *,
    config: MkDocsConfig,
    files: Files,
) -> Environment

```

Apply cross-references and collect backlinks.

Hook for the [`on_env` event](https://www.mkdocs.org/user-guide/plugins/#on_env). In this hook, we try to fix unresolved references of the form `[title][identifier]` or `[identifier][]`. Doing that allows the user of `autorefs` to cross-reference objects in their documentation strings. It uses the native Markdown syntax so it's easy to remember and use.

We log a warning for each reference that we couldn't map to an URL.

We also collect backlinks at the same time. We fix cross-refs and collect backlinks in a single pass for performance reasons (we don't want to run the regular expression on each page twice).

Parameters:

- **`env`** (`Environment`) – The MkDocs environment.
- **`config`** (`MkDocsConfig`) – The MkDocs config object.
- **`files`** (`Files`) – The list of files in the MkDocs project.

Returns:

- `Environment` – The unmodified environment.

Source code in `src/mkdocs_autorefs/_internal/plugin.py`

```
@event_priority(-50)  # Late, after mkdocstrings has finished loading inventories.
def on_env(self, env: Environment, /, *, config: MkDocsConfig, files: Files) -> Environment:  # noqa: ARG002
    """Apply cross-references and collect backlinks.

    Hook for the [`on_env` event](https://www.mkdocs.org/user-guide/plugins/#on_env).
    In this hook, we try to fix unresolved references of the form `[title][identifier]` or `[identifier][]`.
    Doing that allows the user of `autorefs` to cross-reference objects in their documentation strings.
    It uses the native Markdown syntax so it's easy to remember and use.

    We log a warning for each reference that we couldn't map to an URL.

    We also collect backlinks at the same time. We fix cross-refs and collect backlinks in a single pass
    for performance reasons (we don't want to run the regular expression on each page twice).

    Arguments:
        env: The MkDocs environment.
        config: The MkDocs config object.
        files: The list of files in the MkDocs project.

    Returns:
        The unmodified environment.
    """
    for file in files:
        if file.page and file.page.content:
            _log.debug("Applying cross-refs in page %s", file.page.file.src_path)

            # YORE: Bump 2: Replace `, fallback=self.get_fallback_anchor` with `` within line.
            url_mapper = functools.partial(
                self.get_item_url,
                from_url=file.page.url,
                fallback=self.get_fallback_anchor,
            )
            backlink_recorder = (
                functools.partial(self._record_backlink, page_url=file.page.url) if self.record_backlinks else None
            )
            # YORE: Bump 2: Replace `, _legacy_refs=self.legacy_refs` with `` within line.
            file.page.content, unmapped = fix_refs(
                file.page.content,
                url_mapper,
                record_backlink=backlink_recorder,
                link_titles=self._link_titles,
                strip_title_tags=self._strip_title_tags,
                _legacy_refs=self.legacy_refs,
            )

            if unmapped and _log.isEnabledFor(logging.WARNING):
                for ref, context in unmapped:
                    message = f"from {context.filepath}:{context.lineno}: ({context.origin}) " if context else ""
                    _log.warning(
                        f"{file.page.file.src_path}: {message}Could not find cross-reference target '{ref}'",
                    )

    return env

```

### on_page_content

```
on_page_content(
    html: str, page: Page, **kwargs: Any
) -> str

```

Map anchors to URLs.

Hook for the [`on_page_content` event](https://www.mkdocs.org/user-guide/plugins/#on_page_content). In this hook, we map the IDs of every anchor found in the table of contents to the anchors absolute URLs. This mapping will be used later to fix unresolved reference of the form `[title][identifier]` or `[identifier][]`.

Parameters:

- **`html`** (`str`) – HTML converted from Markdown.
- **`page`** (`Page`) – The related MkDocs page instance.
- **`kwargs`** (`Any`, default: `{}` ) – Additional arguments passed by MkDocs.

Returns:

- `str` – The same HTML. We only use this hook to map anchors to URLs.

Source code in `src/mkdocs_autorefs/_internal/plugin.py`

```
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
    self.current_page = page
    # Collect `std`-domain URLs.
    if self.scan_toc:
        _log.debug("Mapping identifiers to URLs for page %s", page.file.src_path)
        for item in page.toc.items:
            self.map_urls(page, item)
    return html

```

### on_page_markdown

```
on_page_markdown(
    markdown: str, page: Page, **kwargs: Any
) -> str

```

Remember which page is the current one.

Parameters:

- **`markdown`** (`str`) – Input Markdown.
- **`page`** (`Page`) – The related MkDocs page instance.
- **`kwargs`** (`Any`, default: `{}` ) – Additional arguments passed by MkDocs.

Returns:

- `str` – The same Markdown. We only use this hook to keep a reference to the current page URL, used during Markdown conversion by the anchor scanner tree processor.

Source code in `src/mkdocs_autorefs/_internal/plugin.py`

```
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
    # YORE: Bump 2: Remove line.
    self._url_to_page[page.url] = page
    self.current_page = page
    return markdown

```

### register_anchor

```
register_anchor(
    page: Page,
    identifier: str,
    anchor: str | None = None,
    *,
    title: str | None = None,
    primary: bool = True,
) -> None

```

Register that an anchor corresponding to an identifier was encountered when rendering the page.

Parameters:

- **`page`** (`Page`) – The page where the anchor was found.
- **`identifier`** (`str`) – The identifier to register.
- **`anchor`** (`str | None`, default: `None` ) – The anchor on the page, without #. If not provided, defaults to the identifier.
- **`title`** (`str | None`, default: `None` ) – The title of the anchor (optional).
- **`primary`** (`bool`, default: `True` ) – Whether this anchor is the primary one for the identifier.

Source code in `src/mkdocs_autorefs/_internal/plugin.py`

```
def register_anchor(
    self,
    page: Page,
    identifier: str,
    anchor: str | None = None,
    *,
    title: str | None = None,
    primary: bool = True,
) -> None:
    """Register that an anchor corresponding to an identifier was encountered when rendering the page.

    Arguments:
        page: The page where the anchor was found.
        identifier: The identifier to register.
        anchor: The anchor on the page, without `#`. If not provided, defaults to the identifier.
        title: The title of the anchor (optional).
        primary: Whether this anchor is the primary one for the identifier.
    """
    # YORE: Bump 2: Remove block.
    if isinstance(page, str):
        try:
            page = self._url_to_page[page]
        except KeyError:
            page = self.current_page

    url = f"{page.url}#{anchor or identifier}"
    url_map = self._primary_url_map if primary else self._secondary_url_map
    if identifier in url_map:
        if url not in url_map[identifier]:
            url_map[identifier].append(url)
    else:
        url_map[identifier] = [url]
    if title and url not in self._title_map:
        self._title_map[url] = title

```

### register_url

```
register_url(identifier: str, url: str) -> None

```

Register that the identifier should be turned into a link to this URL.

Parameters:

- **`identifier`** (`str`) – The new identifier.
- **`url`** (`str`) – The absolute URL (including anchor, if needed) where this item can be found.

Source code in `src/mkdocs_autorefs/_internal/plugin.py`

```
def register_url(self, identifier: str, url: str) -> None:
    """Register that the identifier should be turned into a link to this URL.

    Arguments:
        identifier: The new identifier.
        url: The absolute URL (including anchor, if needed) where this item can be found.
    """
    self._abs_url_map[identifier] = url

```

## Backlink

```
Backlink(crumbs: tuple[BacklinkCrumb, ...])

```

A backlink (list of breadcrumbs).

Attributes:

- **`crumbs`** (`tuple[BacklinkCrumb, ...]`) – The list of breadcrumbs.

### crumbs

```
crumbs: tuple[BacklinkCrumb, ...]

```

The list of breadcrumbs.

## BacklinkCrumb

```
BacklinkCrumb(
    title: str,
    url: str,
    parent: BacklinkCrumb | None = None,
)

```

A navigation breadcrumb for a backlink.

Methods:

- **`__eq__`** – Compare URLs for equality.

Attributes:

- **`parent`** (`BacklinkCrumb | None`) – The parent breadcrumb.
- **`title`** (`str`) – The title of the breadcrumb.
- **`url`** (`str`) – The URL of the breadcrumb.

### parent

```
parent: BacklinkCrumb | None = None

```

The parent breadcrumb.

### title

```
title: str

```

The title of the breadcrumb.

### url

```
url: str

```

The URL of the breadcrumb.

### __eq__

```
__eq__(value: object) -> bool

```

Compare URLs for equality.

Source code in `src/mkdocs_autorefs/_internal/backlinks.py`

```
def __eq__(self, value: object) -> bool:
    """Compare URLs for equality."""
    if isinstance(value, BacklinkCrumb):
        return self.url == value.url
    return False

```

## BacklinksTreeProcessor

```
BacklinksTreeProcessor(
    plugin: AutorefsPlugin, md: Markdown | None = None
)

```

Bases: `Treeprocessor`

Enhance autorefs with `backlink-type` and `backlink-anchor` attributes.

These attributes are then used later to register backlinks.

Parameters:

- **`plugin`** (`AutorefsPlugin`) – A reference to the autorefs plugin, to use its register_anchor method.

Methods:

- **`run`** – Run the tree processor.

Attributes:

- **`initial_id`** (`str | None`) – The initial heading ID.
- **`name`** (`str`) – The name of the tree processor.

Source code in `src/mkdocs_autorefs/_internal/backlinks.py`

```
def __init__(self, plugin: AutorefsPlugin, md: Markdown | None = None) -> None:
    """Initialize the tree processor.

    Parameters:
        plugin: A reference to the autorefs plugin, to use its `register_anchor` method.
    """
    super().__init__(md)
    self._plugin = plugin
    self._last_heading_id: str | None = None

```

### initial_id

```
initial_id: str | None = None

```

The initial heading ID.

### name

```
name: str = 'mkdocs-autorefs-backlinks'

```

The name of the tree processor.

### run

```
run(root: Element) -> None

```

Run the tree processor.

Parameters:

- **`root`** (`Element`) – The root element of the document.

Source code in `src/mkdocs_autorefs/_internal/backlinks.py`

```
def run(self, root: Element) -> None:
    """Run the tree processor.

    Arguments:
        root: The root element of the document.
    """
    if self._plugin.current_page is not None:
        self._last_heading_id = self.initial_id
        self._enhance_autorefs(root)

```

## fix_ref

```
fix_ref(
    url_mapper: Callable[[str], tuple[str, str | None]],
    unmapped: list[tuple[str, Context | None]],
    record_backlink: Callable[[str, str, str], None]
    | None = None,
    *,
    link_titles: bool | Literal["external"] = True,
    strip_title_tags: bool = False,
) -> Callable

```

Return a `repl` function for [`re.sub`](https://docs.python.org/3/library/re.html#re.sub).

In our context, we match Markdown references and replace them with HTML links.

When the matched reference's identifier was not mapped to an URL, we append the identifier to the outer `unmapped` list. It generally means the user is trying to cross-reference an object that was not collected and rendered, making it impossible to link to it. We catch this exception in the caller to issue a warning.

Parameters:

- **`url_mapper`** (`Callable[[str], tuple[str, str | None]]`) – A callable that gets an object's site URL by its identifier, such as mkdocs_autorefs.AutorefsPlugin.get_item_url.
- **`unmapped`** (`list[tuple[str, Context | None]]`) – A list to store unmapped identifiers.
- **`record_backlink`** (`Callable[[str, str, str], None] | None`, default: `None` ) – A callable to record backlinks.
- **`link_titles`** (`bool | Literal['external']`, default: `True` ) – How to set HTML titles on links. Always (True), never (False), or external-only ("external").
- **`strip_title_tags`** (`bool`, default: `False` ) – Whether to strip HTML tags from link titles.

Returns:

- `Callable` – The actual function accepting a Match object
- `Callable` – and returning the replacement strings.

Source code in `src/mkdocs_autorefs/_internal/references.py`

```
def fix_ref(
    url_mapper: Callable[[str], tuple[str, str | None]],
    unmapped: list[tuple[str, AutorefsHookInterface.Context | None]],
    record_backlink: Callable[[str, str, str], None] | None = None,
    *,
    link_titles: bool | Literal["external"] = True,
    strip_title_tags: bool = False,
) -> Callable:
    """Return a `repl` function for [`re.sub`](https://docs.python.org/3/library/re.html#re.sub).

    In our context, we match Markdown references and replace them with HTML links.

    When the matched reference's identifier was not mapped to an URL, we append the identifier to the outer
    `unmapped` list. It generally means the user is trying to cross-reference an object that was not collected
    and rendered, making it impossible to link to it. We catch this exception in the caller to issue a warning.

    Arguments:
        url_mapper: A callable that gets an object's site URL by its identifier,
            such as [mkdocs_autorefs.AutorefsPlugin.get_item_url][].
        unmapped: A list to store unmapped identifiers.
        record_backlink: A callable to record backlinks.
        link_titles: How to set HTML titles on links. Always (`True`), never (`False`), or external-only (`"external"`).
        strip_title_tags: Whether to strip HTML tags from link titles.

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

        identifiers = (identifier, slug) if slug else (identifier,)

        if (
            record_backlink
            and (backlink_type := attrs.get("backlink-type"))
            and (backlink_anchor := attrs.get("backlink-anchor"))
        ):
            record_backlink(identifier, backlink_type, backlink_anchor)

        try:
            url, original_title = _find_url(identifiers, url_mapper)
        except KeyError:
            if optional:
                _log.debug("Unresolved optional cross-reference: %s", identifier)
                return f'<span title="{identifier}">{title}</span>'
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

        title_attr = ""
        if link_titles is True or (link_titles == "external" and external):
            if optional:
                # The `optional` attribute is generally only added by mkdocstrings handlers,
                # for API objects, meaning we can and should append the full identifier.
                tooltip = _tooltip(identifier, original_title, strip_tags=strip_title_tags)
            else:
                # Autorefs without `optional` are generally user-written ones,
                # so we should only use the original title.
                tooltip = original_title or ""

            if tooltip and tooltip not in f"<code>{title}</code>":
                title_attr = f' title="{_html_tag_stripper.strip(tooltip) if strip_title_tags else escape(tooltip)}"'

        return f'<a class="{class_attr}"{title_attr} href="{escape(url)}"{remaining}>{title}</a>'

    return inner

```

## fix_refs

```
fix_refs(
    html: str,
    url_mapper: Callable[[str], tuple[str, str | None]],
    *,
    record_backlink: Callable[[str, str, str], None]
    | None = None,
    link_titles: bool | Literal["external"] = True,
    strip_title_tags: bool = False,
    _legacy_refs: bool = True,
) -> tuple[str, list[tuple[str, Context | None]]]

```

Fix all references in the given HTML text.

Parameters:

- **`html`** (`str`) – The text to fix.
- **`url_mapper`** (`Callable[[str], tuple[str, str | None]]`) – A callable that gets an object's site URL by its identifier, such as mkdocs_autorefs.AutorefsPlugin.get_item_url.
- **`record_backlink`** (`Callable[[str, str, str], None] | None`, default: `None` ) – A callable to record backlinks.
- **`link_titles`** (`bool | Literal['external']`, default: `True` ) – How to set HTML titles on links. Always (True), never (False), or external-only ("external").
- **`strip_title_tags`** (`bool`, default: `False` ) – Whether to strip HTML tags from link titles.

Returns:

- `tuple[str, list[tuple[str, Context | None]]]` – The fixed HTML, and a list of unmapped identifiers (string and optional context).

Source code in `src/mkdocs_autorefs/_internal/references.py`

```
def fix_refs(
    html: str,
    url_mapper: Callable[[str], tuple[str, str | None]],
    *,
    record_backlink: Callable[[str, str, str], None] | None = None,
    link_titles: bool | Literal["external"] = True,
    strip_title_tags: bool = False,
    # YORE: Bump 2: Remove line.
    _legacy_refs: bool = True,
) -> tuple[str, list[tuple[str, AutorefsHookInterface.Context | None]]]:
    """Fix all references in the given HTML text.

    Arguments:
        html: The text to fix.
        url_mapper: A callable that gets an object's site URL by its identifier,
            such as [mkdocs_autorefs.AutorefsPlugin.get_item_url][].
        record_backlink: A callable to record backlinks.
        link_titles: How to set HTML titles on links. Always (`True`), never (`False`), or external-only (`"external"`).
        strip_title_tags: Whether to strip HTML tags from link titles.

    Returns:
        The fixed HTML, and a list of unmapped identifiers (string and optional context).
    """
    unmapped: list[tuple[str, AutorefsHookInterface.Context | None]] = []
    html = AUTOREF_RE.sub(
        fix_ref(url_mapper, unmapped, record_backlink, link_titles=link_titles, strip_title_tags=strip_title_tags),
        html,
    )

    # YORE: Bump 2: Remove block.
    if _legacy_refs:
        html = AUTO_REF_RE.sub(_legacy_fix_ref(url_mapper, unmapped), html)

    return html, unmapped

```

## relative_url

```
relative_url(url_a: str, url_b: str) -> str

```

Compute the relative path from URL A to URL B.

Parameters:

- **`url_a`** (`str`) – URL A.
- **`url_b`** (`str`) – URL B.

Returns:

- `str` – The relative URL to go from A to B.

Source code in `src/mkdocs_autorefs/_internal/references.py`

```
def relative_url(url_a: str, url_b: str) -> str:
    """Compute the relative path from URL A to URL B.

    Arguments:
        url_a: URL A.
        url_b: URL B.

    Returns:
        The relative URL to go from A to B.
    """
    parts_a = url_a.split("/")
    url_b, *rest = url_b.split("#", 1)
    anchor = rest[0] if rest else ""
    parts_b = url_b.split("/")

    # Remove common left parts.
    while parts_a and parts_b and parts_a[0] == parts_b[0]:
        parts_a.pop(0)
        parts_b.pop(0)

    # Go up as many times as remaining a parts' depth.
    levels = len(parts_a) - 1
    parts_relative = [".."] * levels + parts_b
    relative = "/".join(parts_relative)
    return f"{relative}#{anchor}"

```
