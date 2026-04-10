# Codex Consensus: v0.4 Direction Decision

Status: closed after strategic reset to 2D nearest-neighbor scope

## Why this changed

The earlier 3D-oriented `v0.4` package is no longer the live direction.

The current explicit user decision is:

- do not make `v0.4` a 3D milestone

So the consensus must be refreshed against the revised nearest-neighbor plan.

## Current Codex position

- `v0.4` should not be demo-first
- `v0.4` should not be backend-only
- `v0.4` should not be 3D-first
- the strongest next milestone is a workload-language-first 2D release built
  around nearest-neighbor workloads

## Current provisional conclusion

The live revised package is:

- headline workload family:
  - nearest-neighbor search
- first accepted public workload:
  - `fixed_radius_neighbors`
- second workload in the same family:
  - `knn_rows`

The main reasons are:

- RTNN gives direct workload-level support
- X-HD shows nearest-neighbor search is a strong foundational building block
- the family is clearly non-graphical and aligned with RTDL's identity

## What the revised external reviews confirmed

Gemini confirmed the strategic move is right:

- replacing the 3D-first draft with a nearest-neighbor package better matches
  RTDL's public identity

Claude confirmed the same and sharpened the package:

- fixed-radius-first, KNN-second is the right sequencing
- Hausdorff should remain out of `v0.4` headline scope
- the package needed a named external baseline and a cleaner finish line
- backend transfer assumptions need to be explicit

## Final Codex conclusion

The settled `v0.4` package is:

- release theme:
  - nearest-neighbor workload release
- first accepted public workload:
  - `fixed_radius_neighbors`
- second workload in the same family:
  - `knn_rows`

This package is sharper and more faithful to RTDL's identity than the earlier
3D-first draft.
