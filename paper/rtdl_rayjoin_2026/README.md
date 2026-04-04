# RTDL RayJoin Paper Package

This directory contains the current IEEE-style anonymous manuscript draft for
RTDL.

## Files

- `main.tex`
- `references.bib`
- vendored IEEEtran template files under `IEEEtran/`

## Current state

This package is intended to be submission-ready in source structure and close to
submission-ready in content quality under the repository's bounded-claim rule.

Built artifact:

- `main.pdf`

The PDF was built locally with `tectonic`.

Important note:

- the manuscript still has minor TeX box warnings
- but the package now compiles successfully end-to-end into a PDF on this
  machine
- the package is still anonymous and uses a generic review-style author block
  rather than a venue-specific submission ID or metadata block

## Submission boundary

This package is intentionally honest about the current RTDL evidence boundary:

- accepted bounded closure is included
- unavailable dataset families remain deferred explicitly
- overlay is labeled as an overlay-seed analogue rather than full polygon
  materialization

This means the package is suitable for peer review as a bounded-result systems
paper, not as a claim of paper-identical full RayJoin reproduction.

## Suggested build commands once LaTeX is available

```bash
tectonic main.tex
```

Alternative traditional toolchain:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```
