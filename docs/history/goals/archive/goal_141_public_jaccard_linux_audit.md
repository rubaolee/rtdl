# Goal 141: Public Jaccard Linux Audit

## Purpose

Take the narrow Jaccard line through a real Linux/public-data audit after the
authored closures in Goals 138 and 140.

## Accepted scope

- use real public pathology annotations, not only authored shapes
- keep the accepted Goal 140 semantics:
  - orthogonal integer-grid unit-cell polygons
- make the public-data derivation explicit
- validate Python/native CPU against PostGIS on Linux
- report practical performance numbers

## Accepted closure for Goal 141

- one real public MoNuSeg XML slide downloaded on Linux
- deterministic conversion from public freehand polygons to unit-square RTDL polygons
- deterministic derived left/right comparison pair
- Linux/PostGIS parity on accepted scales
- report the scaling boundary honestly

## Not claimed

- generic continuous polygon-set Jaccard
- direct evaluation on raw freehand polygons under unchanged semantics
- paired human-vs-human public segmentation set comparison from the dataset itself
- broad backend audit beyond Python/native CPU
