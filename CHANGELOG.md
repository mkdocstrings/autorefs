# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [1.4.1](https://github.com/mkdocstrings/autorefs/releases/tag/1.4.1) - 2025-03-08

<small>[Compare with 1.4.0](https://github.com/mkdocstrings/autorefs/compare/1.4.0...1.4.1)</small>

### Code Refactoring

- Store parent pages *and parent sections* in backlink breadcrumbs ([67955ce](https://github.com/mkdocstrings/autorefs/commit/67955ce5bf6b1b2cbea9c78b459e980f17bececc) by Timothée Mazzucotelli).
- Ignore Markdown anchors when setting backlink metadata on autorefs ([3ac4797](https://github.com/mkdocstrings/autorefs/commit/3ac47979c0371ba53e623284c76bb29985ee7037) by Timothée Mazzucotelli).
- Handle absence of `#` when computing relative URLs ([ca6461e](https://github.com/mkdocstrings/autorefs/commit/ca6461ebdb006897b012d1b92692ffffe9445ed2) by Timothée Mazzucotelli).

## [1.4.0](https://github.com/mkdocstrings/autorefs/releases/tag/1.4.0) - 2025-02-24

<small>[Compare with 1.3.1](https://github.com/mkdocstrings/autorefs/compare/1.3.1...1.4.0)</small>

### Features

- Add backlinks feature ([5a3b387](https://github.com/mkdocstrings/autorefs/commit/5a3b38753c68cabd047fd062afba66417ccd124e) by Timothée Mazzucotelli). [PR-65](https://github.com/mkdocstrings/autorefs/pull/65), [Issue-mkdocstrings-723](https://github.com/mkdocstrings/mkdocstrings/issues/723), [Issue-mkdocstrings-python-153](https://github.com/mkdocstrings/python/issues/153)
- Add `strip_title_tags` option ([00ce203](https://github.com/mkdocstrings/autorefs/commit/00ce2031a1a648c7d6f682ff7e94138c73957b20) and [b21aefd](https://github.com/mkdocstrings/autorefs/commit/b21aefd79b7f53c1b153be635cf4a8ccf1fcdb2f) by Timothée Mazzucotelli). [Issue-33](https://github.com/mkdocstrings/autorefs/issues/33)
- Add `link_titles` option and adapt related logic ([e3b602e](https://github.com/mkdocstrings/autorefs/commit/e3b602e60a5836e3ef41433d5490202a9656f603) by Timothée Mazzucotelli). [Issue-33](https://github.com/mkdocstrings/autorefs/issues/33), [Issue-62](https://github.com/mkdocstrings/autorefs/issues/62)

### Code Refactoring

- Move code to internal folder, expose public API in top-level module, document all public objects ([9615d13](https://github.com/mkdocstrings/autorefs/commit/9615d13e2f85640ebb1c6c055d41f068752884b2) by Timothée Mazzucotelli).
- Store actual page instance instead of URL in plugin's `current_page` attribute ([8023588](https://github.com/mkdocstrings/autorefs/commit/8023588ee38dc86299010979b05873dfd6b5039a) and [2009f85](https://github.com/mkdocstrings/autorefs/commit/2009f85eb10abc14b35c74a969c84744ee1f98ed) by Timothée Mazzucotelli).
- Use the `on_env` hook to fix cross-references ([70fec3e](https://github.com/mkdocstrings/autorefs/commit/70fec3e270e2d8f95213d63b8a99962b9d30569c) by Timothée Mazzucotelli). [Discussion-mkdocs-3917](https://github.com/mkdocs/mkdocs/discussions/3917)
- Record heading titles alongside URLs ([791782e](https://github.com/mkdocstrings/autorefs/commit/791782eef8f85aad84c39bf4f82286613f055322) by Timothée Mazzucotelli). [Issue-33](https://github.com/mkdocstrings/autorefs/issues/33)

## [1.3.1](https://github.com/mkdocstrings/autorefs/releases/tag/1.3.1) - 2025-02-11

<small>[Compare with 1.3.0](https://github.com/mkdocstrings/autorefs/compare/1.3.0...1.3.1)</small>

### Bug Fixes

- Always resolve secondary URLs to closest (don't log warnings) ([243ad35](https://github.com/mkdocstrings/autorefs/commit/243ad35f193b48216b531333e0d91ab2fa0a0db4) by Timothée Mazzucotelli). [Issue-52](https://github.com/mkdocstrings/autorefs/issues/52)

## [1.3.0](https://github.com/mkdocstrings/autorefs/releases/tag/1.3.0) - 2025-01-12

<small>[Compare with 1.2.0](https://github.com/mkdocstrings/autorefs/compare/1.2.0...1.3.0)</small>

### Build

- Drop support for Python 3.8 ([ee3eaad](https://github.com/mkdocstrings/autorefs/commit/ee3eaadac59331b883f83c6cd9aa0ac4ea3707b5) by Timothée Mazzucotelli).

### Features

- Handle inline references with markup within them ([54a02a7](https://github.com/mkdocstrings/autorefs/commit/54a02a7a61cdeaed0df3f98f49be4c36d07c0b8e) by Timothée Mazzucotelli). [Follow-up-of-issue-58](https://github.com/mkdocstrings/autorefs/issues/58)
- Separate URLs in two groups, primary and secondary ([559c723](https://github.com/mkdocstrings/autorefs/commit/559c723203d3f73040b1005ab3762a4a7bf8e133) by Timothée Mazzucotelli). [Related-to-issue-61](https://github.com/mkdocstrings/autorefs/issues/61)

### Bug Fixes

- Fallback to slugified title as id for non-exact, non-code references (`[Hello World][]` -> `[hello-world][]`) ([13428f1](https://github.com/mkdocstrings/autorefs/commit/13428f15d72d3fd473dcd16da94abcc3c32465e9) by Timothée Mazzucotelli). [Issue-58](https://github.com/mkdocstrings/autorefs/issues/58)

### Code Refactoring

- Deprecate fallback mechanism ([5e89cd8](https://github.com/mkdocstrings/autorefs/commit/5e89cd89f56f611666d84f95c4de0e184aa98437) by Timothée Mazzucotelli). [Issue-61](https://github.com/mkdocstrings/autorefs/issues/61)
- Log a debug message for unresolved optional references ([9e990d7](https://github.com/mkdocstrings/autorefs/commit/9e990d79a348f06c3d031c6759814acc32449e15) by Timothée Mazzucotelli).

## [1.2.0](https://github.com/mkdocstrings/autorefs/releases/tag/1.2.0) - 2024-09-01

<small>[Compare with 1.1.0](https://github.com/mkdocstrings/autorefs/compare/1.1.0...1.2.0)</small>

### Features

- Provide hook interface, use it to expand identifiers, attach additional context to references, and give more context around unmapped identifiers ([fb8df98](https://github.com/mkdocstrings/autorefs/commit/fb8df98fc8f9fb1b3accb8a305cc90b3a3507d86) by Timothée Mazzucotelli). [Issue-54](https://github.com/mkdocstrings/autorefs/issues/54), [PR-mkdocstrings#666](https://github.com/mkdocstrings/mkdocstrings/pull/666)
- Add option to resolve autorefs to closest URLs when multiple ones are found ([2916eb2](https://github.com/mkdocstrings/autorefs/commit/2916eb27dec89287dcaa1aefb4e9532156b66e30) by Timothée Mazzucotelli). [Issue-52](https://github.com/mkdocstrings/autorefs/issues/52)

### Bug Fixes

- Don't ignore identifiers containing spaces and slashes ([b36a0d1](https://github.com/mkdocstrings/autorefs/commit/b36a0d1c4b0f5a6441ee6a2de7409942a8702bd8) by Timothée Mazzucotelli). [Issue-55](https://github.com/mkdocstrings/autorefs/issues/55)

### Code Refactoring

- Emit deprecation warnings when old-style spans are found ([4f2be46](https://github.com/mkdocstrings/autorefs/commit/4f2be4633eec42c8e8582804741548a8e5602727) by Timothée Mazzucotelli).
- Use `%s` formatting instead of f-strings in log messages ([0cedf9d](https://github.com/mkdocstrings/autorefs/commit/0cedf9d82ede8ba10dc8e100d7d1e5ce488fca34) by Timothée Mazzucotelli).

## [1.1.0](https://github.com/mkdocstrings/autorefs/releases/tag/1.1.0) - 2024-08-20

<small>[Compare with 1.0.1](https://github.com/mkdocstrings/autorefs/compare/1.0.1...1.1.0)</small>

### Deprecations

- `AUTO_REF_RE` is renamed `AUTOREF_RE` (and updated for an improved version of `fix_refs`)
- `AutoRefInlineProcessor` is renamed `AutorefsInlineProcessor`

### Features

- Warn when multiple URLs are found for the same identifier ([c630354](https://github.com/mkdocstrings/autorefs/commit/c6303542018ca835f6941c070accb582f851f6b1) by Markus B). [Issue-35](https://github.com/mkdocstrings/autorefs/issues/35), [PR-50](https://github.com/mkdocstrings/autorefs/pull/50), Co-authored-by: Timothée Mazzucotelli <dev@pawamoy.fr>

### Bug Fixes

- Only log "Markdown anchors feature enabled" once ([1c9bda1](https://github.com/mkdocstrings/autorefs/commit/1c9bda1ab4f13c9a5cf5d202de755e5296729654) by Timothée Mazzucotelli). [Issue-44](https://github.com/mkdocstrings/autorefs/issues/44)

### Code Refactoring

- Use a custom autoref HTML tag ([e142023](https://github.com/mkdocstrings/autorefs/commit/e14202317dc13dd5eed93b5d7cfd183c87de893f) by Timothée Mazzucotelli). [PR-48](https://github.com/mkdocstrings/autorefs/pull/48)
- Rename AutoRefInlineProcessor to AutorefsInlineProcessor ([ffcaa01](https://github.com/mkdocstrings/autorefs/commit/ffcaa0178b642e423acdc66d35f1e6b207099dc7) by Timothée Mazzucotelli).
- Attach name to processors for easier retrieval ([036b825](https://github.com/mkdocstrings/autorefs/commit/036b825c7994b2586564e8707fbc0b3627c29569) by Timothée Mazzucotelli).

## [1.0.1](https://github.com/mkdocstrings/autorefs/releases/tag/1.0.1) - 2024-02-29

<small>[Compare with 1.0.0](https://github.com/mkdocstrings/autorefs/compare/1.0.0...1.0.1)</small>

### Bug Fixes

- Don't import `MkDocsConfig` (does not exist on MkDocs 1.3-) ([9c15664](https://github.com/mkdocstrings/autorefs/commit/9c156643ead1dc24f08b8047bd5b2fcd97662783) by Timothée Mazzucotelli).

## [1.0.0](https://github.com/mkdocstrings/autorefs/releases/tag/1.0.0) - 2024-02-27

<small>[Compare with 0.5.0](https://github.com/mkdocstrings/autorefs/compare/0.5.0...1.0.0)</small>

### Features

- Add Markdown anchors and aliases ([a215a97](https://github.com/mkdocstrings/autorefs/commit/a215a97a057b54e11ebec8865c64e93429edde63) by Timothée Mazzucotelli). [Replaces-PR-#20](https://github.com/mkdocstrings/autorefs/pull/20), [Related-to-PR-#25](https://github.com/mkdocstrings/autorefs/pull/25), [Related-to-issue-#35](https://github.com/mkdocstrings/autorefs/issues/35), Co-authored-by: Oleh Prypin <oleh@pryp.in>, Co-authored-by: tvdboom <m.524687@gmail.com>
- Preserve HTML data attributes (from spans to anchors) ([0c1781d](https://github.com/mkdocstrings/autorefs/commit/0c1781d7e3d6bffd55802868802bcd1ec9e8bbc7) by Timothée Mazzucotelli). [Issue-#41](https://github.com/mkdocstrings/autorefs/issues/41), [PR-#42](https://github.com/mkdocstrings/autorefs/pull/42), Co-authored-by: Oleh Prypin <oleh@pryp.in>
- Support ``[`identifier`][]`` with pymdownx.inlinehilite enabled ([e7f2228](https://github.com/mkdocstrings/autorefs/commit/e7f222894c70627c70e6a14e453a10a81e3f8957) by Oleh Prypin). [Issue-#34](https://github.com/mkdocstrings/autorefs/issues/34), [PR-#40](https://github.com/mkdocstrings/autorefs/pull/40), Co-authored-by: Timothée Mazzucotelli <dev@pawamoy.fr>

### Bug Fixes

- Recognize links with multi-line text ([225a6f2](https://github.com/mkdocstrings/autorefs/commit/225a6f275069bcdfb3411e80d4a7fa645b857b88) by Oleh Prypin). [Issue #31](https://github.com/mkdocstrings/autorefs/issues/31), [PR #32](https://github.com/mkdocstrings/autorefs/pull/32)

## [0.5.0](https://github.com/mkdocstrings/autorefs/releases/tag/0.5.0) - 2023-08-02

<small>[Compare with 0.4.1](https://github.com/mkdocstrings/autorefs/compare/0.4.1...0.5.0)</small>

### Breaking Changes

- Drop support for Python 3.7

### Build

- Migrate to pdm-backend ([48b92fb](https://github.com/mkdocstrings/autorefs/commit/48b92fb2c12e97242007e5fbbc1b18a36b7f29b6) by Michał Górny).

### Bug Fixes

- Stop using deprecated `warning_filter` ([7721103](https://github.com/mkdocstrings/autorefs/commit/77211035bb10b8e55f595eb7d0392344669ffdec) by Kyle King). [PR #30](https://github.com/mkdocstrings/autorefs/pull/30)

### Code Refactoring

- Use new MkDocs plugin logger if available ([ca8d758](https://github.com/mkdocstrings/autorefs/commit/ca8d75805ac289e9a5a8123565aa7833b34bd214) by Timothée Mazzucotelli).

## [0.4.1](https://github.com/mkdocstrings/autorefs/releases/tag/0.4.1) - 2022-03-07

<small>[Compare with 0.4.0](https://github.com/mkdocstrings/autorefs/compare/0.4.0...0.4.1)</small>

### Bug Fixes
- Fix packaging (missing `__init__` module) ([de0670b](https://github.com/mkdocstrings/autorefs/commit/de0670b77be84529c9c1ef37cad2a85ef8ec3cab) by Timothée Mazzucotelli). [Issue #17](https://github.com/mkdocstrings/autorefs/issues/17), [issue mkdocstrings/mkdocstrings#398](https://github.com/mkdocstrings/mkdocstrings/issues/398), [PR #18](https://github.com/mkdocstrings/autorefs/pull/18)


## [0.4.0](https://github.com/mkdocstrings/autorefs/releases/tag/0.4.0) - 2022-03-07

<small>[Compare with 0.3.1](https://github.com/mkdocstrings/autorefs/compare/0.3.1...0.4.0)</small>

### Features
- Add HTML classes to references: `autorefs` always, and `autorefs-internal` or `autorefs-external` depending on the link ([39db59d](https://github.com/mkdocstrings/autorefs/commit/39db59d802a59d1af93d24520b1e219eeec780e4) by Timothée Mazzucotelli). [PR #16](https://github.com/mkdocstrings/autorefs/pull/16)

### Bug Fixes
- Don't compute relative URLs of already relative ones ([f6b861c](https://github.com/mkdocstrings/autorefs/commit/f6b861c0e4a95c406ea3552fc93f889c3006e1a9) by Timothée Mazzucotelli). [PR #15](https://github.com/mkdocstrings/autorefs/pull/15)


## [0.3.1](https://github.com/mkdocstrings/autorefs/releases/tag/0.3.1) - 2021-12-27

<small>[Compare with 0.3.0](https://github.com/mkdocstrings/autorefs/compare/0.3.0...0.3.1)</small>

### Code Refactoring
- Support fallback method returning multiple identifiers ([0d2b411](https://github.com/mkdocstrings/autorefs/commit/0d2b411030d23cf65c834c6a881ec8d0efddee8c) by Timothée Mazzucotelli). [Issue #11](https://github.com/mkdocstrings/autorefs/issues/11), [PR #12](https://github.com/mkdocstrings/autorefs/pull/12) and [mkdocstrings#350](https://github.com/mkdocstrings/mkdocstrings/pull/350)


## [0.3.0](https://github.com/mkdocstrings/autorefs/releases/tag/0.3.0) - 2021-07-24

<small>[Compare with 0.2.1](https://github.com/mkdocstrings/autorefs/compare/0.2.1...0.3.0)</small>

### Features
- Add optional-hover ref type ([0288bdd](https://github.com/mkdocstrings/autorefs/commit/0288bdd34f779d73d3da19cfe2a89254fd3c4942) by Brian Koropoff). [PR #10](https://github.com/mkdocstrings/autorefs/pull/10)


## [0.2.1](https://github.com/mkdocstrings/autorefs/releases/tag/0.2.1) - 2021-05-07

<small>[Compare with 0.2.0](https://github.com/mkdocstrings/autorefs/compare/0.2.0...0.2.1)</small>

### Bug Fixes
- Prevent error during parallel installations ([c90e399](https://github.com/mkdocstrings/autorefs/commit/c90e399213dec3435bf5dd0a0e5035ba586076fd) by Timothée Mazzucotelli). [PR #9](https://github.com/mkdocstrings/autorefs/pull/9)


## [0.2.0](https://github.com/mkdocstrings/autorefs/releases/tag/0.2.0) - 2021-05-03

<small>[Compare with 0.1.1](https://github.com/mkdocstrings/autorefs/compare/0.1.1...0.2.0)</small>

### Features
- Allow registering absolute URLs for autorefs ([621686b](https://github.com/mkdocstrings/autorefs/commit/621686b4b36b8d24df80035095700f6a4f96567c) by Oleh Prypin). [PR #8](https://github.com/mkdocstrings/autorefs/pull/8)
- Allow external tools to insert references that are OK to skip ([7619c28](https://github.com/mkdocstrings/autorefs/commit/7619c2835a63b54b1f5e9e11c5f320c04e3579ac) by Oleh Prypin). [PR #7](https://github.com/mkdocstrings/autorefs/pull/7)
- Allow `[``identifier``][]`, understood as `[``identifier``][identifier]` ([2d3182d](https://github.com/mkdocstrings/autorefs/commit/2d3182db54dc33e75914e9c509bbf849842eb70a) by Oleh Prypin). [PR #5](https://github.com/mkdocstrings/autorefs/pull/5)


## [0.1.1](https://github.com/mkdocstrings/autorefs/releases/tag/0.1.1) - 2021-02-28

<small>[Compare with 0.1.0](https://github.com/mkdocstrings/autorefs/compare/0.1.0...0.1.1)</small>

### Packaging

- Remove unused dependencies ([9c6a8e6](https://github.com/mkdocstrings/autorefs/commit/9c6a8e610f52d471fefa02baa4aef2773bdb59c0) by Oleh Prypin).


## [0.1.0](https://github.com/mkdocstrings/autorefs/releases/tag/0.1.0) - 2021-02-17

<small>[Compare with first commit](https://github.com/mkdocstrings/autorefs/compare/fe6faa5d5a7a901605ec8ab98df09dc95067f6a8...0.1.0)</small>

### Features
- Split out "mkdocs-autorefs" plugin from "mkdocstrings" ([fe6faa5](https://github.com/mkdocstrings/autorefs/commit/fe6faa5d5a7a901605ec8ab98df09dc95067f6a8) by Oleh Prypin).
