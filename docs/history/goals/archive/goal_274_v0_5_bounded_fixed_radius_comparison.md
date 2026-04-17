# Goal 274: v0.5 Bounded Fixed-Radius Comparison Harness

Date: 2026-04-12
Status: proposed

## Purpose

Add the first bounded offline comparison harness that evaluates a parsed
external fixed-radius artifact against RTDL's own reference rows on the same
portable 3D point packages.

## Why This Goal Matters

After Goals 272 and 273, the repo can:

- materialize portable bounded KITTI point packages
- parse a bounded cuNSearch fixed-radius response artifact

What it still cannot do is connect those two layers into a real comparison
result. That means the adapter line still stops one step before parity.

## Scope

This goal will:

1. add a bounded fixed-radius comparison helper
2. load portable point packages for query and search inputs
3. compute RTDL reference rows on those packages
4. parse the external response artifact
5. report row counts and parity status honestly

## Non-Goals

This goal does not:

- execute cuNSearch live
- claim live Linux parity has been achieved
- claim any paper-fidelity reproduction result

## Done When

This goal is done when the public Python surface can:

- compare portable 3D RTDL inputs against a bounded external response artifact
- report parity and row counts honestly
- preserve the offline-only boundary clearly
