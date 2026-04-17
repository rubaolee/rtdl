# Goal 265: v0.5 RTNN Dataset Registry

Date: 2026-04-12
Status: proposed

## Purpose

Add a real RTNN-specific dataset-family and experiment-target registry inside the
live workspace so `v0.5` paper-consistency work has a concrete source of truth
for:

- which 3D dataset families matter
- how they are supposed to be acquired
- which reproduction tier each target belongs to

## Why This Goal Matters

The current `v0.5` line already has:

- 3D public point types
- 3D Python-reference nearest-neighbor support
- additive `bounded_knn_rows`
- 2D CPU/oracle closure for `bounded_knn_rows`

What is still missing is the first real paper-consistency data layer.

Without that layer, later claims about:

- RTNN-style reproduction
- dataset packaging
- exact versus bounded reproduction

would still be too loose.

## Scope

This goal will:

1. add a dedicated RTNN reproduction module in `src/rtdsl/`
2. seed the accepted dataset-family registry from the `v0.5` RTNN gap summary
3. define first experiment-target labels:
   - bounded reproduction
   - exact reproduction candidate
   - RTDL extension
4. add tests proving the registry contents and filters
5. update the `v0.5` goal-sequence document so it matches the real current line

## Non-Goals

This goal does not:

- download or package the datasets yet
- add baseline-library adapters yet
- claim full paper reproduction

## Done When

This goal is done when:

- RTNN dataset families are queryable from the public Python surface
- the registry clearly distinguishes dataset family, experiment target, and
  local bounded profile
- the sequence doc no longer misstates Goals 263 and 264
