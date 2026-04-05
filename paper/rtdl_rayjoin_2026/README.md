# RTDL RayJoin Paper Package

This directory contains the current IEEE-style RTDL manuscript draft.

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
- the current built PDF is 8 pages
- the current draft names the author as:
  - Rubao Lee
  - `lee.rubao@ieee.org`
- the current draft has repository review coverage from Gemini and Claude
  section reviews plus an updated full-draft Gemini review:
  - `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-05-codex-consensus-paper-updated-draft.md`

## Submission boundary

This package is intentionally honest about the current RTDL evidence boundary:

- accepted bounded closure is included
- unstable continent datasets remain deferred explicitly
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
