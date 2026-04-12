# RTNN Gap Summary For v0.5

Date: 2026-04-11
Status: active planning input

## Purpose

Summarize, inside the live `v0.4.0` workspace, the structural gaps between the
released nearest-neighbor line and a paper-faithful RTNN reproduction story.

This report exists so `v0.5` planning and saved review can rely only on files
inside the current workspace.

## Current `v0.4.0` Position

RTDL `v0.4.0` already has:

- accepted `fixed_radius_neighbors`
- accepted `knn_rows`
- CPU/oracle truth path
- Embree
- OptiX
- Vulkan
- heavy Linux benchmarking
- indexed PostGIS comparison

That is enough for a strong RTNN-inspired study.

It is not enough for a full paper-faithful RTNN reproduction.

## Confirmed Gaps

### 1. Public nearest-neighbor surface is still 2D-first

The published nearest-neighbor surface is strong for the released 2D line, but
the RTNN paper's evaluation story is materially 3D. `v0.5` needs a true 3D
nearest-neighbor public surface if paper-consistent reproduction is a real
goal.

### 2. Current `knn_rows` contract is not paper-aligned

The current released `knn_rows` surface exposes a `k`-only shape. If the target
paper semantics require both:

- search radius
- maximum returned neighbors

then `v0.5` needs a bounded-radius KNN contract instead of forcing the paper
story through the current interface.

### 3. Paper baseline-library harnesses are missing

The RTNN-style comparison story requires a decision and honest documentation for
baseline libraries such as:

- cuNSearch
- FRNN
- PCLOctree
- FastRNN

`v0.4.0` does not ship those harnesses.

### 4. Paper dataset packaging is missing

The repo does not yet package or document a reproducible acquisition flow for
the paper-aligned dataset layer, including likely needs such as:

- KITTI-derived point sets
- Stanford 3D scan point sets
- N-body or Millennium-style point sets

### 5. Paper ablation harnesses are missing

`v0.4.0` does not ship the paper-style ablation layer needed for honest
comparison of scheduling, partitioning, bundling, or similar internal choices.

### 6. Hardware parity is not available

Exact speedup reproduction against the paper is still bounded by the actual
available hardware. This means `v0.5` reports must distinguish:

- exact reproduction
- bounded reproduction
- RTDL extension

## Implication For `v0.5`

The next release line should be driven by paper/implementation consistency, not
by unrelated feature growth.

The minimum real `v0.5` spine is:

1. 3D nearest-neighbor surface
2. paper-consistent KNN contract where needed
3. dataset packaging / acquisition flows
4. baseline-library harnesses
5. labeled experiment reports

## Honesty Boundary

This report does not claim that `v0.5` will necessarily reproduce every paper
experiment exactly. It defines the known missing pieces that must be resolved or
explicitly bounded before such claims would be honest.
