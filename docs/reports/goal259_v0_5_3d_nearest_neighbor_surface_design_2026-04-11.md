# Goal 259: v0.5 3D Nearest-Neighbor Surface Design

Date: 2026-04-11
Status: implemented

## Purpose

Turn the `v0.5` charter into the first concrete engineering design decision.

## Current Constraint

The live codebase is still structurally 2D-first for nearest-neighbor work:

- `src/rtdsl/types.py` exposes `Point2DLayout` and `Points`
- `src/rtdsl/reference.py` uses `Point(id, x, y)` for nearest-neighbor truth
  paths
- the current runtime paths normalize and pack points around `x, y`

That means the correct first `v0.5` move is not immediate backend coding. The
correct first move is a saved design agreement for the 3D public surface.

## Design Decision

`v0.5` should open the nearest-neighbor 3D line in this order:

1. define first-class 3D point geometry surface
2. add reference/correctness path
3. add runtime and CPU/oracle support
4. then bring up accelerated backends

The repo should not claim a 3D nearest-neighbor public surface is online before
those layers exist.

## Main Outputs

- saved design goal for the 3D nearest-neighbor public surface
- explicit separation of:
  - dimensionality support
  - bounded-radius KNN paper-consistency semantics

## Why This Is The Right Next Step

It avoids two failure modes:

1. exposing a fake 3D surface too early
2. mixing dimensionality support with the still-separate paper-contract
   question

This keeps the first `v0.5` implementation goals scoped and honest.
