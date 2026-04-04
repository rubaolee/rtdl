# RTDL RayJoin Paper Package

This directory contains the current IEEE-style anonymous manuscript draft for
RTDL.

## Files

- `main.tex`
- `references.bib`
- vendored IEEEtran template files under `IEEEtran/`

## Current state

This package is intended to be peer-review ready in content and structure.

Built artifact:

- `main.pdf`

The PDF was built locally with `tectonic`.

Important note:

- the manuscript still has minor TeX box warnings
- but the package now compiles successfully end-to-end into a PDF on this
  machine

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
