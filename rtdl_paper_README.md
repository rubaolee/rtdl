# RTDL Paper Package

The current RTDL manuscript is stored at the repository top level.

## Files

- `rtdl_paper.tex`
- `rtdl_paper_references.bib`
- `rtdl_paper.pdf`
- `rtdl_paper_assets/IEEEtran/`
- `rtdl_paper_assets/figures/`

## Current paper scope

This draft is intentionally a system/design paper first.

It does not embed the full experiment archive in the manuscript. Instead, it
keeps a short current-status evaluation section and leaves the detailed
artifact trail in the repository reports.

The paper currently states, briefly and honestly, that:

- RTDL preserves exact emitted-row parity on the accepted package surfaces
- Embree and OptiX beat PostGIS on the strongest accepted long
  `county_zipcode` positive-hit `pip` surface
- Vulkan is hardware-validated and parity-clean on that same surface, but
  slower

## Build

Preferred:

```bash
tectonic rtdl_paper.tex
```

Traditional toolchain:

```bash
pdflatex rtdl_paper.tex
bibtex rtdl_paper
pdflatex rtdl_paper.tex
pdflatex rtdl_paper.tex
```

## Author

- Rubao Lee
- `lee.rubao@ieee.org`
