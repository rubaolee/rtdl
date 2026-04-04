# RTDL RayJoin Paper Package

This directory contains the current IEEE-style anonymous manuscript draft for
RTDL.

## Files

- `main.tex`
- `references.bib`
- vendored IEEEtran template files under `IEEEtran/`

## Current boundary

This package is intended to be peer-review ready in content and structure, but
the current local shell does not have a LaTeX engine on `PATH`.

That means:

- the source is real IEEE-style LaTeX
- the draft can be audited now for content, structure, and formatting choices
- PDF compilation still requires a LaTeX engine such as `pdflatex`, `latexmk`,
  or `tectonic` in the execution environment

## Suggested build commands once LaTeX is available

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```
