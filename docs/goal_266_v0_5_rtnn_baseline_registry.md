# Goal 266: v0.5 RTNN Baseline Registry

Date: 2026-04-12
Status: proposed

## Purpose

Add a concrete baseline-library decision layer for the RTNN-style comparison set
so `v0.5` can move from vague baseline mentions to explicit integration
priorities and boundaries.

## Why This Goal Matters

The charter and gap summary already say that the RTNN comparison set needs an
honest baseline-library story. Without a registry, later adapter work would be
too ad hoc and too easy to overclaim.

## Scope

This goal will:

1. add a dedicated RTNN baseline registry module
2. record the paper comparison-set libraries explicitly:
   - `cuNSearch`
   - `FRNN`
   - `PCLOctree`
   - `FastRNN`
3. record how the repo's existing external baselines fit relative to that set:
   - `SciPy cKDTree`
   - `PostGIS`
4. record the first explicit adapter decisions and priorities
5. add tests proving the registry and decisions

## Non-Goals

This goal does not:

- build any third-party comparison library
- claim any baseline adapter is online
- claim paper-faithful reproduction

## Done When

This goal is done when the public Python surface can answer:

- which comparison baselines are in scope
- which are paper-set versus non-paper-set
- which library should be adapted first
- which ones are intentionally deferred because of packaging friction
