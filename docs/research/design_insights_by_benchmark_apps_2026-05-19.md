# Design Insights By Benchmark Apps

Date: 2026-05-19

Status: research/design synthesis for the current v2.x benchmark-app campaign.

## Purpose

RTDL's recent benchmark apps were not treated as a fixed app library. They were
used as pressure tests for the language and runtime. The rule stayed constant:
the native engine must remain app-agnostic, while app/domain logic belongs in
Python, partner code, tutorials, examples, or research benchmark harnesses.

The three completed benchmark campaigns are:

- Hausdorff Distance
- RayJoin-style spatial workloads
- RTNN-inspired nearest-neighbor search

Together, they show what serious RTDL users need from the language/runtime.

## Summary Table

| benchmark app | pressure on RTDL | generic RTDL/runtime additions |
| --- | --- | --- |
| Hausdorff Distance | exact distance, pruning, max reduction, witness-like nearest candidates | point/group distance workflows, max-distance nearest-candidate framing, scale-aware Python+partner orchestration, stricter exact-vs-threshold claim boundaries |
| RayJoin | spatial join, membership, first-hit, compact positives, row streams | prepared segment-pair paths, prepared closed-shape membership, bounded point probes, generic first-hit rows, raw row views, compact positive output, phase-separated timing |
| RTNN | 3-D nearest-neighbor search, prepared structures, batching, top-K summaries, dense clustered data | prepared 3-D fixed-radius neighbor handles, packed column input, device-side count/summary/ranked-summary continuations, batched query runners, CuPy grid baseline, density-aware runtime target |

## Hausdorff Distance

Hausdorff Distance forced RTDL to separate exact user intent from acceleration
subpaths. The app can use RTDL to generate or prune candidate relationships,
but exact Hausdorff still needs a disciplined reduction path over distances.

Design insights:

- Exactness must be explicit. A threshold/probe path is not automatically an
  exact Hausdorff function.
- Point groups and nearest-candidate rows are generic enough to belong in RTDL.
- The useful reduction is often a max over per-point nearest distances, so
  summary/reduction contracts matter as much as witness rows.
- Scale-aware app code is legitimate in Python/partner layers, but native ABI
  names must stay generic.

What RTDL gained:

- A stronger point/group distance programming pattern.
- Clearer max-distance nearest-candidate vocabulary.
- Better public boundaries around exact HD, threshold search, and X-HD-inspired
  optimization claims.

## RayJoin

RayJoin forced RTDL to face spatial-join workloads where the expensive part is
not merely detecting one hit. The workload needs membership, first boundary
hits, compact positive rows, and controlled row materialization.

Design insights:

- Prepared geometry is first-class: build once, query many times.
- Generic closed-shape membership is safer than app-shaped PIP or county logic.
- First-hit / nearest-boundary rows are generic primitives, not RayJoin-specific
  shortcuts.
- Returning millions of witness rows is often the wrong contract when the user
  only needs count, parity, membership, or positive ids.
- Phase-separated timing is essential: prepared query time, Python call time,
  and whole-app time are different claims.

What RTDL gained:

- Prepared segment-pair execution patterns.
- Prepared closed-shape membership.
- Bounded point probes.
- Generic first-hit / nearest-boundary rows.
- Raw row views and compact positive outputs.
- A sharper device-resident continuation roadmap for grouped counts, parity,
  and compact streams.

## RTNN

RTNN forced RTDL to deal with 3-D nearest-neighbor search as a serious systems
benchmark. It exposed the difference between a generic prepared RTDL path and a
specialized spatial-index implementation.

Design insights:

- Packed/prepared column input must be first-class for serious performance.
- Prepared search-side structures matter more than one-shot traversal.
- Device-side summaries are often the right output contract.
- A weak all-pairs CUDA baseline is not enough; RTDL must be compared against
  stronger spatial-index CUDA baselines.
- Dense clustered distributions need density-aware scheduling or a partner-grid
  backend. Python-level partitioning over many prepared handles was measured
  and rejected as an optimization.

What RTDL gained:

- Prepared 3-D fixed-radius neighbor handles.
- Batched query runners.
- Device-side count, distance summary, exact rows, ranked rows, and
  ranked-summary continuations.
- CuPy RawKernel grid baseline for a stronger CUDA-core comparison.
- A precise next primitive target: generic density-aware fixed-radius runtime
  scheduling or a first-class CUDA-grid partner backend.

## Cross-App Runtime Pattern

The three apps converge on the same runtime design:

1. Prepared structures should be central.
2. Output contracts must be explicit: witness rows, compact positives, counts,
   summaries, first hits, ranked summaries, and grouped reductions are different
   primitives.
3. Partner code is not a side detail. CuPy/PyTorch-style partners are how users
   continue work on GPU-resident or reduced data without forcing app semantics
   into the RTDL engine.
4. Benchmark apps should pressure generic primitives, not introduce app-shaped
   native ABI.
5. Negative results are useful. RayJoin and RTNN both showed cases where a
   plausible high-level policy was not the right runtime primitive.

## What Was Not Added

RTDL did not add:

- a Hausdorff-specific native engine;
- a RayJoin-specific native engine;
- an RTNN-specific native engine;
- app-specific native ABI names;
- a broad claim that RT cores accelerate every part of every app;
- a full reproduction claim for X-HD, RayJoin, or RTNN.

That restraint is part of the design. The benchmark apps teach the language
what generic contracts it needs.

## Current Generic Primitive Direction

The strongest v2.x direction is:

- prepared scenes and prepared point sets;
- packed column input;
- bounded witness rows;
- raw row views;
- compact positive rows;
- first-hit / nearest-hit rows;
- device-side grouped reductions;
- exact count and distance summaries;
- ranked neighbor rows and ranked summaries;
- density-aware fixed-radius scheduling;
- explicit partner backend selection and claim boundaries.

## Release/Claim Boundary

This document is a design synthesis. It is not a release authorization and does
not override individual benchmark reports or external reviews.

Any public performance claim still needs the measured scope, exact contract,
hardware context, and required AI consensus for that claim.
