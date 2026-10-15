# 1404 fork of Documenso

This repository is a fork of [Documenso](https://github.com/documenso/documenso) (AGPL-3.0),
run by 1404 at https://sign.1404.io.

**What we changed:** branding only — product name, logos, favicons, colours, page titles,
email wording and footer, links to 1404.io, a "Source code (AGPL)" link in the app, and the
default signing reason. We removed upstream's GitHub workflows and build our own image.
We did not modify `packages/ee` (Documenso Commercial License) and do not use its paid features.

Everything is regenerated from two scripts in `.1404-brand/`:
`make_assets.py` (logo + icons from the 1404.io font, Instrument Serif, SIL OFL) and
`rebrand.py` (text, links, colours). The full diff against upstream is the commit
"1404 branding" on the `1404-v<version>` branch.

Copyright for Documenso remains with Documenso, Inc. and contributors; see `LICENSE`.
"Documenso" is their trademark; this fork does not present itself as Documenso.
